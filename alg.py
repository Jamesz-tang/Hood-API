# Create optimized pallets or parcels for the list of items to pack for shipping quotes using google or tools SCIP algorithm. Each item has the following attributes.
# - weight
# - length
# - width
# - height
# - assembled (boolean)
# - bundled (boolean)
#
#
# Each pallet has the following a maximum height, fixed length, fixed width, weight,  a type of BUNDLE, PLT4, PLT6 and PLT8 and assembled (boolean).
#
# Create the minimum number of pallets using linear solution using google or tools,
#
# Consider the following Constraints
# 1. Assembled pallet can only hold assembled items only.
# 2, Bundle type pallet can hold bundled items only.
# 3. Smaller pallets are preferred but not required.
# 4. No constraints on the weight of a pallet.
#
# The output must include the total number of pallets used, and total weight. Each pallet must include
# - actual height, and total weight including the pallet weight of each pallet
# - the details of the items ii the pallet
# - the pallet type, height, width, length and weight of the pallet
#


from ortools.linear_solver import pywraplp

# Define items and pallets using lists
items = [
    {'id': 'item9', 'weight': 12, 'length': 2, 'width': 2, 'height': 1, 'assembled': False, 'bundled': False},
    {'id': 'item1', 'weight': 10, 'length': 2, 'width': 2, 'height': 1, 'assembled': False, 'bundled': False},
    {'id': 'item4', 'weight': 5, 'length': 1, 'width': 1, 'height': 1, 'assembled': False, 'bundled': False},
    {'id': 'item6', 'weight': 8, 'length': 1, 'width': 1, 'height': 1, 'assembled': False, 'bundled': False},

    {'id': 'item7', 'weight': 18, 'length': 2, 'width': 2, 'height': 2, 'assembled': True, 'bundled': False},
    {'id': 'item10', 'weight': 40, 'length': 5, 'width': 5, 'height': 3, 'assembled': True, 'bundled': False},
    {'id': 'item2', 'weight': 20, 'length': 2, 'width': 2, 'height': 2, 'assembled': True, 'bundled': False},
    {'id': 'item5', 'weight': 30, 'length': 4, 'width': 4, 'height': 2, 'assembled': True, 'bundled': False},

    {'id': 'item3', 'weight': 15, 'length': 3, 'width': 3, 'height': 1, 'assembled': False, 'bundled': True},
    {'id': 'item8', 'weight': 25, 'length': 3, 'width': 3, 'height': 2, 'assembled': False, 'bundled': True},

]

pallets = [
    {'id': 'bundle', 'type': 'BUNDLE', 'length': 10, 'width': 10, 'max_height': 5, 'weight': 50, 'assembled': False},
    {'id': 'bundle', 'type': 'BUNDLE', 'length': 10, 'width': 10, 'max_height': 5, 'weight': 50, 'assembled': False},

    {'id': 'plt4', 'type': 'PLT4', 'length': 4, 'width': 4, 'max_height': 5, 'weight': 30, 'assembled': True},
    {'id': 'plt6', 'type': 'PLT6', 'length': 6, 'width': 6, 'max_height': 5, 'weight': 35, 'assembled': True},
    {'id': 'plt8', 'type': 'PLT8', 'length': 8, 'width': 8, 'max_height': 5, 'weight': 40, 'assembled': True},

    {'id': 'plt4', 'type': 'PLT4', 'length': 4, 'width': 4, 'max_height': 5, 'weight': 30, 'assembled': False},
    {'id': 'plt6', 'type': 'PLT6', 'length': 6, 'width': 6, 'max_height': 5, 'weight': 35, 'assembled': False},
    {'id': 'plt8', 'type': 'PLT8', 'length': 8, 'width': 8, 'max_height': 5, 'weight': 40, 'assembled': False},
]

# Ensure no item is both assembled and bundled
for item in items:
    if item['assembled'] and item['bundled']:
        raise ValueError('An item cannot be both assembled and bundled.')

# Define solver
solver = pywraplp.Solver.CreateSolver('SCIP')
if not solver:
    raise Exception("Solver not found")

# Decision variables
x = {}
for i in range(len(items)):
    for j in range(len(pallets)):
        x[i, j] = solver.BoolVar(f'x_{i}_{j}')

# Constraints
# Each item must be placed in exactly one pallet
for i in range(len(items)):
    solver.Add(sum(x[i, j] for j in range(len(pallets))) == 1)

# Pallet constraints
for j in range(len(pallets)):
    max_height = pallets[j]['max_height']
    max_length = pallets[j]['length']
    max_width = pallets[j]['width']
    if pallets[j]['assembled']:
        for i in range(len(items)):
            if not items[i]['assembled']:
                solver.Add(x[i, j] == 0)
    if pallets[j]['type'] == 'BUNDLE':
        for i in range(len(items)):
            if not items[i]['bundled']:
                solver.Add(x[i, j] == 0)
    solver.Add(sum(items[i]['height'] * x[i, j] for i in range(len(items))) <= max_height)
    solver.Add(sum(items[i]['length'] * x[i, j] for i in range(len(items))) <= max_length)
    solver.Add(sum(items[i]['width'] * x[i, j] for i in range(len(items))) <= max_width)

# Objective: minimize the number of pallets used
solver.Minimize(sum(x[i, j] for i in range(len(items)) for j in range(len(pallets))))

# Solve the problem
status = solver.Solve()

# Output results in list format
result = {}
if status == pywraplp.Solver.OPTIMAL:
    total_pallets_used = sum(x[i, j].solution_value() for i in range(len(items)) for j in range(len(pallets)))
    result['total_pallets_used'] = total_pallets_used
    result['pallets'] = []
    for j in range(len(pallets)):
        pallet_items = [items[i] for i in range(len(items)) if x[i, j].solution_value() > 0.5]
        if pallet_items:
            actual_height = sum(item['height'] for item in pallet_items)
            total_weight = pallets[j]['weight'] + sum(item['weight'] for item in pallet_items)
            result['pallets'].append({
                'type': pallets[j]['type'],
                'dimensions': f"{pallets[j]['length']}x{pallets[j]['width']}x{pallets[j]['max_height']}",
                'actual_height': actual_height,
                'total_weight': total_weight,
                'items': pallet_items
            })
else:
    result['error'] = 'No optimal solution found'

print(result)
