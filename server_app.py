from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/search", methods=["POST"])
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

@app.route("/regi", methods=["POST"])
def regi():
    _regi_name = request.data.get("name", None)
    _regi_desc = request.data.get("desc", None)
    _regi_image = request.files.get("image", None)
    
    if _regi_name == None or _regi_image == None or _regi_desc == None:
        return jsonify({"error": "Required parameters are missing"}), 400

    return jsonify({"result": "success"}), 200
    
if __name__ == "__main__":
    app.run(host="localhost", port=80, debug=True)