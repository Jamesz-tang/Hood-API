import os

from flask import jsonify, request
from middlewares import auth
from services import freight
from . import api_blueprint


@api_blueprint.route('/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello, World!"})


@api_blueprint.route('/freight/pack', methods=['POST'])
@auth.auth
def pack():
    items = request.get_json()
    pallets = freight.pack(items)
    return jsonify({'status_code': 0, 'message': 'succeeded', 'data': pallets})


# Refresh token endpoint
@api_blueprint.route('/refresh', methods=['POST'])
def refresh_token_endpoint():
    data = request.get_json()
    refresh_token_value = data.get('refresh_token')

    if not refresh_token_value:
        return jsonify({"message": "Refresh token is required"}), 400

    USER_POOL_ID = os.environ.get('USER_POOL_ID')
    APP_CLIENT_ID = os.environ.get('APP_CLIENT_ID')
    APP_CLIENT_SECRET = os.environ.get('APP_CLIENT_SECRET')  # Client secret if applicable
    REGION = os.environ.get('REGION', 'us-east-1')
    USERNAME = os.environ.get('USERNAME')
    new_tokens = auth.refresh_tokens(APP_CLIENT_ID, APP_CLIENT_SECRET, refresh_token_value, USERNAME, REGION)
    # new_tokens = auth.refresh_token(refresh_token_value)

    if new_tokens:
        return jsonify(new_tokens), 200
    else:
        return jsonify({"message": "Invalid refresh token"}), 401
