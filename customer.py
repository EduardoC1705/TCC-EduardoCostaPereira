from positionalentity import PositionalEntity

class Customer(PositionalEntity):
    def __init__(self, id, x, y, d, q):
        super().__init__(id, x, y)
        self.service_duration = int(d)
        self.demand = int(q)
    
    def get_demand(self):
        return self.demand    
    
    def get_service_duration(self):
        return self.service_duration
    

    def __str__(self):
        return "Customer" + super().__str__() + f"Service Duration: {self.service_duration}\nDemand: {self.demand}\n"

