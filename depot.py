from positionalentity import PositionalEntity

class Depot(PositionalEntity):
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
    
    def __str__(self):
        return "Depot"+super().__str__()