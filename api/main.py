import time
from flask import Blueprint, redirect, jsonify, request
from base64 import b64encode, b64decode
import json
from src import utils
import os

TEMP_DIR = os.path.join("db", "temp_dir")
DB_PATH = os.path.join("db", "info.json")

api = Blueprint('api', __name__, url_prefix='/api')

detection_model_path = "/home/azureuser/server/src/models/face-detection-adas-0001"
reid_model_path = "/home/azureuser/server/src/models/face-reidentification-retail-0095"
FaceRecodation = utils.FaceRecognition(detection_model_path, reid_model_path)

@api.route("/list", methods=["GET"])
def crimi_list():
    response = {
        "error": False,
        "detail": "",
    }
    
    try:
        with open(os.path.join("db", "info.json"), "r") as f:
            db = json.load(f)
        
        send_db_info = []
        for db_item in db:
            send_db_info.append({
                "crimi_name": db_item["crimi_name"],
                "crimi_desc": db_item["crimi_desc"],
                "regi_time": db_item["regi_time"],
                "crimi_face": []
            })
            for face in db_item["crimi_face"]:
                with open(os.path.join("db", "faces", face), "rb") as f:
                    send_db_info[-1]["crimi_face"].append(b64encode(f.read()).decode())
        
    except Exception as e:
        response.update({"error": True})
        response.update({"detail": "An unknown error has occurred. Please try again later."})
        return jsonify(response), 500
    
    response.update({"error": False})
    response.update({"detail": "Load successful"})
    response.update({"data": send_db_info})
    
    return jsonify(response), 200

@api.route("/search", methods=["POST"])
def search():
    SIMILAR_LEVEL = 0.7
    SUSPECT_LEVEL = 0.5
    response = {
        "error": False,
        "detail": "",
    }
    
    _res_image = request.files.get("image", None)
    # 필수 파라미터 확인
    if _res_image == None:
        response.update({"error": True})
        response.update({"detail": "Required parameters are missing"})
        return jsonify(response), 400
    
    # 얼굴 있냐 확인
    _res_image.save(os.path.join(TEMP_DIR, "temp_search_input_face.jpg"))
    if FaceRecodation.is_face(os.path.join(TEMP_DIR, "temp_search_input_face.jpg")) == False:
        response.update({"error": True})
        response.update({"detail": "Upload only images that include the face."})
        os.remove(os.path.join(TEMP_DIR, "temp_search_input_face.jpg"))
        
        return jsonify(response), 400
    
    similar_info = []
    suspect_info = []
    
    with open(DB_PATH, "r") as f:
        db = json.load(f)
    
    for db_item in db:
        for face in db_item["crimi_face"]:
            base_face_path = os.path.join("db", "faces", face)
            with open(base_face_path, "rb") as base_face:
                base_face_data = base_face.read()
            
            similarity_score = FaceRecodation.compare_faces(os.path.join(TEMP_DIR, "temp_search_input_face.jpg"), base_face_path)
            print(similarity_score)
            if similarity_score > SIMILAR_LEVEL:
                similar_info.append({
                    "crimi_name": db_item["crimi_name"],
                    "crimi_desc": db_item["crimi_desc"],
                    "crimi_face": b64encode(base_face_data).decode()
                })
                break
            elif similarity_score > SUSPECT_LEVEL:
                suspect_info.append({
                    "crimi_name": db_item["crimi_name"],
                    "crimi_desc": db_item["crimi_desc"],
                    "crimi_face": b64encode(base_face_data).decode()
                })
                break
    
    response.update({"error": False})
    response.update({"detail": "Search successful"})
    response.update({"similar_info": similar_info})
    response.update({"suspect_info": suspect_info})
    
    return jsonify(response), 200

@api.route("/regi", methods=["POST"])
def regi():
    response = {
        "error": False,
        "detail": "",
    }
    
    _regi_name = request.form.get('crimi_name', None)
    _regi_desc = request.form.get('crimi_desc', None)
    _regi_image = request.files.get("crimi_image", None)
    _regi_agree = request.form.get('is_agree', False)
    _regi_time = request.form.get('regi_time', None)
    
    # 약관 확인
    if _regi_agree == False:
        response.update({"error": True})
        response.update({"detail": "You must agree to the terms and conditions."})
        return jsonify(response), 400    
    
    # 필수 파라미터 확인
    if _regi_name == None or _regi_image == None or _regi_desc == None:
        response.update({"error": True})
        response.update({"detail": "Required parameters are missing"})
        return response, 400
    
    # 얼굴 있냐 확인
    _regi_image.save(os.path.join(TEMP_DIR, "temp_regi_input_face.jpg"))
    if FaceRecodation.is_face(os.path.join(TEMP_DIR, "temp_regi_input_face.jpg")) == False:
        response.update({"error": True})
        response.update({"detail": "Upload only images that include the face."})
        return jsonify(response), 400
    
    # 등록
    try:
        with open(DB_PATH, "r") as f:
            db = json.load(f)
        
        # 등록
        ## 얼굴 저장
        gen_rhash = utils.gen_rhash()
        save_file_name = f"{gen_rhash}.jpg"
        while os.path.exists(os.path.join("db", "faces", save_file_name)):
            gen_rhash = utils.gen_rhash()
            save_file_name = f"{gen_rhash}.jpg"
        os.rename(os.path.join(TEMP_DIR, "temp_regi_input_face.jpg"), os.path.join("db", "faces", save_file_name))
        
        ## 정보 저장
        ### 중복이냐?
        for db_item in db:
            if db_item["crimi_name"] == _regi_name:
                old_crimi_data = db_item
                db.remove(db_item)
                
                old_crimi_data["crimi_face"].append(save_file_name)
                db.append(old_crimi_data)
                
                with open(DB_PATH, "w") as f:
                    json.dump(db, f)
                
                response.update({"error": False})
                response.update({"detail": "Added a photo to the previously registered information."})
                return jsonify(response), 200
        
        ### 중복 아님
        crimi_data = {
            "crimi_name": _regi_name,
            "crimi_desc": _regi_desc,
            "regi_time": _regi_time,
            "crimi_face": [save_file_name]
        }
        db.append(crimi_data)
        
        with open(DB_PATH, "w") as f:
            json.dump(db, f)
            
        response.update({"error": False})
        response.update({"detail": "Registration successful"})
        return jsonify(response), 200        
            
    except Exception as e:
        print(e)
        response.update({"error": True})
        response.update({"detail": "An unknown error has occurred. Please try again later."})
        return jsonify(response), 500