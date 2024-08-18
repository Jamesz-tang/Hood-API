class EmpiricalSolver:
    def __init__(self, items, pallet_length=48, pallet_width=40.5, pallet_height=48, pallet_max_weight=518):
        """
        Initialize the EmpiricalSolver with a list of items and pallet constraints.

        Parameters:
        -----------
        items : list
            A list of dictionaries where each dictionary represents an item.
            Each item should have the following keys:
            - sku (str): The SKU of the item.
            - weight (float): The weight of the item.
            - length (float): The length of the item.
            - width (float): The width of the item.
            - height (float): The height of the item.
            - bundled (bool): A flag indicating whether the item is bundled.
            - quantity (int): The quantity of the item.

        pallet_length : float, optional
            The length of the pallet (default is 48).

        pallet_width : float, optional
            The width of the pallet (default is 40.5).

        pallet_max_weight : float, optional
            The maximum weight the pallet can hold (default is 518 LB).
        """
        self.items = items
        self.pallet_length = pallet_length
        self.pallet_width = pallet_width
        self.pallet_height = pallet_height
        self.pallet_max_weight = pallet_max_weight

    def solve(self):
        """
        Solve the palletization problem by creating the optimal number of pallets.

        Returns:
        --------
        list
            A list of pallets with the items optimally distributed.
        """
        return self._create_pallets()

    def _create_pallets(self):
        """
        Create pallets by distributing items based on the weight constraint.

        Returns:
        --------
        list
            A list of pallets where each pallet is a dictionary containing:
            - pallet_number (int): The identifier for the pallet.
            - items (list): A list of items placed on the pallet.
            - total_weight (float): The total weight of items on the pallet.
        """
        pallets = []
        assembled = contains_assembled_items(self.items)
        actual_volume = round(self.pallet_length * self.pallet_width * self.pallet_height, 1)
        total_cabinet_weight = total_weight_not_bundled(self.items)
        pallet_count = total_cabinet_weight // self.pallet_max_weight

        # Append pallet
        for i in range(pallet_count):
            pallets.append({
                'type': 'PLT4',
                'size': 4,
                'length': self.pallet_length,
                'width': self.pallet_width,
                'height': self.pallet_height,
                'actual_volume': actual_volume,
                'weight': self.pallet_max_weight,
                'assembled': assembled,
                'items': []
            })

        # The last pallet
        remaining_weight = round(total_cabinet_weight - self.pallet_max_weight * pallet_count, 1)
        pallets.append({
            'type': 'PLT4',
            'size': 4,
            'length': self.pallet_length,
            'width': self.pallet_width,
            'height': round(self.pallet_height * (remaining_weight/self.pallet_max_weight), 1),
            'actual_volume': actual_volume,
            'weight': remaining_weight,
            'assembled': assembled,
            'items': []
        })

        # Handle bundle items
        # Pallet(max_volume=9650, length=98, width=10, weight=3, type='BD', assembled=False, size=96)
        bundle_volume = round(98 * 10 * 10)
        for item in self.items:
            if item['bundled']:
                for _ in range(item['quantity']):
                    pallets.append({
                        'type': 'BD',
                        'size': 96,
                        'length': 98,
                        'width': 10,
                        'height': 10,
                        'actual_volume': bundle_volume,
                        'weight': item['weight'] + 3,
                        'assembled': False,
                        'items': []
                    })

        return pallets


def contains_assembled_items(items):
    """
    Determines if the list of items contains any assembled items.

    This function checks if any of the items in the provided list have the 'assembled'
    attribute set to True.

    Parameters:
    -----------
    items : list
        A list of dictionaries where each dictionary represents an item.
        Each item should have the following keys:
        - sku (str): The SKU of the item.
        - weight (float): The weight of the item.
        - length (float): The length of the item.
        - width (float): The width of the item.
        - height (float): The height of the item.
        - assembled (bool): A flag indicating whether the item is assembled.
        - quantity (int): The quantity of the item.

    Returns:
    --------
    bool
        True if there is at least one assembled item in the list, False otherwise.

    """
    return any(item.get('assembled', False) for item in items)


def total_weight_not_bundled(items):
    """
    Computes the total weight of items that are not bundled.

    This function iterates through the list of items and sums up the total weight of
    the items that are not bundled.

    Parameters:
    -----------
    items : list
        A list of dictionaries where each dictionary represents an item.
        Each item should have the following keys:
        - sku (str): The SKU of the item.
        - weight (float): The weight of the item.
        - length (float): The length of the item.
        - width (float): The width of the item.
        - height (float): The height of the item.
        - bundled (bool): A flag indicating whether the item is bundled.
        - quantity (int): The quantity of the item.

    Returns:
    --------
    float
        The total weight of items that are not bundled.
    """
    return sum(item['weight'] * item['quantity'] for item in items if not item['bundled'])
