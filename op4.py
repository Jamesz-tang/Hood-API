# Optimize bins for the list of items with weight, dimensions and a field representing whether it is an assembled, another field representing whether it is a bundle item using google OR Tools. Considering the given list of pallet types, each has a type,  maximum height, fixed width and fixed length. Each pallet type can be used multiple times if needed. Items on the same pallet can be put side by side if there aere room to fit. Assembled items cannot be stacked over another assembled item in the same pallet. Each bundle item must be in a bundle and cannot have any other items. The bin must provide actual height.  Smaller pallets are preferred but not required. There are no constraints on the weight of a pallet.

# Define the problem data:

# List of items with their weight, dimensions (length, width, height), assembled flag, and bundle flag.
# List of pallet types with their dimensions (length, width, max height).
# Formulate the constraints:
#
# Items must fit within the dimensions of the pallets.
# Assembled items cannot be stacked over other assembled items in the same pallet.
# Bundle items must be in a bundle and cannot share a pallet with any other items.
# Optimize for using the smallest possible pallets while considering all constraints.
# Implement the OR-Tools model:
#
# Use OR-Tools to define variables and constraints for the problem.
# Use a solver to find the optimal bin (pallet) packing configuration.


from ortools.sat.python import cp_model

class BinPackingModel:
    def __init__(self, items, pallets):
        self.items = items
        self.pallets = pallets
        self.model = cp_model.CpModel()
        self._create_variables()
        self._add_constraints()
        self._define_objective()

    def _create_variables(self):
        # Create variables for items in each pallet and their positions
        self.item_in_pallet = {}
        self.item_positions = {}
        self.pallet_heights = []

        for i, item in enumerate(self.items):
            for j, pallet in enumerate(self.pallets):
                self.item_in_pallet[(i, j)] = self.model.NewBoolVar(f'item_{i}_in_pallet_{j}')

                # Variables for item positions within a pallet
                self.item_positions[(i, j)] = (
                    self.model.NewIntVar(0, pallet['length'], f'item_{i}_x_pallet_{j}'),
                    self.model.NewIntVar(0, pallet['width'], f'item_{i}_y_pallet_{j}'),
                    self.model.NewIntVar(0, pallet['height'], f'item_{i}_z_pallet_{j}')
                )

        # Variables for height of each pallet
        for j, pallet in enumerate(self.pallets):
            self.pallet_heights.append(self.model.NewIntVar(0, pallet['height'], f'pallet_{j}_height'))

    def _add_constraints(self):
        # Ensure each item is placed in exactly one pallet
        for i in range(len(self.items)):
            self.model.Add(sum(self.item_in_pallet[(i, j)] for j in range(len(self.pallets))) == 1)

        for j, pallet in enumerate(self.pallets):
            pallet_items = [i for i in range(len(self.items)) if self.items[i]['bundle'] == 0]
            for i in pallet_items:
                x, y, z = self.item_positions[(i, j)]
                item = self.items[i]

                # Ensure items fit within the pallet dimensions
                self.model.Add(x + item['length'] <= pallet['length']).OnlyEnforceIf(self.item_in_pallet[(i, j)])
                self.model.Add(y + item['width'] <= pallet['width']).OnlyEnforceIf(self.item_in_pallet[(i, j)])
                self.model.Add(z + item['height'] <= pallet['height']).OnlyEnforceIf(self.item_in_pallet[(i, j)])

                # Ensure the total height of items in the pallet does not exceed the pallet height
                self.model.Add(z + item['height'] <= self.pallet_heights[j]).OnlyEnforceIf(self.item_in_pallet[(i, j)])

            # Assembled items constraints
            assembled_items = [i for i in range(len(self.items)) if self.items[i]['assembled']]
            for i in assembled_items:
                z = self.item_positions[(i, j)][2]
                item = self.items[i]

                for k in assembled_items:
                    if i != k:
                        z_k = self.item_positions[(k, j)][2]
                        self.model.Add(z + item['height'] <= z_k).OnlyEnforceIf(self.item_in_pallet[(i, j)].Not()).OnlyEnforceIf(self.item_in_pallet[(k, j)].Not())

            # Bundle items constraints
            bundle_items = [i for i in range(len(self.items)) if self.items[i]['bundle']]
            for i in bundle_items:
                self.model.Add(sum(self.item_in_pallet[(i, j)] for j in range(len(self.pallets))) == 1)
                self.model.Add(sum(self.item_in_pallet[(i, j)] for k in range(len(self.items)) if k != i) == 0).OnlyEnforceIf(self.item_in_pallet[(i, j)])

    def _define_objective(self):
        # Minimize the total height of pallets used
        self.model.Minimize(sum(self.pallet_heights))

    def solve(self):
        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print('Solution:')
            for j, pallet in enumerate(self.pallets):
                print(f'Pallet {j}:')
                for i in range(len(self.items)):
                    if solver.Value(self.item_in_pallet[(i, j)]):
                        x, y, z = [solver.Value(v) for v in self.item_positions[(i, j)]]
                        print(f'  Item {i} at position (x={x}, y={y}, z={z})')
                print(f'  Pallet height: {solver.Value(self.pallet_heights[j])}')
        else:
            print('No solution found.')

# Example usage
items = [
    {'weight': 10, 'length': 2, 'width': 2, 'height': 2, 'assembled': True, 'bundle': False},
    {'weight': 15, 'length': 2, 'width': 2, 'height': 1, 'assembled': False, 'bundle': False},
    {'weight': 15, 'length': 3, 'width': 3, 'height': 1, 'assembled': False, 'bundle': False},
    {'weight': 5, 'length': 1, 'width': 1, 'height': 1, 'assembled': False, 'bundle': False},
    # Add more items as needed
]

pallets = [
    {'length': 10, 'width': 10, 'height': 10},
    {'length': 5, 'width': 5, 'height': 5},
    {'length': 5, 'width': 5, 'height': 5},
    {'length': 15, 'width': 15, 'height': 15},

    # Add more pallet types as needed
]

model = BinPackingModel(items, pallets)
model.solve()


# his script sets up a constraint programming model to find the optimal packing of items into pallets while respecting the constraints for assembled and bundle items. The objective is to minimize the total height of the pallets used, with a preference for smaller pallets. The solver provides the positions of items within each pallet, and the actual height of each pallet used.







