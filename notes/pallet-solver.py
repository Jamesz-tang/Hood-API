# Create optimized pallets or parcels for the list of items to pack for shipping quotes using google or toolss. Each item has the following attributes.
# - weight
# - length
# - width
# - height
# - assembled, and
# - bundled
#
#
# Each pallet has the following a maximum height, fixed length, fixed width, weight,  a type of BUNDLE, PLT4, PLT6 and PLT8 and assembled (boolean).
#
# Create the minimum number of pallets using linear solution using google or tools,
#
# Consider the following Constraints
# 1. Assembled pallet can only hold assembled items only.
# 2, Bundle pallet can hold bundle items only.
# 3. Smaller pallets are preferred but not required.
# 4. No constraints on the weight of a pallet.
#
# The output must include the total number of pallets used, and total weight. Each pallet must include
# - actual height, and total weight including teh pallet weight of each pallet
# - the details of the items ii the pallet
# - the pallet type of the pallet


# To create an optimized pallet packing solution with Google OR-Tools given your constraints,
# you can use the Linear Programming (LP) solver. The problem involves several constraints and goals,
# such as minimizing the number of pallets used, considering pallet types, and packing constraints
# related to item assembly and bundling.
#

import json
from ortools.linear_solver import pywraplp


def create_optimization_model(items, pallets):
    # Create the solver
    solver = pywraplp.Solver.CreateSolver('SCIP')
    if not solver:
        raise Exception("SCIP solver not available")

    num_items = len(items)
    num_pallets = len(pallets)

    # Decision Variables
    x = {}
    for i in range(num_items):
        for j in range(num_pallets):
            x[i, j] = solver.IntVar(0, 1, f'x[{i},{j}]')

    y = {}
    for j in range(num_pallets):
        y[j] = solver.IntVar(0, 1, f'y[{j}]')

    # Constraints

    # Each item must be placed on exactly one pallet
    for i in range(num_items):
        solver.Add(solver.Sum(x[i, j] for j in range(num_pallets)) == 1)

    # Assembled items can only be on assembled pallets
    for i in range(num_items):
        if items[i]['assembled']:
            for j in range(num_pallets):
                if not pallets[j]['assembled']:
                    solver.Add(x[i, j] == 0)

    # Bundled items can only be on BUNDLE pallets
    for i in range(num_items):
        if items[i]['bundled']:
            for j in range(num_pallets):
                if pallets[j]['type'] != 'BUNDLE':
                    solver.Add(x[i, j] == 0)

    # Maximum height constraint for each pallet
    for j in range(num_pallets):
        height_sum = solver.Sum(x[i, j] * items[i]['height'] for i in range(num_items))
        solver.Add(height_sum <= pallets[j]['max_height'])

    # Each pallet that contains items must be used
    for j in range(num_pallets):
        for i in range(num_items):
            solver.Add(x[i, j] <= y[j])

    # Objective Function: Minimize the number of pallets used
    solver.Minimize(solver.Sum(y[j] for j in range(num_pallets)))

    # Solve the problem
    status = solver.Solve()

    if status != pywraplp.Solver.OPTIMAL:
        raise Exception("No optimal solution found")

    # Extract results
    result = {
        'total_pallets': 0,
        'pallets': []
    }

    for j in range(num_pallets):
        if y[j].solution_value() > 0:
            pallet_details = {
                'type': pallets[j]['type'],
                'max_height': pallets[j]['max_height'],
                'length': pallets[j]['length'],
                'width': pallets[j]['width'],
                'weight': pallets[j]['weight'],
                'actual_height': 0,
                'total_weight': pallets[j]['weight'],
                'items': []
            }

            total_height = 0
            total_weight = pallets[j]['weight']
            for i in range(num_items):
                if x[i, j].solution_value() > 0:
                    item = items[i]
                    total_weight += item['weight']
                    total_height += item['height']
                    pallet_details['items'].append({
                        'weight': item['weight'],
                        'length': item['length'],
                        'width': item['width'],
                        'height': item['height'],
                        'assembled': item['assembled'],
                        'bundled': item['bundled']
                    })

            pallet_details['actual_height'] = total_height
            pallet_details['total_weight'] = total_weight
            result['pallets'].append(pallet_details)
            result['total_pallets'] += 1

    return result


# Example Input
items = [
    {'weight': 15, 'length': 5, 'width': 4, 'height': 4, 'assembled': False, 'bundled': False},
    {'weight': 15, 'length': 5, 'width': 4, 'height': 4, 'assembled': False, 'bundled': False},
    {'weight': 16, 'length': 4, 'width': 4, 'height': 4, 'assembled': False, 'bundled': False},
    {'weight': 22, 'length': 4, 'width': 4, 'height': 3, 'assembled': False, 'bundled': False},

    # {'weight': 12, 'length': 3, 'width': 3, 'height': 2, 'assembled': True, 'bundled': False},
    # {'weight': 8, 'length': 2, 'width': 2, 'height': 1, 'assembled': True, 'bundled': False},
    # {'weight': 10, 'length': 3, 'width': 3, 'height': 2, 'assembled': True, 'bundled': False},
    # {'weight': 9, 'length': 2, 'width': 2, 'height': 2, 'assembled': True, 'bundled': False},
    # {'weight': 11, 'length': 2, 'width': 2, 'height': 2, 'assembled': True, 'bundled': False},
    # {'weight': 6, 'length': 1, 'width': 1, 'height': 1, 'assembled': True, 'bundled': False},
    #
    #
    # {'weight': 18, 'length': 108, 'width': 10, 'height': 5, 'assembled': False, 'bundled': True},
    # {'weight': 18, 'length': 108, 'width': 10, 'height': 5, 'assembled': False, 'bundled': True},
    # {'weight': 18, 'length': 108, 'width': 10, 'height': 5, 'assembled': False, 'bundled': True},

]

pallets = [
    {'type': 'BUNDLE', 'max_height': 5, 'length': 108, 'width': 10, 'weight': 1, 'assembled': False},
    {'type': 'BUNDLE', 'max_height': 5, 'length': 108, 'width': 10, 'weight': 1, 'assembled': False},
    {'type': 'BUNDLE', 'max_height': 5, 'length': 108, 'width': 10, 'weight': 1, 'assembled': False},

    {'type': 'PLT4', 'max_height': 5, 'length': 4, 'width': 4, 'weight': 25, 'assembled': True},
    {'type': 'PLT6', 'max_height': 6, 'length': 6, 'width': 6, 'weight': 35, 'assembled': True},
    {'type': 'PLT8', 'max_height': 8, 'length': 8, 'width': 8, 'weight': 45, 'assembled': True},
    {'type': 'PLT4', 'max_height': 4, 'length': 4, 'width': 4, 'weight': 20, 'assembled': True},
    {'type': 'PLT6', 'max_height': 7, 'length': 6, 'width': 6, 'weight': 30, 'assembled': True},
    {'type': 'PLT8', 'max_height': 9, 'length': 8, 'width': 8, 'weight': 40, 'assembled': True},

    {'type': 'PLT4', 'max_height': 5, 'length': 4, 'width': 4, 'weight': 25, 'assembled': False},
    {'type': 'PLT4', 'max_height': 5, 'length': 4, 'width': 4, 'weight': 25, 'assembled': False},
    {'type': 'PLT4', 'max_height': 5, 'length': 4, 'width': 4, 'weight': 25, 'assembled': False},

    {'type': 'PLT6', 'max_height': 6, 'length': 6, 'width': 6, 'weight': 35, 'assembled': False},
    {'type': 'PLT6', 'max_height': 6, 'length': 6, 'width': 6, 'weight': 35, 'assembled': False},
    {'type': 'PLT6', 'max_height': 6, 'length': 6, 'width': 6, 'weight': 35, 'assembled': False},

    {'type': 'PLT8', 'max_height': 9, 'length': 8, 'width': 8, 'weight': 40, 'assembled': False},
    {'type': 'PLT8', 'max_height': 9, 'length': 8, 'width': 8, 'weight': 40, 'assembled': False},
    {'type': 'PLT8', 'max_height': 9, 'length': 8, 'width': 8, 'weight': 40, 'assembled': False},
    {'type': 'PLT8', 'max_height': 9, 'length': 8, 'width': 8, 'weight': 40, 'assembled': False},

]

result = create_optimization_model(items, pallets)

# Print result in JSON format
print(json.dumps(result, indent=4))
