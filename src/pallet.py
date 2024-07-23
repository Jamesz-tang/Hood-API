class Pallet:
    def __init__(self, type, length, width, max_height, weight, assembled):
        self.type = type
        self.length = length
        self.width = width
        self.max_height = max_height
        self.weight = weight
        self.assembled = assembled

    def __repr__(self):
        return f"Pallet(type={self.type}, dimensions={self.length}x{self.width}x{self.max_height})"
