import math
from dataclasses import dataclass
from ortools.linear_solver import pywraplp


@dataclass
class Item:
    """
    Represents an item with its attributes for pallet optimization.

    Attributes:
        sku (str): Stock Keeping Unit identifier.
        weight (float): Weight of the item.
        length (float): Length of the item.
        width (float): Width of the item.
        height (float): Height of the item.
        assembled (bool): Indicates if the item is assembled.
        bundled (bool): Indicates if the item is bundled.
    """
    sku: str
    weight: float
    length: float
    width: float
    height: float
    assembled: bool
    bundled: bool


@dataclass
class Pallet:
    """
    Represents a pallet with its attributes for pallet optimization.

    Attributes:
        max_volume (float): Maximum volume capacity of the pallet.
        length (float): Length of the pallet.
        width (float): Width of the pallet.
        weight (float): Weight of the pallet.
        type (str): Type of the pallet (e.g., 'BD', 'PLT4', 'PLT6', 'PLT8').
        assembled (bool): Indicates if the pallet is assembled.
        size (int): Size identifier for the pallet.
    """
    max_volume: float
    length: float
    width: float
    weight: float
    type: str  # 'BD', 'PLT4', 'PLT6', 'PLT8'
    assembled: bool
    size: int


class PalletOptimizer:
    """
    Optimizes the use of pallets to pack items efficiently using the OR-Tools linear solver.

    Attributes:
        items (list[Item]): List of items to be packed.
        pallets (list[Pallet]): List of available pallets.
        solver (pywraplp.Solver): OR-Tools solver instance.
    """

    def __init__(self, items, pallets):
        """
        Initializes the optimizer with items and pallets.

        Args:
            items (list[Item]): List of items to be packed.
            pallets (list[Pallet]): List of available pallets.
        """
        self.items = items
        self.pallets = pallets
        self.solver = pywraplp.Solver.CreateSolver('SCIP')

    def create_variables(self):
        """
        Creates decision variables for the optimization problem.

        - Binary variables for each item-pallet combination.
        - Binary variables indicating whether each pallet is used.
        """
        self.item_pallet_vars = {}
        for i, item in enumerate(self.items):
            for j, pallet in enumerate(self.pallets):
                self.item_pallet_vars[(i, j)] = self.solver.BoolVar(f'item_{i}_on_pallet_{j}')

        self.pallet_used_vars = {}
        for j, pallet in enumerate(self.pallets):
            self.pallet_used_vars[j] = self.solver.BoolVar(f'pallet_{j}_used')

    def add_constraints(self):
        """
        Adds constraints to the optimization problem.

        - Each item must be assigned to exactly one pallet.
        - Item dimensions must fit within pallet dimensions.
        - Assembled items can only be placed on assembled pallets.
        - Bundled items can only be placed on bundle pallets.
        - No mixed pallet types (assembled, bundled) in a single pallet.
        - Volume capacity of each pallet must not be exceeded.
        - If a pallet is used, it must contain at least one item.
        - Assembled pallets can only hold assembled items.
        """
        for i, item in enumerate(self.items):
            self.solver.Add(sum(self.item_pallet_vars[(i, j)] for j in range(len(self.pallets))) == 1)

        for i, item in enumerate(self.items):
            for j, pallet in enumerate(self.pallets):
                if item.length > pallet.length or item.width > pallet.width:
                    self.solver.Add(self.item_pallet_vars[(i, j)] == 0)

        for i, item in enumerate(self.items):
            if item.assembled:
                for j, pallet in enumerate(self.pallets):
                    if not pallet.assembled:
                        self.solver.Add(self.item_pallet_vars[(i, j)] == 0)

        for i, item in enumerate(self.items):
            if item.bundled:
                for j, pallet in enumerate(self.pallets):
                    if pallet.type != 'BD':
                        self.solver.Add(self.item_pallet_vars[(i, j)] == 0)

        for j, pallet in enumerate(self.pallets):
            if pallet.assembled:
                self.solver.Add(sum(
                    self.item_pallet_vars[(i, j)] for i in range(len(self.items)) if self.items[i].assembled) == sum(
                    self.item_pallet_vars[(i, j)] for i in range(len(self.items)) if self.items[i].bundled) == 0)
            elif pallet.type == 'BD':
                self.solver.Add(
                    sum(self.item_pallet_vars[(i, j)] for i in range(len(self.items)) if self.items[i].bundled) == sum(
                        self.item_pallet_vars[(i, j)] for i in range(len(self.items)) if self.items[i].assembled) == 0)

        for j, pallet in enumerate(self.pallets):
            self.solver.Add(sum(
                self.item_pallet_vars[(i, j)] * (self.items[i].length * self.items[i].width * self.items[i].height)
                for i in range(len(self.items))
            ) <= pallet.max_volume)

        for j, pallet in enumerate(self.pallets):
            self.solver.Add(self.pallet_used_vars[j] * len(self.items) >= sum(
                self.item_pallet_vars[(i, j)] for i in range(len(self.items))))

        for j, pallet in enumerate(self.pallets):
            if pallet.assembled:
                for i, item in enumerate(self.items):
                    if not item.assembled:
                        self.solver.Add(self.item_pallet_vars[(i, j)] == 0)

    def set_objective(self):
        """
        Sets the objective function for the optimization problem.

        - Minimize the number of pallets used.
        - Prefer smaller pallets by adding a penalty term proportional to the pallet size.
        """
        objective = self.solver.Objective()

        for j, pallet in enumerate(self.pallets):
            penalty = pallet.size
            objective.SetCoefficient(self.pallet_used_vars[j],
                                     1 + penalty / 1000.0)  # Adjust the penalty scale as needed

        objective.SetMinimization()

    def solve(self):
        """
        Solves the optimization problem.

        Returns:
            dict: Results of the optimization including details of each pallet used, or a message indicating no optimal solution.
        """
        self.create_variables()
        self.add_constraints()
        self.set_objective()
        status = self.solver.Solve()

        if status == pywraplp.Solver.OPTIMAL:
            return self.get_results()
        else:
            return []  # no optimal solution found

    def get_results(self):
        """
        Retrieves the results of the optimization.

        Returns:
            list[dict]: Details of each pallet used, including items and calculated height, or an empty list if no pallets are used.
        """
        pallet_height = 5.5
        mockup_height = 5  # minimum item height

        results = {
            'total_pallets_used': 0,
            'pallets': []
        }

        for j, pallet in enumerate(self.pallets):
            if self.pallet_used_vars[j].solution_value() > 0.5:
                pallet_details = {
                    'type': pallet.type,
                    'size': pallet.size,
                    'length': pallet.length,
                    'width': pallet.width,
                    'height': pallet_height,  # Initialize the height with height of the pallet
                    'actual_volume': 0,
                    'weight': round(pallet.weight, 1),  # Initialize the weight with weight of the pallet
                    'assembled': False,
                    'items': []
                }

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
                        pallet_details['actual_volume'] += round(volume, 1)
                        pallet_details['weight'] += round(item.weight, 1)
                        pallet_details['assembled'] = item.assembled
                if pallet_details['actual_volume'] > 0:
                    pallet_details['height'] = round(pallet_details['actual_volume'] / (pallet.length * pallet.width),
                                                     1) + pallet_height + mockup_height

                results['total_pallets_used'] += 1
                results['pallets'].append(pallet_details)

        return results['pallets']
