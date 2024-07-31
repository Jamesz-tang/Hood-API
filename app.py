import logging
import os
from flask import Flask, request, jsonify
from api.routes import api_blueprint
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.register_blueprint(api_blueprint, url_prefix='/api')


def setup_logging():
    log_level_str = str.upper(os.getenv('LOG_LEVEL', 'INFO'))
    log_level = logging.INFO

    if log_level_str == 'DEBUG':
        log_level = logging.DEBUG
    elif log_level_str == 'INFO':
        log_level = logging.INFO
    elif log_level_str == 'WARNING':
        log_level = logging.WARNING
    elif log_level_str == 'ERROR':
        log_level = logging.ERROR

    # Set up logging
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')


setup_logging()
logger = logging.getLogger(__name__)


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
    logger.info('%s hit', app_name)

    return 'Welcome to ' + app_name


@app.route('/health', methods=['GET'])
def get_health():
    return 'healthy'


if __name__ == '__main__':
    logger.info('Starting server ...')
    app.run(debug=True, port=8080, host='0.0.0.0')
