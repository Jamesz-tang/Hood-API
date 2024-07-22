from ortools.sat.python import cp_model

# Optimize packages  for the list of items with weight, dimensions and a field representing whether it is an assembled, another field representing whether it is a bundle item using google OR Tools. Considering the given list of pallet types, each has a type,  maximum height, fixed width and fixed length. Each pallet type can be used multiple times if needed. Assembled items cannot be stacked over another assembled item in the same pallet. Each bundle item must be in a bundle and cannot have any other items. Smaller pallets are preferred but not required. There are no constraints on the weight of a pallet.
#
# ChatGPT
# Memory updated
# To optimize the packaging of items using Google OR-Tools, we'll follow these steps:
#
# Define the Problem:
#
# Items: Each item has a weight, dimensions (length, width, height), an assembled flag, and a bundle flag.
# Pallets: Each pallet type has a type, maximum height, fixed width, and fixed length.
# Constraints:
# Assembled items cannot be stacked over another assembled item in the same pallet.
# Each bundle item must be in a separate bundle and cannot share a pallet with other items.
# Smaller pallets are preferred but not required.
# No constraints on the weight of a pallet.
# Formulate the Optimization Model:
#
# Use OR-Tools to define decision variables, constraints, and the objective function.
# Decision variables will represent whether an item is placed on a specific pallet and the position of the item on the pallet.
# Constraints will ensure items are placed within the dimensions of the pallets, assembled items are not stacked incorrectly, and bundle items are isolated.
# The objective function will aim to minimize the number of pallets used, with a preference for smaller pallets.
# Implement the Model:
#
# Define the items and pallet types.
# Set up the OR-Tools model with the defined constraints and objective function.
# Solve the model and extract the solution.

class PackagingOptimizer:
    def __init__(self, items, pallets):
        self.items = items
        self.pallets = pallets
        self.model = cp_model.CpModel()

    def define_variables(self):
        self.item_on_pallet = {}
        for i, item in enumerate(self.items):
            for p, pallet in enumerate(self.pallets):
                self.item_on_pallet[i, p] = self.model.NewBoolVar(f'item_{i}_on_pallet_{p}')

        self.pallet_height = {}
        for p, pallet in enumerate(self.pallets):
            self.pallet_height[p] = self.model.NewIntVar(0, pallet['max_height'], f'pallet_{p}_height')

    def add_constraints(self):
        for i, item in enumerate(self.items):
            # Each item must be on exactly one pallet
            self.model.Add(sum(self.item_on_pallet[i, p] for p in range(len(self.pallets))) == 1)

            if item['bundle']:
                # Bundle items must be in their own pallet
                for j, other_item in enumerate(self.items):
                    if i != j:
                        for p in range(len(self.pallets)):
                            self.model.Add(self.item_on_pallet[i, p] + self.item_on_pallet[j, p] <= 1)

        for p, pallet in enumerate(self.pallets):
            assembled_items = [i for i, item in enumerate(self.items) if item['assembled']]
            for i in assembled_items:
                for j in assembled_items:
                    if i != j:
                        self.model.Add(self.item_on_pallet[i, p] + self.item_on_pallet[j, p] <= 1)

            # Ensure items fit within pallet dimensions
            for i, item in enumerate(self.items):
                self.model.Add(self.item_on_pallet[i, p] * item['height'] <= pallet['max_height'])
                self.model.Add(self.item_on_pallet[i, p] * item['length'] <= pallet['length'])
                self.model.Add(self.item_on_pallet[i, p] * item['width'] <= pallet['width'])

            # Ensure pallet height is within max height
            self.model.Add(
                sum(self.item_on_pallet[i, p] * self.items[i]['height'] for i in range(len(self.items))) <= pallet[
                    'max_height'])

    def set_objective(self):
        self.model.Minimize(sum(self.pallet_height[p] for p in range(len(self.pallets))))

    def solve(self):
        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            for p in range(len(self.pallets)):
                print(f'Pallet {p}:')
                for i in range(len(self.items)):
                    if solver.Value(self.item_on_pallet[i, p]):
                        print(f'  Item {i}')
        else:
            print('No solution found.')


# Example usage
items = [
    {'weight': 10, 'length': 2, 'width': 2, 'height': 2, 'assembled': False, 'bundle': False},
    {'weight': 20, 'length': 3, 'width': 3, 'height': 3, 'assembled': True, 'bundle': False},
    {'weight': 15, 'length': 1, 'width': 1, 'height': 1, 'assembled': False, 'bundle': True},
    # Add more items
]

pallets = [
    {'type': 'small', 'max_height': 10, 'length': 5, 'width': 5},
    {'type': 'large', 'max_height': 15, 'length': 10, 'width': 10},
    # Add more pallet types
]

optimizer = PackagingOptimizer(items, pallets)
optimizer.define_variables()
optimizer.add_constraints()
optimizer.set_objective()
optimizer.solve()
