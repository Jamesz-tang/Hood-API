from ortools.linear_solver import pywraplp


class PackingSolver:
    def __init__(self, items, pallets):
        self.items = items
        self.pallets = pallets
        self.solver = pywraplp.Solver.CreateSolver('SCIP')
        if not self.solver:
            raise Exception("Solver not found")
        self.x = {}

    def create_variables(self):
        for i in range(len(self.items)):
            for j in range(len(self.pallets)):
                self.x[i, j] = self.solver.BoolVar(f'x_{i}_{j}')

    def add_constraints(self):
        # Each item must be placed in exactly one pallet
        for i in range(len(self.items)):
            self.solver.Add(sum(self.x[i, j] for j in range(len(self.pallets))) == 1)

        # Pallet constraints
        for j in range(len(self.pallets)):
            pallet = self.pallets[j]
            if pallet.assembled:
                for i in range(len(self.items)):
                    if not self.items[i].assembled:
                        self.solver.Add(self.x[i, j] == 0)
            if pallet.type == 'BUNDLE':
                for i in range(len(self.items)):
                    if not self.items[i].bundled:
                        self.solver.Add(self.x[i, j] == 0)
            self.solver.Add(
                sum(self.items[i].height * self.x[i, j] for i in range(len(self.items))) <= pallet.max_height)
            self.solver.Add(sum(self.items[i].length * self.x[i, j] for i in range(len(self.items))) <= pallet.length)
            self.solver.Add(sum(self.items[i].width * self.x[i, j] for i in range(len(self.items))) <= pallet.width)

    def set_objective(self):
        self.solver.Minimize(sum(self.x[i, j] for i in range(len(self.items)) for j in range(len(self.pallets))))

    def solve(self):
        status = self.solver.Solve()
        result = {}
        if status == self.solver.OPTIMAL:
            total_pallets_used = 0
            result['pallets'] = []
            for j in range(len(self.pallets)):
                pallet = self.pallets[j]
                pallet_items = [self.items[i] for i in range(len(self.items)) if self.x[i, j].solution_value() > 0.5]
                if pallet_items:
                    total_pallets_used += 1
                    actual_height = sum(item.height for item in pallet_items)
                    total_weight = self.pallets[j].weight + sum(item.weight for item in pallet_items)
                    result['pallets'].append({
                        'pallet_type': pallet,
                        'actual_height': actual_height,
                        'total_weight': total_weight,
                        'items': pallet_items
                    })
                result['total_pallets_used'] = total_pallets_used

        else:
            result['error'] = 'No optimal solution found'
        return result
