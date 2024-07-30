from flask import jsonify, request

from middlewares import auth
from services import freight
from utils import secret
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

    cred = secret.get_credentials()

    if not refresh_token_value:
        return jsonify({"message": "Refresh token is required"}), 400

    client_id = cred['client_id']
    client_secret = cred['client_secret']
    aws_region = cred['aws_region']
    username = cred['username']
    new_tokens = auth.refresh_tokens(client_id, client_secret, refresh_token_value, username, aws_region)

    if new_tokens:
        return jsonify(new_tokens), 200
    else:
        return jsonify({"message": "Invalid refresh token"}), 401
