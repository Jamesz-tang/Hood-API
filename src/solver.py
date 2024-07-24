import json
from ortools.linear_solver import pywraplp


class PalletOptimizer:
    def __init__(self, items, pallets):
        self.items = items
        self.pallets = pallets
        self.solver = pywraplp.Solver.CreateSolver('SCIP')
        if not self.solver:
            raise Exception("SCIP solver is not available.")
        self.x = {}  # Decision variables for item placement
        self.h = []  # Actual height of each pallet

    def setup_problem(self):
        num_items = len(self.items)
        num_pallets = len(self.pallets)

        # Initialize decision variables
        for i in range(num_items):
            for j in range(num_pallets):
                self.x[(i, j)] = self.solver.BoolVar(f'x[{i},{j}]')

        self.h = [self.solver.NumVar(0, self.pallets[j]['max_height'], f'h[{j}]') for j in range(num_pallets)]

        # Objective function: minimize the total height of all pallets
        self.solver.Minimize(self.solver.Sum([self.h[j] for j in range(num_pallets)]))

        # Constraints
        # Ensure each item is assigned to exactly one pallet
        for i in range(num_items):
            self.solver.Add(self.solver.Sum([self.x[(i, j)] for j in range(num_pallets)]) == 1)

        # Pallet type and item type constraints
        for j in range(num_pallets):
            pallet = self.pallets[j]
            for i in range(num_items):
                item = self.items[i]
                # Assembled items can only go on assembled pallets
                if item['assembled'] and not pallet['assembled']:
                    self.solver.Add(self.x[(i, j)] == 0)
                # Bundled items can only go on 'BD' type pallets
                if item['bundled'] and pallet['type'] != 'BD':
                    self.solver.Add(self.x[(i, j)] == 0)

        # Pallet dimensions and height constraints
        for j in range(num_pallets):
            pallet = self.pallets[j]
            # Ensure items fit within pallet dimensions
            for i in range(num_items):
                item = self.items[i]
                self.solver.Add(self.x[(i, j)] * item['length'] <= pallet['length'])
                self.solver.Add(self.x[(i, j)] * item['width'] <= pallet['width'])
                self.solver.Add(self.h[j] <= pallet['max_height'])

            # Simplified height constraint: items' heights should fit in the pallet's height
            self.solver.Add(
                self.h[j] == self.solver.Sum([item['height'] * self.x[(i, j)] for i, item in enumerate(self.items)])
            )

    def solve(self):
        status = self.solver.Solve()
        if status == pywraplp.Solver.OPTIMAL:
            return self.format_solution()
        else:
            return {"message": "No optimal solution found."}

    def format_solution(self):
        result = {
            "total_pallets_used": 0,
            "total_weight_including_pallets": 0,
            "pallets": []
        }

        num_items = len(self.items)
        num_pallets = len(self.pallets)

        for j in range(num_pallets):
            if self.h[j].solution_value() > 0:
                pallet_items = []
                pallet_weight = self.pallets[j]['weight']
                for i in range(num_items):
                    if self.x[(i, j)].solution_value() > 0:
                        pallet_items.append(self.items[i])
                        pallet_weight += self.items[i]['weight']

                result['total_pallets_used'] += 1
                result['total_weight_including_pallets'] += pallet_weight
                result['pallets'].append({
                    "pallet_type": self.pallets[j]['type'],
                    "actual_height": self.h[j].solution_value(),
                    "total_weight": pallet_weight,
                    "items": pallet_items
                })

        return result


# Example usage
items = [
    {'weight': 10, 'length': 1.5, 'width': 1.0, 'height': 0.5, 'assembled': False, 'bundled': False},
    {'weight': 15, 'length': 2.0, 'width': 1.0, 'height': 0.5, 'assembled': False, 'bundled': False},
    {'weight': 25, 'length': 2.0, 'width': 1.5, 'height': 1.0, 'assembled': False, 'bundled': False},
    {'weight': 12, 'length': 1.2, 'width': 0.8, 'height': 0.6, 'assembled': False, 'bundled': False},

    {'weight': 8, 'length': 1.0, 'width': 0.5, 'height': 0.5, 'assembled': True, 'bundled': False},
    {'weight': 20, 'length': 1.0, 'width': 1.0, 'height': 1.0, 'assembled': True, 'bundled': False},
    {'weight': 18, 'length': 1.5, 'width': 1.0, 'height': 0.8, 'assembled': True, 'bundled': False},

    {'weight': 7, 'length': 1.0, 'width': 1.0, 'height': 0.4, 'assembled': False, 'bundled': True},
    {'weight': 5, 'length': 1.0, 'width': 1.0, 'height': 0.5, 'assembled': False, 'bundled': True},
    {'weight': 6, 'length': 1.0, 'width': 1.0, 'height': 0.6, 'assembled': False, 'bundled': True}
]

pallets = [
    {'max_height': 2.0, 'length': 2.0, 'width': 2.0, 'weight': 30, 'type': 'PLT4', 'assembled': False},
    {'max_height': 2.5, 'length': 2.5, 'width': 2.5, 'weight': 35, 'type': 'PLT6', 'assembled': False},
    {'max_height': 3.0, 'length': 3.0, 'width': 3.0, 'weight': 40, 'type': 'PLT8', 'assembled': False},

    {'max_height': 2.0, 'length': 2.0, 'width': 2.0, 'weight': 30, 'type': 'Assembled', 'assembled': True},
    {'max_height': 2.0, 'length': 2.0, 'width': 2.0, 'weight': 30, 'type': 'Assembled', 'assembled': True},
    {'max_height': 2.0, 'length': 2.0, 'width': 2.0, 'weight': 30, 'type': 'Assembled', 'assembled': True},

    {'max_height': 1.0, 'length': 1.0, 'width': 1.0, 'weight': 20, 'type': 'BD', 'assembled': False},
    {'max_height': 1.0, 'length': 1.0, 'width': 1.0, 'weight': 20, 'type': 'BD', 'assembled': False},
    {'max_height': 1.0, 'length': 1.0, 'width': 1.0, 'weight': 20, 'type': 'BD', 'assembled': False},
]

optimizer = PalletOptimizer(items, pallets)
optimizer.setup_problem()
result = optimizer.solve()
json_data = json.dumps(result, default=lambda o: o.__dict__, indent=4)
print(json_data)
