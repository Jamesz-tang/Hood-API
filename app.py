from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Sample data to simulate a database
items = [
    {"id": 1, "name": "Item 1", "weight": 10, "dimensions": {"length": 2, "width": 2, "height": 2}},
    {"id": 2, "name": "Item 2", "weight": 20, "dimensions": {"length": 3, "width": 3, "height": 3}},
]

pallets = [
    {"id": 1, "length": 120, "width": 100, "max_height": 150},
    {"id": 2, "length": 120, "width": 100, "max_height": 200},
]


@app.route('/', methods=['GET'])
def ok():
    return 'OK'


@app.route('/health', methods=['GET'])
def get_health():
    return 'healthy'

@app.route('/test', methods=['GET'])
def get_health():
    return 'test'

@app.route('/api/optimal_bin_packages', methods=['POST'])
def optimal_bin_packages():
    data = request.json
    # Add your optimization logic here
    return jsonify({"message": "Optimization logic to be implemented"})

if __name__ == '__main__':
    app.run(debug=True)


@app.route('/items', methods=['GET'])
def get_items():
    return jsonify(items)


@app.route('/items', methods=['POST'])
def add_item():
    new_item = request.json
    new_item['id'] = len(items) + 1
    items.append(new_item)
    return jsonify(new_item), 201


@app.route('/pallets', methods=['GET'])
def get_pallets():
    return jsonify(pallets)


@app.route('/pallets', methods=['POST'])
def add_pallet():
    new_pallet = request.json
    new_pallet['id'] = len(pallets) + 1
    pallets.append(new_pallet)
    return jsonify(new_pallet), 201


@app.route('/optimal-bin-packages', methods=['POST'])
def create_optimal_bin_packages():
    data = request.json
    # Assuming data contains 'items' and 'pallets'
    items_to_pack = data['items']
    pallets_to_use = data['pallets']

    # Here you would call your optimization logic, for example using Google OR-Tools
    optimal_packages = []  # Placeholder for the optimized packaging result

    return jsonify(optimal_packages)


if __name__ == '__main__':
    app.run(debug=True)
