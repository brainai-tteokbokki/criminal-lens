import os
from flask import Flask, render_template, jsonify, send_file
from dotenv import load_dotenv
from api.main import api
load_dotenv()

SERVER_HOST = os.getenv("SERVER_HOST")
SERVER_PORT = os.getenv("SERVER_PORT")

app = Flask(__name__)
app.register_blueprint(api)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/robots.txt', methods=['GET'])
def robotstxt():
    return send_file('static/robots.txt')

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
    
    if code == 404:
        response.update({"detail": "This is not a valid endpoint."})
    
    print(f"Error: {message}")
    
    return jsonify(response), code

if __name__ == '__main__':
	app.run(host=SERVER_HOST, port=SERVER_PORT, debug=True)