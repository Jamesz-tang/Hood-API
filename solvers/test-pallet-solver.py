import json

from palletsolver import Item, Pallet, PalletOptimizer

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
    Pallet(max_volume=9250, length=25, width=25, weight=60, type='PLT8', assembled=False, size=88),

    Pallet(max_volume=62500, length=25, width=25, weight=60, type='PLT8', assembled=True, size=8),

    Pallet(max_volume=5760, length=96, width=10, weight=70, type='BD', assembled=False, size=6),
    Pallet(max_volume=5760, length=96, width=10, weight=70, type='BD', assembled=False, size=6),

]

# Example usage
if __name__ == '__main__':
    optimizer = PalletOptimizer(items, pallets)
    result = optimizer.solve()
    json_data = json.dumps(result, default=lambda o: o.__dict__, indent=2)
    print(json_data)
