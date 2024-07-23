from packing_system import PackingSystem

# Define items and pallets data
items_data = [
    {'weight': 12, 'length': 2, 'width': 2, 'height': 1, 'assembled': False, 'bundled': False},
    {'weight': 10, 'length': 2, 'width': 2, 'height': 1, 'assembled': False, 'bundled': False},
    {'weight': 5, 'length': 1, 'width': 1, 'height': 1, 'assembled': False, 'bundled': False},
    {'weight': 8, 'length': 1, 'width': 1, 'height': 1, 'assembled': False, 'bundled': False},
    {'weight': 18, 'length': 2, 'width': 2, 'height': 2, 'assembled': True, 'bundled': False},
    {'weight': 40, 'length': 5, 'width': 5, 'height': 3, 'assembled': True, 'bundled': False},
    {'weight': 20, 'length': 2, 'width': 2, 'height': 2, 'assembled': True, 'bundled': False},
    {'weight': 30, 'length': 4, 'width': 4, 'height': 2, 'assembled': True, 'bundled': False},
    {'weight': 15, 'length': 3, 'width': 3, 'height': 1, 'assembled': False, 'bundled': True},
    {'weight': 25, 'length': 3, 'width': 3, 'height': 2, 'assembled': False, 'bundled': True},
]

pallets_data = [
    {'type': 'BUNDLE', 'length': 10, 'width': 10, 'max_height': 5, 'weight': 50, 'assembled': False},
    {'type': 'BUNDLE', 'length': 10, 'width': 10, 'max_height': 5, 'weight': 50, 'assembled': False},
    {'type': 'PLT4', 'length': 4, 'width': 4, 'max_height': 5, 'weight': 30, 'assembled': True},
    {'type': 'PLT6', 'length': 6, 'width': 6, 'max_height': 5, 'weight': 35, 'assembled': True},
    {'type': 'PLT8', 'length': 8, 'width': 8, 'max_height': 5, 'weight': 40, 'assembled': True},
    {'type': 'PLT4', 'length': 4, 'width': 4, 'max_height': 5, 'weight': 30, 'assembled': False},
    {'type': 'PLT6', 'length': 6, 'width': 6, 'max_height': 5, 'weight': 35, 'assembled': False},
    {'type': 'PLT8', 'length': 8, 'width': 8, 'max_height': 5, 'weight': 40, 'assembled': False},
]

# Create a packing system and solve the problem
packing_system = PackingSystem(items_data, pallets_data)
result = packing_system.solve_packing()

print(result)
