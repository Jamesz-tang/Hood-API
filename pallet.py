class Pallet:
    def __init__(self):
        self.pallet_dict = {
            "rta": {
                "PLT8": {
                    "pallet_type": "PLT8",
                    "max_height": 43.5,
                    "weight": 40,
                    "length": 102,
                    "width": 45,
                    "height": 4.5,
                },
                "PLT6": {
                    "pallet_type": "PLT6",
                    "max_height": 70.5,
                    "weight": 40,
                    "length": 70,
                    "width": 45,
                    "height": 4.5,
                },
                "PLT4": {
                    "pallet_type": "PLT4",
                    "max_height": 70.5,
                    "weight": 40,
                    "length": 45,
                    "width": 45,
                    "height": 4.5,
                },
                "BD": {
                    "pallet_type": "BD",
                    "max_height": 10,
                    "weight": 2,
                    "length": 96,
                    "width": 10,
                    "height": 10,
                }
            },
            "assembled": {
                "PLT8": {
                    "pallet_type": "PLT8",
                    "max_height": 37.5,
                    "weight": 40,
                    "length": 102,
                    "width": 45,
                    "height": 4.5,
                },
                "PLT5": {
                    "pallet_type": "PLT5",
                    "max_height": 81.5,
                    "weight": 1,
                    "length": 55,
                    "width": 45,
                    "height": 10,
                }
            }
        }

    def get_pallet(self, assembled: bool, bundled: bool, pallet_name: str):

        if bundled:
            pallet = self.pallet_dict["rta"]['BD']
        elif assembled:
            pallet = self.pallet_dict["assembled"][pallet_name]
        else:
            pallet = self.pallet_dict["rta"][pallet_name]

        return pallet


# Example usage
pallet_type = Pallet()
print(pallet_type.get_pallet(False, True, 'BD'))
print(pallet_type.get_pallet(True, False, 'PLT8'))
print(pallet_type.get_pallet(True, False, 'PLT5'))
print(pallet_type.get_pallet(False, False, 'PLT8'))
print(pallet_type.get_pallet(False, False, 'PLT6'))
print(pallet_type.get_pallet(False, False, 'PLT4'))
