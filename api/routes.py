from flask import jsonify, request

from services import freight
from . import api_blueprint


@api_blueprint.route('/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello, World!"})


@api_blueprint.route('/items', methods=['GET'])
def get_items():
    # Replace with actual logic
    items = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]
    return jsonify(items)


@api_blueprint.route('/freight/pack', methods=['POST'])
def pack():
    data = request.get_json()
    pallets = freight.pack(data)
    return jsonify({'status_code': 0, 'message': 'succeeded', 'data': pallets})
