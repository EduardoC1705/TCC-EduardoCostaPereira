import math
class PositionalEntity:
    instances = {}

    def __init__(self, id, x, y):
        self.id = int(id)
        self.x = float(x)
        self.y = float(y)

        PositionalEntity.instances[self.id] = self
    
    def distance(self, pentity):
        return math.sqrt( (self.x - pentity.x)*(self.x - pentity.x) + (self.y - pentity.y)*(self.y - pentity.y))

    
    def __str__(self):
        return f"ID: {self.id}\nX: {self.x}\nY: {self.y}\n"