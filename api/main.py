from flask import Blueprint, redirect, jsonify, request
from base64 import b64encode, b64decode
from src import utils

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/', methods=['GET'])
def api_home():
    response = {
        "error": True,
        "detail": "This is not a valid endpoint.",
    }
    return jsonify(response), 404

@api.route("/search", methods=["POST"])
def search():
    response = {
        "error": False,
        "detail": "",
    }
    
    _res_image = request.files.get("image", None)
    if _res_image == None:
        response.update({"error": True})
        response.update({"detail": "Required parameters are missing"})
        return jsonify(response), 400
    
    response.update({"detail": "Search successful"})
    
    return jsonify(response), 200

@api.route("/regi", methods=["POST"])
def regi():
    _regi_name = request.data.get("name", None)
    _regi_desc = request.data.get("desc", None)
    _regi_image = request.files.get("image", None)
    if _regi_name == None or _regi_image == None or _regi_desc == None:
        return jsonify({"error": "Required parameters are missing"}), 400

    return jsonify({"result": "success"}), 200
