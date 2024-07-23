from item import Item
from pallet import Pallet
from solver import PackingSolver

class PackingSystem:
    def __init__(self, items_data, pallets_data):
        self.items = [Item(**item) for item in items_data]
        self.pallets = [Pallet(**pallet) for pallet in pallets_data]
        self.validate_items()

    def validate_items(self):
        for item in self.items:
            if item.assembled and item.bundled:
                raise ValueError('An item cannot be both assembled and bundled.')

    def solve_packing(self):
        solver = PackingSolver(self.items, self.pallets)
        solver.create_variables()
        solver.add_constraints()
        solver.set_objective()
        return solver.solve()
