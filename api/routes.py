from flask import jsonify, request
from . import api_blueprint

@api_blueprint.route('/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello, World!"})

@api_blueprint.route('/items', methods=['GET'])
def get_items():
    # Replace with actual logic
    items = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]
    return jsonify(items)
