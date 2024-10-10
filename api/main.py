import logging
from flask import Blueprint, render_template, jsonify, request
from base64 import b64encode, b64decode
import json
from src import utils
import os

LOG_PATH = os.path.join(os.getcwd(), "log")
DB_PATH = os.path.join(os.getcwd(), "db")
TEMP_PATH = os.path.join(DB_PATH, "temp_dir")
DB_FACE_PATH = os.path.join(DB_PATH, "faces")
INFO_DB_PATH = os.path.join(DB_PATH, "info.json")
AUTH_DB_PATH = os.path.join(DB_PATH, "auth.json")

detection_model_path = "/home/azureuser/server/src/models/face-detection-adas-0001"
reid_model_path = "/home/azureuser/server/src/models/face-reidentification-retail-0095"

api = Blueprint('api', __name__, url_prefix='/api')
FaceRecodation = utils.FaceRecognition(detection_model_path, reid_model_path)

logging.basicConfig(filename=os.path.join(LOG_PATH, 'access.log'), level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s', encoding='utf-8')

if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH)

if not os.path.exists(DB_PATH):
    os.makedirs(DB_PATH)
    
if not os.path.exists(INFO_DB_PATH):
    with open(INFO_DB_PATH, "w") as info_db:
        info_db.write(json.dumps([]))
if not os.path.exists(AUTH_DB_PATH):
    with open(AUTH_DB_PATH, "w") as auth_db:
        auth_db.write(json.dumps([]))

if not os.path.exists(DB_FACE_PATH):
    os.makedirs(DB_FACE_PATH)

if not os.path.exists(TEMP_PATH):
    os.makedirs(TEMP_PATH)

def client_ip() -> str:
    return request.remote_addr

def veri_key(auth_key):
    with open(AUTH_DB_PATH, "r") as f:
        db = json.load(f)
        
    for db_item in db:
        if db_item["authKey"] == auth_key:
            logging.info(f"veri_auth: {client_ip()} Success. name<{db_item['userName']}> level<{db_item['userLevel']}> use_key<{db_item['authKey']}>")
            return (db_item["userName"], db_item['userLevel'], db_item["authKey"])
    
    logging.info(f"veri_auth: {client_ip()} Fail. use_key<{auth_key}>")
    return False

@api.route("/", methods=["GET"])
def api_home():
    return render_template("/api/docs.html")

@api.route("/list", methods=["GET"])
def crimi_list():
    response = {
        "error": False,
        "detail": "",
    }
    
    _res_key = request.form.get("authKey", None)
    is_auth = veri_key(_res_key)
    
    try:
        with open(os.path.join("db", "info.json"), "r") as f:
            db = json.load(f)
        
        send_db_info = []
        for db_item in db:
            send_db_info.append({
                "crimi_name": db_item["crimi_name"],
                "crimi_desc": db_item["crimi_desc"],
                "regi_time": db_item["regi_time"],
                "regi_user_name": db_item["regi_user_name"]
            })
            
            if is_auth != False:
                if is_auth[1] == 0:
                    send_db_info[-1]["crimi_face"] = []
                    for face in db_item["crimi_face"]:
                        with open(os.path.join("db", "faces", face), "rb") as f:
                            send_db_info[-1]["crimi_face"].append(b64encode(f.read()).decode())
        
    except Exception as e:
        logging.error(f"Error: {e}")
        response.update({"error": True})
        response.update({"detail": "An unknown error has occurred. Please try again later."})
        return jsonify(response), 500
    
    response.update({"error": False})
    if is_auth != False:
        response.update({"detail": "Load successful"})
    else:
        response.update({"detail": "Load successful (Face data is not included)"})
    response.update({"data": send_db_info})
    
    return jsonify(response), 200

@api.route("/search", methods=["POST"])
def crimi_search():
    SIMILAR_LEVEL = 0.7
    SUSPECT_LEVEL = 0.5
    image_ext = ["jpg", "jpeg", "png"]
    response = {
        "error": False,
        "detail": "",
    }
    
    _res_key = request.form.get("authKey", None)
    is_auth = veri_key(_res_key)
    _res_face = request.files.get("crimi_face", None)
    
    # 필수 파라미터 확인
    if _res_face == None:
        response.update({"error": True})
        response.update({"detail": "Required parameters are missing"})
        return jsonify(response), 400
    
    # 이미지 파일 아닐 경우 반려
    if utils.get_file_ext(_res_face.filename) not in image_ext:
        response.update({"error": True})
        response.update({"detail": f"Only image files are allowed: {', '.join(image_ext)}"})
        return jsonify(response), 400
    
    # 얼굴 있냐 확인
    try:
        _res_face.save(os.path.join(TEMP_PATH, "temp_search_input_face.jpg"))
        if FaceRecodation.is_face(os.path.join(TEMP_PATH, "temp_search_input_face.jpg")) == False:
            response.update({"error": True})
            response.update({"detail": "Upload only images that include the face."})
            os.remove(os.path.join(TEMP_PATH, "temp_search_input_face.jpg"))
            return jsonify(response), 400
    except Exception as e:
        logging.error(f"Error: {e}")
        response.update({"error": True})
        response.update({"detail": "An unknown error has occurred. Please try again later."})
        return jsonify(response), 500
    
    similar_info = []
    suspect_info = []
    
    with open(INFO_DB_PATH, "r") as f:
        db = json.load(f)
    
    for db_item in db:
        is_similar = False
        is_suspect = False
        
        for face in db_item["crimi_face"]:
            base_face_path = os.path.join("db", "faces", face)
            with open(base_face_path, "rb") as base_face:
                base_face_data = base_face.read()
            
            similarity_score = FaceRecodation.compare_faces(os.path.join(TEMP_PATH, "temp_search_input_face.jpg"), base_face_path)
            
            if similarity_score > SIMILAR_LEVEL:
                is_similar = True
                break
            elif similarity_score > SUSPECT_LEVEL:
                is_suspect = True
        
        if is_suspect == True:
            suspect_info.append({
                "crimi_name": db_item["crimi_name"],
                "crimi_desc": db_item["crimi_desc"],
                "regi_user": db_item.get("regi_user", "Unknown")
            })
            if is_auth != False:
                if is_auth[1] == 0:
                    suspect_info[-1]["crimi_face"] = b64encode(base_face_data).decode
            
            continue
        
        elif is_similar == True:
            similar_info.append({
                "crimi_name": db_item["crimi_name"],
                "crimi_desc": db_item["crimi_desc"],
                "regi_user": db_item.get("regi_user", "Unknown")
            })
            if is_auth != False:
                if is_auth[1] == 0:
                    similar_info[-1]["crimi_face"] = b64encode(base_face_data).decode()
            
    
    if os.path.exists(os.path.join(TEMP_PATH, "temp_search_input_face.jpg")):
        os.remove(os.path.join(TEMP_PATH, "temp_search_input_face.jpg"))
    
    response.update({"error": False})
    if is_auth != False:
        response.update({"detail": "Search successful"})
    else:
        response.update({"detail": "Search successful (Face data is not included)"})
    response.update({"similar_info": similar_info})
    response.update({"suspect_info": suspect_info})
    
    return jsonify(response), 200

@api.route("/regi", methods=["POST"])
def crimi_regi():
    image_ext = ["jpg", "jpeg", "png"]
    response = {
        "error": False,
        "detail": "",
    }
    
    _res_key = request.form.get('authKey', None)
    is_auth = veri_key(_res_key)
    _res_regi_name = request.form.get('crimi_name', None)
    _res_regi_desc = request.form.get('crimi_desc', None)
    _res_regi_face = request.files.get("crimi_face", None)
    _res_regi_agree = request.form.get('is_agree', False)
    _res_regi_time = request.form.get('regi_time', None)
    
    # 필수 파라미터 확인
    if _res_regi_name == None or _res_regi_face == None or _res_regi_desc == None:
        response.update({"error": True})
        response.update({"detail": "Required parameters are missing"})
        return response, 400
    
    # 인증 실패 시 반려
    if is_auth == False:
        response.update({"error": True})
        response.update({"detail": "You do not have permission to register."})
        return jsonify(response), 403
    
    # 이미지 파일 아닐 경우 반려
    if utils.get_file_ext(_res_regi_face.filename) not in image_ext:
        response.update({"error": True})
        response.update({"detail": f"Only image files are allowed: {', '.join(image_ext)}"})
        return jsonify(response), 400
    
    # 약관 확인
    if _res_regi_agree == False:
        response.update({"error": True})
        response.update({"detail": "You must agree to the terms and conditions."})
        return jsonify(response), 400
    
    # 얼굴 있냐 확인
    _res_regi_face.save(os.path.join(TEMP_PATH, "temp_regi_input_face.jpg"))
    if FaceRecodation.is_face(os.path.join(TEMP_PATH, "temp_regi_input_face.jpg")) == False:
        response.update({"error": True})
        response.update({"detail": "Upload only images that include the face."})
        return jsonify(response), 400
    
    # 등록
    try:
        with open(INFO_DB_PATH, "r") as f:
            db = json.load(f)
        
        ## 얼굴 저장
        gen_rhash = utils.gen_rhash()
        save_file_name = f"{gen_rhash}.jpg"
        while os.path.exists(os.path.join("db", "faces", save_file_name)):
            gen_rhash = utils.gen_rhash()
            save_file_name = f"{gen_rhash}.jpg"
        os.rename(os.path.join(TEMP_PATH, "temp_regi_input_face.jpg"), os.path.join("db", "faces", save_file_name))
        
        ## 정보 저장
        ### 중복이냐?
        for db_item in db:
            if db_item["crimi_name"] == _res_regi_name:
                if is_auth == False:
                    response.update({"error": True})
                    response.update({"detail": "You do not have permission to add photos."})
                    return jsonify(response), 403
                else:
                    if is_auth[1] == 0:
                        old_crimi_data = db_item
                        db.remove(db_item)
                        
                        old_crimi_data["crimi_face"].append(save_file_name)
                        db.append(old_crimi_data)
                        
                        with open(INFO_DB_PATH, "w") as f:
                            json.dump(db, f)
                        
                        response.update({"error": False})
                        response.update({"detail": "Added a photo to the previously registered information."})
                        return jsonify(response), 200
                    
                    else:
                        response.update({"error": True})
                        response.update({"detail": "You do not have permission to add photos."})
                        return jsonify(response), 403
        
        ### 중복 아님
        crimi_data = {
            "crimi_name": _res_regi_name,
            "crimi_desc": _res_regi_desc,
            "regi_time": _res_regi_time,
            "crimi_face": [save_file_name],
            "regi_user_ip": client_ip(),
            "regi_user_name": f"{is_auth[0]}"
        }
        
        db.append(crimi_data)
        with open(INFO_DB_PATH, "w") as f:
            json.dump(db, f, indent=4)
        
        logging.info(f"{crimi_data['regi_user']} registered {crimi_data['crimi_name']}")
        
        response.update({"error": False})
        response.update({"detail": "Registration successful"})
        return jsonify(response), 200        
            
    except Exception as e:
        print(f"Error: {e}")
        response.update({"error": True})
        response.update({"detail": "An unknown error has occurred. Please try again later."})
        return jsonify(response), 500

@api.route("/del", methods=["POST"])
def crimi_del():
    response = {
        "error": False,
        "detail": "",
    }
    
    _res_key = request.form.get("authKey", None)
    is_auth = veri_key(_res_key)
    _res_del_name = request.form.get("crimi_name", None)
    
    if is_auth == False:
        response.update({"error": True})
        response.update({"detail": "You do not have permission to edit this data."})
        return jsonify(response), 403
    else:
        if is_auth[1] != 0:
            response.update({"error": True})
            response.update({"detail": "You do not have permission to edit this data."})
            return jsonify(response), 403
    
    # 필수 파라미터 확인
    if _res_del_name == None:
        response.update({"error": True})
        response.update({"detail": "Required parameters are missing"})
        return jsonify(response), 400

    # 정보 삭제
    try:
        with open(INFO_DB_PATH, "r") as f:
            db = json.load(f)
        
        for db_item in db:
            if db_item["crimi_name"] == _res_del_name:
                for face in db_item["crimi_face"]:
                    os.remove(os.path.join("db", "faces", face))
                db.remove(db_item)
                
                with open(INFO_DB_PATH, "w") as f:
                    json.dump(db, f)
                
                logging.info(f"{is_auth[0]} deleted {db_item['crimi_name']}")
                
                response.update({"error": False})
                response.update({"detail": "Deletion successful"})
                return jsonify(response), 200
        
        response.update({"error": True})
        response.update({"detail": "There is no data to delete."})
        return jsonify(response), 404
    except Exception as e:
        response.update({"error": True})
        response.update({"detail": "An unknown error has occurred. Please try again later."})
        return jsonify(response), 500