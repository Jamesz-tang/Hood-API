import os
from flask import Flask, request, jsonify
from api.routes import api_blueprint
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.register_blueprint(api_blueprint, url_prefix='/api')


@app.errorhandler(404)
# inbuilt function which takes error as parameter
def not_found(e):
    # defining function
    return 'Page Not Found'


@app.errorhandler(400)
# inbuilt function which takes error as parameter
def not_found(e):
    # defining function
    return 'Bad Request'


@app.route('/', methods=['GET'])
def ok():
    app_name = os.getenv('APP_NAME')
    app.logger.info('%s hit', app_name)

    return 'Welcome to ' + app_name


@app.route('/health', methods=['GET'])
def get_health():
    return 'healthy'


if __name__ == '__main__':
    app.run(debug=True, port=8080, host='0.0.0.0')
