import logging

from solvers.palletsolver import Item, Pallet, PalletOptimizer
from solvers.empicalsolver import EmpiricalSolver

logger = logging.getLogger(__name__)


def pack(items):
    total_quantity = sum(item['quantity'] for item in items)

    # Go with empirical packs
    if total_quantity > 70:
        logger.debug('XXXXXX-1 Go with empirical packs')
        return create_empirical_packs(items)

    logger.debug('XXXXXX-2 Go with optimal packs')

    # Go with optimal packs
    pallets = create_optimal_packs(items)
    if len(pallets) > 0:
        return pallets

    # Fallback to empirical packs
    logger.debug('XXXXXX-3 Go with empirical packs')
    return create_empirical_packs(items)


def create_optimal_packs(items):
    """
    Creates optimal pallet packs for a given list of items.

    This function processes a list of items, generating the necessary item objects
    and pallet types. It then uses a pallet optimizer to find the optimal packing
    solution based on the given items and pallet constraints.

    Parameters:
    -----------
    items : list
        A list of dictionaries where each dictionary represents an item. The items
        should include attributes such as SKU, weight, dimensions, and other relevant
        packing constraints.

    Returns:
    --------
    list
        A list of optimized pallet packs. Each pack contains the details of the items
        included, the pallet used, and how the items are arranged within the pallet.
        The structure of the returned data depends on the implementation of the
        `PalletOptimizer` class and its `solve` method.

    Internal Functions Called:
    --------------------------
    - _create_items(items): Converts the input list of dictionaries into item objects
      required by the optimizer.
    - _create_pallets(items): Creates a list of available pallet types based on the
      items to be packed.
    - PalletOptimizer(items, pallets): Initializes the pallet optimizer with the
      created items and pallets.
    - solve(): Solves the packing problem and returns the optimized solution.

    Example:
    --------
    >>> items = [
    >>>     {'sku': 'ABC123', 'weight': 10.5, 'length': 15, 'width': 20, 'height': 5, 'bundled': False, 'quantity': 10},
    >>>     {'sku': 'DEF456', 'weight': 5.0, 'length': 10, 'width': 12, 'height': 3, 'bundled': True, 'quantity': 5}
    >>> ]
    >>> optimal_packs = _create_optimal_packs(items)
    >>> print(optimal_packs)
    [{'pallet': 'PALLET_TYPE_1', 'items': [...], 'arrangement': ...}, ...]

    Notes:
    ------
    - The function is intended for internal use, as indicated by the leading underscore in its name.
    - The actual output format and details depend on the `solve` method of the `PalletOptimizer` class.
    """
    items = create_items(items)
    pallets = create_pallets(items)
    optimizer = PalletOptimizer(items, pallets)

    return optimizer.solve()


def create_empirical_packs(items):
    empirical = EmpiricalSolver(items)

    return empirical.solve()


def create_items(items):
    return [Item(sku=x['sku'], weight=x['weight'], length=x['length'], width=x['width'],
                 height=x['height'], assembled=x['assembled'], bundled=x['bundled'])
            for x in items for _ in range(x['quantity'])]


def create_pallets(items):
    return [create_item_pallet(item) for item in items]


def create_item_pallet(item: Item):
    # Bundle item
    if item.bundled:
        return Pallet(max_volume=9650, length=98, width=10, weight=3, type='BD', assembled=False, size=96)

    # assembled item
    if item.assembled:
        if item.length <= 55:
            return Pallet(max_volume=144738, length=55, width=48, weight=68, type='PLT5', assembled=True, size=15)
        else:
            return Pallet(max_volume=131090, length=102, width=45.5, weight=78, type='PLT8', assembled=True, size=18)
    # RTA item
    if item.length <= 48:
        return Pallet(max_volume=58372, length=48, width=40.5, weight=35, type='PLT4', assembled=False, size=4)
    elif item.length <= 70:
        return Pallet(max_volume=236275, length=70, width=45, weight=70, type='PLT6', assembled=False, size=6)
    return Pallet(max_volume=176256, length=102, width=45.5, weight=78, type='PLT8', assembled=False, size=8)
