class Item:
    def __init__(self, weight, length, width, height, assembled, bundled):
        self.weight = weight
        self.length = length
        self.width = width
        self.height = height
        self.assembled = assembled
        self.bundled = bundled

    def __repr__(self):
        return f"Item(weight={self.weight}, length={self.length}, width={self.width}, height={self.height})"
