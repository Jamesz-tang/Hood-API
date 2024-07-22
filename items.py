from ortools.linear_solver import pywraplp
import json


def optimize_packages(items, pallets):
    # Create the solver
    solver = pywraplp.Solver.CreateSolver('SCIP')
    if not solver:
        return None

    # Define variables
    num_items = len(items)
    num_pallets = len(pallets)

    # Variables: x[i][j] is True if item i is packed in pallet j
    x = {}
    for i in range(num_items):
        for j in range(num_pallets):
            x[i, j] = solver.BoolVar(f'x_{i}_{j}')

    # Constraints
    # Each item must be in exactly one pallet
    for i in range(num_items):
        solver.Add(sum(x[i, j] for j in range(num_pallets)) == 1)

    # Pallet constraints: height, length, width
    for j in range(num_pallets):
        solver.Add(sum(x[i, j] * items[i]['height'] for i in range(num_items)) <= pallets[j]['max_height'])
        solver.Add(sum(x[i, j] * items[i]['length'] for i in range(num_items)) <= pallets[j]['length'])
        solver.Add(sum(x[i, j] * items[i]['width'] for i in range(num_items)) <= pallets[j]['width'])

    # Assembled item constraints: no stacking on top of another assembled item
    for j in range(num_pallets):
        assembled_items = [i for i in range(num_items) if items[i]['is_assembled']]
        for i in assembled_items:
            solver.Add(sum(x[k, j] for k in assembled_items if k != i) == 0)

    # # Bundle item constraints: must be alone in a pallet
    # for i in range(num_items):
    #     if items[i]['is_bundle']:
    #         for j in range(num_pallets):
    #             solver.Add(sum(x[k, j] for k in range(num_items) if k != i) == 0)

    # Objective: minimize the number of pallets used (prefer smaller pallets)
    solver.Minimize(solver.Sum(x[i, j] * (j + 1) for i in range(num_items) for j in range(num_pallets)))

    # Solve the problem
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        solution = []
        for j in range(num_pallets):
            pallet_items = []
            for i in range(num_items):
                if x[i, j].solution_value():
                    pallet_items.append(items[i])
            if pallet_items:
                solution.append({'pallet': pallets[j], 'items': pallet_items})
        return solution
    else:
        print('The problem does not have an optimal solution.')
        return None


# Example usage
items = [
    {'weight': 10, 'length': 2, 'width': 2, 'height': 2, 'is_assembled': False, 'is_bundle': False},
    {'weight': 5, 'length': 1, 'width': 1, 'height': 5, 'is_assembled': False, 'is_bundle': False},
    {'weight': 5, 'length': 1, 'width': 1, 'height': 5, 'is_assembled': False, 'is_bundle': False},
    # {'weight': 5, 'length': 1, 'width': 1, 'height': 1, 'is_assembled': False, 'is_bundle': True},
    {'weight': 5, 'length': 100, 'width': 4, 'height': 10, 'is_assembled': False, 'is_bundle': True},
    {'weight': 5, 'length': 100, 'width': 4, 'height': 10, 'is_assembled': False, 'is_bundle': True},
    {'weight': 5, 'length': 100, 'width': 4, 'height': 10, 'is_assembled': False, 'is_bundle': True},
    {'weight': 5, 'length': 100, 'width': 4, 'height': 10, 'is_assembled': False, 'is_bundle': True},
    {'weight': 10, 'length': 2, 'width': 2, 'height': 2, 'is_assembled': False, 'is_bundle': False},
    {'weight': 5, 'length': 1, 'width': 1, 'height': 5, 'is_assembled': False, 'is_bundle': False},
    {'weight': 5, 'length': 1, 'width': 1, 'height': 5, 'is_assembled': False, 'is_bundle': False},
    # {'weight': 5, 'length': 1, 'width': 1, 'height': 1, 'is_assembled': False, 'is_bundle': True},
    {'weight': 5, 'length': 100, 'width': 4, 'height': 10, 'is_assembled': False, 'is_bundle': True},
    {'weight': 5, 'length': 100, 'width': 4, 'height': 10, 'is_assembled': False, 'is_bundle': True},
    {'weight': 5, 'length': 100, 'width': 4, 'height': 10, 'is_assembled': False, 'is_bundle': True},
    {'weight': 5, 'length': 100, 'width': 4, 'height': 10, 'is_assembled': False, 'is_bundle': True},
    {'weight': 10, 'length': 2, 'width': 2, 'height': 2, 'is_assembled': False, 'is_bundle': False},
    {'weight': 5, 'length': 1, 'width': 1, 'height': 5, 'is_assembled': False, 'is_bundle': False},
    {'weight': 5, 'length': 1, 'width': 1, 'height': 5, 'is_assembled': False, 'is_bundle': False},
    # {'weight': 5, 'length': 1, 'width': 1, 'height': 1, 'is_assembled': False, 'is_bundle': True},
    {'weight': 5, 'length': 100, 'width': 4, 'height': 10, 'is_assembled': False, 'is_bundle': True},
    {'weight': 5, 'length': 100, 'width': 4, 'height': 10, 'is_assembled': False, 'is_bundle': True},
    {'weight': 5, 'length': 100, 'width': 4, 'height': 10, 'is_assembled': False, 'is_bundle': True},
    {'weight': 5, 'length': 100, 'width': 4, 'height': 10, 'is_assembled': False, 'is_bundle': True},
    {'weight': 10, 'length': 2, 'width': 2, 'height': 2, 'is_assembled': False, 'is_bundle': False},
    {'weight': 5, 'length': 1, 'width': 1, 'height': 5, 'is_assembled': False, 'is_bundle': False},
    {'weight': 5, 'length': 1, 'width': 1, 'height': 5, 'is_assembled': False, 'is_bundle': False},
    # {'weight': 5, 'length': 1, 'width': 1, 'height': 1, 'is_assembled': False, 'is_bundle': True},
    {'weight': 5, 'length': 100, 'width': 4, 'height': 10, 'is_assembled': False, 'is_bundle': True},
    {'weight': 5, 'length': 100, 'width': 4, 'height': 10, 'is_assembled': False, 'is_bundle': True},
    {'weight': 5, 'length': 100, 'width': 4, 'height': 10, 'is_assembled': False, 'is_bundle': True},
    {'weight': 5, 'length': 100, 'width': 4, 'height': 10, 'is_assembled': False, 'is_bundle': True},
    {'weight': 10, 'length': 2, 'width': 2, 'height': 2, 'is_assembled': False, 'is_bundle': False},
    {'weight': 5, 'length': 1, 'width': 1, 'height': 5, 'is_assembled': False, 'is_bundle': False},
    {'weight': 5, 'length': 1, 'width': 1, 'height': 5, 'is_assembled': False, 'is_bundle': False},
    # {'weight': 5, 'length': 1, 'width': 1, 'height': 1, 'is_assembled': False, 'is_bundle': True},
    {'weight': 5, 'length': 100, 'width': 4, 'height': 10, 'is_assembled': False, 'is_bundle': True},
    {'weight': 5, 'length': 100, 'width': 4, 'height': 10, 'is_assembled': False, 'is_bundle': True},
    {'weight': 5, 'length': 100, 'width': 4, 'height': 10, 'is_assembled': False, 'is_bundle': True},
    {'weight': 5, 'length': 100, 'width': 4, 'height': 10, 'is_assembled': False, 'is_bundle': True},

    {'weight': 10, 'length': 2, 'width': 2, 'height': 2, 'is_assembled': False, 'is_bundle': False},
    {'weight': 5, 'length': 1, 'width': 1, 'height': 5, 'is_assembled': False, 'is_bundle': False},
    {'weight': 5, 'length': 1, 'width': 1, 'height': 5, 'is_assembled': False, 'is_bundle': False},
    # {'weight': 5, 'length': 1, 'width': 1, 'height': 1, 'is_assembled': False, 'is_bundle': True},
    {'weight': 5, 'length': 100, 'width': 4, 'height': 10, 'is_assembled': False, 'is_bundle': True},
    {'weight': 5, 'length': 100, 'width': 4, 'height': 10, 'is_assembled': False, 'is_bundle': True},
    {'weight': 5, 'length': 100, 'width': 4, 'height': 10, 'is_assembled': False, 'is_bundle': True},
    {'weight': 5, 'length': 100, 'width': 4, 'height': 10, 'is_assembled': False, 'is_bundle': True},

    {'weight': 10, 'length': 2, 'width': 2, 'height': 2, 'is_assembled': False, 'is_bundle': False},
    {'weight': 5, 'length': 1, 'width': 1, 'height': 5, 'is_assembled': False, 'is_bundle': False},
    {'weight': 5, 'length': 1, 'width': 1, 'height': 5, 'is_assembled': False, 'is_bundle': False},
    # {'weight': 5, 'length': 1, 'width': 1, 'height': 1, 'is_assembled': False, 'is_bundle': True},
    {'weight': 5, 'length': 100, 'width': 4, 'height': 10, 'is_assembled': False, 'is_bundle': True},
    {'weight': 5, 'length': 100, 'width': 4, 'height': 10, 'is_assembled': False, 'is_bundle': True},
    {'weight': 5, 'length': 100, 'width': 4, 'height': 10, 'is_assembled': False, 'is_bundle': True},
    {'weight': 5, 'length': 100, 'width': 4, 'height': 10, 'is_assembled': False, 'is_bundle': True},

    {'weight': 10, 'length': 2, 'width': 2, 'height': 2, 'is_assembled': False, 'is_bundle': False},
    {'weight': 5, 'length': 1, 'width': 1, 'height': 5, 'is_assembled': False, 'is_bundle': False},
    {'weight': 5, 'length': 1, 'width': 1, 'height': 5, 'is_assembled': False, 'is_bundle': False},
    # {'weight': 5, 'length': 1, 'width': 1, 'height': 1, 'is_assembled': False, 'is_bundle': True},
    {'weight': 5, 'length': 100, 'width': 4, 'height': 10, 'is_assembled': False, 'is_bundle': True},
    {'weight': 5, 'length': 100, 'width': 4, 'height': 10, 'is_assembled': False, 'is_bundle': True},
    {'weight': 5, 'length': 100, 'width': 4, 'height': 10, 'is_assembled': False, 'is_bundle': True},
    {'weight': 5, 'length': 100, 'width': 4, 'height': 10, 'is_assembled': False, 'is_bundle': True},

    {'weight': 10, 'length': 2, 'width': 2, 'height': 2, 'is_assembled': False, 'is_bundle': False},
    {'weight': 5, 'length': 1, 'width': 1, 'height': 5, 'is_assembled': False, 'is_bundle': False},
    {'weight': 5, 'length': 1, 'width': 1, 'height': 5, 'is_assembled': False, 'is_bundle': False},
    # {'weight': 5, 'length': 1, 'width': 1, 'height': 1, 'is_assembled': False, 'is_bundle': True},
    {'weight': 5, 'length': 100, 'width': 4, 'height': 10, 'is_assembled': False, 'is_bundle': True},
    {'weight': 5, 'length': 100, 'width': 4, 'height': 10, 'is_assembled': False, 'is_bundle': True},
    {'weight': 5, 'length': 100, 'width': 4, 'height': 10, 'is_assembled': False, 'is_bundle': True},
    {'weight': 5, 'length': 100, 'width': 4, 'height': 10, 'is_assembled': False, 'is_bundle': True},
    # Add more items as needed
]

pallets = [
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},

    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 180, 'width': 17},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},

    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 6, 'length': 10, 'width': 5},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 18, 'width': 17},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    {'max_height': 10, 'length': 101, 'width': 5},
    # Add more pallets as needed
]

solution = optimize_packages(items, pallets)
print(json.dumps(solution))
