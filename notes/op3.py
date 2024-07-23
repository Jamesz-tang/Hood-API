from ortools.linear_solver import pywraplp
from ortools.sat.python import cp_model


def optimize_bins(items, pallets):
    # Define the model
    model = cp_model.CpModel()

    # Define variables
    num_items = len(items)
    num_pallets = len(pallets)

    # Create decision variables
    x = {}
    for i in range(num_items):
        for j in range(num_pallets):
            x[(i, j)] = model.NewBoolVar(f'x_{i}_{j}')

    # Ensure each item is placed in one pallet
    for i in range(num_items):
        model.Add(sum(x[(i, j)] for j in range(num_pallets)) == 1)

    # Define constraints for bundles
    for i in range(num_items):
        if items[i]['bundle']:
            for j in range(num_pallets):
                for k in range(num_items):
                    if k != i:
                        model.Add(x[(i, j)] + x[(k, j)] <= 1)

    # Define constraints for assembled items
    for j in range(num_pallets):
        assembled_items_in_pallet = []
        for i in range(num_items):
            if items[i]['assembled']:
                assembled_items_in_pallet.append(i)

        if len(assembled_items_in_pallet) > 1:
            for i in range(len(assembled_items_in_pallet) - 1):
                model.Add(sum(x[(assembled_items_in_pallet[i], j)] for j in range(num_pallets)) <= sum(
                    x[(assembled_items_in_pallet[i + 1], j)] for j in range(num_pallets)))

    # Define the height used for each pallet
    height_used = []
    for j in range(num_pallets):
        height_used_j = model.NewIntVar(0, max(p['max_height'] for p in pallets), f'height_used_{j}')
        model.Add(height_used_j == sum(x[(i, j)] * items[i]['height'] for i in range(num_items)))
        height_used.append(height_used_j)

    # Ensure height used does not exceed the maximum height of each pallet
    for j in range(num_pallets):
        model.Add(height_used[j] <= pallets[j]['max_height'])

    # Define objective to minimize the number of pallets used
    model.Minimize(sum(x[(i, j)] for i in range(num_items) for j in range(num_pallets)))

    # Solve the model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print(f'Solution found with objective value {solver.ObjectiveValue()}:')
        for j in range(num_pallets):
            pallet_items = []
            for i in range(num_items):
                if solver.BooleanValue(x[(i, j)]):
                    pallet_items.append(items[i])
            if pallet_items:
                print(f'Pallet {j} contains items: {pallet_items}')
                print(f'Height used in Pallet {j}: {solver.Value(height_used[j])}')
    else:
        print('No solution found.')


# Example usage
items = [
    {'weight': 10, 'length': 2, 'width': 2, 'height': 3, 'assembled': False, 'bundle': False},
    {'weight': 15, 'length': 3, 'width': 2, 'height': 2, 'assembled': True, 'bundle': False},
    {'weight': 5, 'length': 1, 'width': 1, 'height': 1, 'assembled': False, 'bundle': True},
    # Add more items as needed
]

pallets = [
    {'type': 'Pallet1', 'length': 10, 'width': 10, 'max_height': 15},
    {'type': 'Pallet2', 'length': 8, 'width': 8, 'max_height': 12},
    # Add more pallet types as needed
]

optimize_bins(items, pallets)
