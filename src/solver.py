import json

from ortools.linear_solver import pywraplp
from dataclasses import dataclass


@dataclass
class Item:
    sku: str
    weight: float
    length: float
    width: float
    height: float
    assembled: bool
    bundled: bool


@dataclass
class Pallet:
    max_volume: float
    length: float
    width: float
    weight: float
    type: str  # 'BD', 'PLT4', 'PLT6', 'PLT8'
    assembled: bool
    size: int


class PalletOptimizer:
    def __init__(self, items, pallets):
        self.items = items
        self.pallets = pallets
        self.solver = pywraplp.Solver.CreateSolver('SCIP')

    def create_variables(self):
        # Create binary decision variables for each item-pallet combination
        self.item_pallet_vars = {}
        for i, item in enumerate(self.items):
            for j, pallet in enumerate(self.pallets):
                self.item_pallet_vars[(i, j)] = self.solver.BoolVar(f'item_{i}_on_pallet_{j}')

        # Create binary decision variables for each pallet being used
        self.pallet_used_vars = {}
        for j, pallet in enumerate(self.pallets):
            self.pallet_used_vars[j] = self.solver.BoolVar(f'pallet_{j}_used')

    def add_constraints(self):
        # Each item must be assigned to exactly one pallet
        for i, item in enumerate(self.items):
            self.solver.Add(sum(self.item_pallet_vars[(i, j)] for j in range(len(self.pallets))) == 1)

        # Constraint: item dimensions must fit within pallet dimensions
        for i, item in enumerate(self.items):
            for j, pallet in enumerate(self.pallets):
                if item.length > pallet.length or item.width > pallet.width:
                    self.solver.Add(self.item_pallet_vars[(i, j)] == 0)

        # Constraint: assembled items only on assembled pallets
        for i, item in enumerate(self.items):
            if item.assembled:
                for j, pallet in enumerate(self.pallets):
                    if not pallet.assembled:
                        self.solver.Add(self.item_pallet_vars[(i, j)] == 0)

        # Constraint: bundled items only on bundle pallets
        for i, item in enumerate(self.items):
            if item.bundled:
                for j, pallet in enumerate(self.pallets):
                    if pallet.type != 'BD':
                        self.solver.Add(self.item_pallet_vars[(i, j)] == 0)

        # Constraint: no mixed pallet types (assembled, bundled)
        for j, pallet in enumerate(self.pallets):
            if pallet.assembled:
                self.solver.Add(sum(
                    self.item_pallet_vars[(i, j)] for i in range(len(self.items)) if self.items[i].assembled) == sum(
                    self.item_pallet_vars[(i, j)] for i in range(len(self.items)) if self.items[i].bundled) == 0)
            elif pallet.type == 'BD':
                self.solver.Add(
                    sum(self.item_pallet_vars[(i, j)] for i in range(len(self.items)) if self.items[i].bundled) == sum(
                        self.item_pallet_vars[(i, j)] for i in range(len(self.items)) if self.items[i].assembled) == 0)

        # Constraint: volume capacity of each pallet
        for j, pallet in enumerate(self.pallets):
            self.solver.Add(sum(
                self.item_pallet_vars[(i, j)] * (self.items[i].length * self.items[i].width * self.items[i].height)
                for i in range(len(self.items))
            ) <= pallet.max_volume)

        # Constraint: if a pallet is used, it must contain at least one item
        for j, pallet in enumerate(self.pallets):
            self.solver.Add(self.pallet_used_vars[j] * len(self.items) >= sum(
                self.item_pallet_vars[(i, j)] for i in range(len(self.items))))

        # Constraint: Assembled pallets can only hold assembled items
        for j, pallet in enumerate(self.pallets):
            if pallet.assembled:
                for i, item in enumerate(self.items):
                    if not item.assembled:
                        self.solver.Add(self.item_pallet_vars[(i, j)] == 0)

    def set_objective(self):
        # Objective: Minimize the number of pallets used and prefer smaller pallets
        objective = self.solver.Objective()

        for j, pallet in enumerate(self.pallets):
            # Penalize larger pallets by adding a term proportional to the pallet size
            # Smaller size has a lower penalty, hence preferred
            penalty = pallet.size
            objective.SetCoefficient(self.pallet_used_vars[j],
                                     1 + penalty / 1000.0)  # Adjust the penalty scale as needed

        objective.SetMinimization()

    def solve(self):
        self.create_variables()
        self.add_constraints()
        self.set_objective()
        status = self.solver.Solve()

        if status == pywraplp.Solver.OPTIMAL:
            return self.get_results()
        else:
            return "No optimal solution found"

    def get_results(self):
        results = {
            'total_pallets_used': 0,
            'pallets': []
        }

        for j, pallet in enumerate(self.pallets):
            if self.pallet_used_vars[j].solution_value() > 0.5:
                pallet_details = {
                    'type': pallet.type,
                    'size': pallet.size,
                    'height': None,  # Will calculate later
                    'items': [],
                    'actual_volume': 0,
                    'total_weight': pallet.weight
                }

                total_volume = 0
                for i, item in enumerate(self.items):
                    if self.item_pallet_vars[(i, j)].solution_value() > 0.5:
                        item_details = {
                            'sku': item.sku,
                            'weight': item.weight,
                            'length': item.length,
                            'width': item.width,
                            'height': item.height,
                            'assembled': item.assembled,
                            'bundled': item.bundled
                        }
                        pallet_details['items'].append(item_details)
                        volume = item.length * item.width * item.height
                        pallet_details['actual_volume'] += volume
                        pallet_details['total_weight'] += item.weight

                # Calculate the height based on total volume and pallet dimensions
                if pallet_details['actual_volume'] > 0:
                    pallet_details['height'] = pallet_details['actual_volume'] / (pallet.length * pallet.width)

                results['total_pallets_used'] += 1
                results['pallets'].append(pallet_details)

        return results


# Example usage
if __name__ == '__main__':
    # Sample items with SKU
    items = [
        Item(sku='ITEM001', weight=10, length=10, width=10, height=10, assembled=False, bundled=False),
        Item(sku='ITEM004', weight=12, length=12, width=12, height=12, assembled=False, bundled=False),
        Item(sku='ITEM007', weight=20, length=20, width=20, height=20, assembled=False, bundled=False),
        Item(sku='ITEM010', weight=11, length=11, width=11, height=11, assembled=False, bundled=False),

        Item(sku='ITEM002', weight=5, length=5, width=5, height=5, assembled=True, bundled=False),
        Item(sku='ITEM005', weight=8, length=8, width=8, height=8, assembled=True, bundled=False),
        Item(sku='ITEM008', weight=6, length=6, width=6, height=6, assembled=True, bundled=False),

        Item(sku='ITEM009', weight=9, length=96, width=10, height=6, assembled=False, bundled=True),
        Item(sku='ITEM009', weight=9, length=96, width=10, height=6, assembled=False, bundled=True),

    ]

    # Sample pallets
    pallets = [
        Pallet(max_volume=5000, length=18, width=18, weight=50, type='PLT4', assembled=False, size=4),
        Pallet(max_volume=62500, length=25, width=25, weight=60, type='PLT8', assembled=False, size=8),

        Pallet(max_volume=62500, length=25, width=25, weight=60, type='PLT8', assembled=True, size=8),

        Pallet(max_volume=5760, length=96, width=10, weight=70, type='BD', assembled=False, size=6),
        Pallet(max_volume=5760, length=96, width=10, weight=70, type='BD', assembled=False, size=6),

    ]

    optimizer = PalletOptimizer(items, pallets)
    result = optimizer.solve()
    json_data = json.dumps(result, default=lambda o: o.__dict__, indent=4)
    print(json_data)
