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

    new_tokens = auth.refresh_token(refresh_token_value)

    if new_tokens:
        return jsonify(new_tokens), 200
    else:
        return jsonify({"message": "Invalid refresh token"}), 401
