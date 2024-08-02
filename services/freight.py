from solvers.palletsolver import Item, Pallet, PalletOptimizer


def pack(items):
    items = _create_items(items)
    pallets = _create_pallets(items)

    optimizer = PalletOptimizer(items, pallets)
    result = optimizer.solve()

    return result


def _create_items(items):
    return [Item(sku=x['sku'], weight=x['weight'], length=x['length'], width=x['width'],
                 height=x['height'], assembled=x['assembled'], bundled=x['bundled'])
            for x in items for _ in range(x['quantity'])]


def _create_pallets(items):
    return [_create_item_pallet(item) for item in items]


def _create_item_pallet(item: Item):
    # Bundle item
    if item.bundled:
        return Pallet(max_volume=9600, length=96, width=10, weight=2, type='BD', assembled=False, size=96)

    # assembled item
    if item.assembled:
        if item.length <= 55:
            return Pallet(max_volume=144738, length=55, width=45, weight=55, type='PLT5', assembled=True, size=15)
        else:
            return Pallet(max_volume=131090, length=102, width=45, weight=80, type='PLT8', assembled=True, size=18)
    # RTA item
    if item.length <= 45:
        return Pallet(max_volume=58372, length=45, width=45, weight=40, type='PLT4', assembled=False, size=4)
    elif item.length <= 70:
        return Pallet(max_volume=236275, length=70, width=45, weight=70, type='PLT6', assembled=False, size=6)
    return Pallet(max_volume=176256, length=102, width=45, weight=80, type='PLT8', assembled=True, size=8)
