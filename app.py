import os
from flask import Flask, render_template, jsonify
from dotenv import load_dotenv
from api.main import api
load_dotenv()

SERVER_HOST = os.getenv("SERVER_HOST")
SERVER_PORT = os.getenv("SERVER_PORT")

app = Flask(__name__)
app.register_blueprint(api)

@app.route('/', methods=['GET'])
def home():
    return render_template('api/docs.html')

@app.errorhandler(Exception)
def handle_exception(e):
    response = {
        "error": True,
        "detail": "An unexpected error occurred.",
    }
    
    code = -1
    
    if hasattr(e, 'code'):
        code = e.code
    message = str(e)
    
    response.update({'error_code': code})
    response.update({"detail": message})
    
    return jsonify(response), code

if __name__ == '__main__':
	app.run(host=SERVER_HOST, port=SERVER_PORT, debug=True)