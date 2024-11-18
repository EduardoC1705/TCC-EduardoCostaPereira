import re
from positionalentity import PositionalEntity
from customer import Customer
from depot import Depot
from pulp import LpProblem, LpVariable, lpSum, LpMinimize, LpInteger
from itertools import product

def build_three_index(filename):
    instance = MDVRP(filename)
    mdvrp_model = LpProblem("MDVRP", LpMinimize)
    Vc = {i for i in range(1, instance.get_number_of_customers()+1)}
    Vd = {i for i in range(instance.get_number_of_customers()+1, instance.get_number_of_customers()+instance.get_number_of_depots()+1)}
    V = Vc.union(Vd)
    K = {i for i in range(1, instance.get_number_of_depots()*instance.get_number_of_vehicles()+1)}
    x = LpVariable.dicts("x", indices=product(V, V, K), cat="Binary")
    u = LpVariable.dicts("u", indices=Vc, lowBound=1, upBound=len(Vc),cat=LpInteger)
    # Funcao Objetivo
    mdvrp_model += lpSum(x[i, j, k] * instance.distance(i, j)
                for (i, j, k) in product(V, V, K))
    # Restricao 16
    for j in Vc:
        mdvrp_model += lpSum(x[i,j,k] for (i, k) in product(V, K)) == 1
    # Restricao 17 
    for i in Vc:
        mdvrp_model += lpSum(x[i,j,k] for (j, k) in product(V, K)) == 1
    
    # Restricao 18
    for k in K:
        for h in V:
            #mdvrp_model += lpSum(x[i,h,k] for i in V) - lpSum(x[h,j,k] for j in V) == 0
            mdvrp_model += lpSum(x[i,h,k]-x[h,i,k] for i in V) == 0
    
    # Restricao 19
    for k in K:
        mdvrp_model += lpSum(x[i,j,k]*instance.get_demand_of_a_customer(i-1) for (i,j) in product(Vc, V)) <= instance.get_max_load_of_a_vehicle()
    
    # Restricao 20
    if instance.get_max_time_of_a_route() > 0:
        for k in K:
            mdvrp_model += lpSum( x[i,j,k]*instance.get_service_duration_of_a_customer(i-1) for (i,j) in product(Vc,V)) + lpSum(x[i,j,k]*instance.distance(i,j) for (i,j) in product(V,V)) <= instance.get_max_time_of_a_route()

    # Restricao 21
    for i in Vd:
        depot_index = i-min(Vd)
        for k in range( instance.get_number_of_vehicles()*depot_index + 1, instance.get_number_of_vehicles()*(depot_index+1)+1):
            mdvrp_model += lpSum(x[i,j,k] for j in Vc) <= 1
    # Restricao 22
    for j in Vd:
        depot_index = j-min(Vd)
        for k in range( instance.get_number_of_vehicles()*depot_index + 1, instance.get_number_of_vehicles()*(depot_index+1)+1):
            mdvrp_model += lpSum(x[i,j,k] for i in Vc) <= 1
    # Restricao 23
    for j in Vd:
        depot_index = j-min(Vd)
        for k in range(1, instance.get_number_of_depots()*instance.get_number_of_vehicles()+1):
            if k < (instance.get_number_of_vehicles()*depot_index + 1) or k > instance.get_number_of_vehicles()*(depot_index+1):
                mdvrp_model += lpSum(x[i,j,k] for i in Vc) == 0

    # Restricao 24
    for i in Vd:
        depot_index = i-min(Vd)
        for k in range(1, instance.get_number_of_depots()*instance.get_number_of_vehicles()+1):
            if k < (instance.get_number_of_vehicles()*depot_index + 1) or k > instance.get_number_of_vehicles()*(depot_index+1):
                mdvrp_model += lpSum(x[i,j,k] for j in Vc) == 0
    
    # Restricao 25
    n = len(Vc)
    for k in K:
        for i in Vc:
            for j in Vc:
                if (i != j):
                    mdvrp_model += u[i] - u[j] + n * x[i,j,k] <= n-1
    
    #restricao Extra
    for k in K:
        for i in V:
            mdvrp_model += x[i,i,k] == 0

    return mdvrp_model


class MDVRP:
    def __init__(self, filename):
        PositionalEntity.instances.clear()
        with open(filename, "r") as file:
            # linha 1
            line = file.readline().strip()
            params = line.split()
            self.number_of_vehicles = int(params[1])
            self.number_of_customers = int(params[2])
            self.number_of_depots = int(params[3])
            # linha 2
            line = file.readline().strip()
            params = line.split()
            self.max_time_of_a_route = int(params[0])
            self.max_load_of_a_vehicle = int(params[1])
            for _ in range(self.number_of_depots-1):
                next(file)
            # customers
            self.customers = []
            for i in range(self.number_of_customers):
                line = file.readline().strip()
                line = re.sub(r'\s+', ' ', line)
                params = line.split()
                self.customers.append(Customer(params[0], params[1], params[2], params[3], params[4]))
            #depots
            self.depots = []
            for i in range(self.number_of_depots):
                line = file.readline().strip()
                line = re.sub(r'\s+', ' ', line)
                params = line.split()
                self.customers.append(Depot(params[0], params[1], params[2]))

    def build_three_index(self):
        mdvrp_model = LpProblem("MDVRP", LpMinimize)
        Vc = {i for i in range(1, self.number_of_customers+1)}
        Vd = {i for i in range(self.number_of_customers+1, self.number_of_customers+self.number_of_depots+1)}
        V = Vc.union(Vd)
        K = {i for i in range(1, self.number_of_depots*self.number_of_vehicles+1)}
        x = LpVariable.dicts("x", indices=product(V, V, K), cat="Binary")
        u = LpVariable.dicts("u", indices=Vc, lowBound=1, upBound=len(Vc),cat=LpInteger)
        # Funcao Objetivo
        mdvrp_model += lpSum(x[i, j, k] * self.distance(i, j)
                   for (i, j, k) in product(V, V, K))
        # Restricao 16
        for j in Vc:
            mdvrp_model += lpSum(x[i,j,k] for (i, k) in product(V, K)) == 1
        # Restricao 17 
        for i in Vc:
            mdvrp_model += lpSum(x[i,j,k] for (j, k) in product(V, K)) == 1
        
        # Restricao 18
        for k in K:
            for h in V:
                #mdvrp_model += lpSum(x[i,h,k] for i in V) - lpSum(x[h,j,k] for j in V) == 0
                mdvrp_model += lpSum(x[i,h,k]-x[h,i,k] for i in V) == 0
        
        # Restricao 19
        for k in K:
            mdvrp_model += lpSum(x[i,j,k]*self.customers[i-1].get_demand() for (i,j) in product(Vc, V)) <= self.max_load_of_a_vehicle
        
        # Restricao 20
        if self.max_time_of_a_route > 0:
            for k in K:
                mdvrp_model += lpSum( x[i,j,k]*self.customers[i-1].get_service_duration() for (i,j) in product(Vc,V)) + lpSum(x[i,j,k]*self.distance(i,j) for (i,j) in product(V,V)) <= self.max_time_of_a_route
    
        # Restricao 21
        for i in Vd:
            depot_index = i-min(Vd)
            for k in range( self.number_of_vehicles*depot_index + 1, self.number_of_vehicles*(depot_index+1)+1):
                mdvrp_model += lpSum(x[i,j,k] for j in Vc) <= 1
        # Restricao 22
        for j in Vd:
            depot_index = j-min(Vd)
            for k in range( self.number_of_vehicles*depot_index + 1, self.number_of_vehicles*(depot_index+1)+1):
                mdvrp_model += lpSum(x[i,j,k] for i in Vc) <= 1
        # Restricao 23
        for j in Vd:
            depot_index = j-min(Vd)
            for k in range(1, self.number_of_depots*self.number_of_vehicles+1):
                if k < (self.number_of_vehicles*depot_index + 1) or k > self.number_of_vehicles*(depot_index+1):
                    mdvrp_model += lpSum(x[i,j,k] for i in Vc) == 0

        # Restricao 24
        for i in Vd:
            depot_index = i-min(Vd)
            for k in range(1, self.number_of_depots*self.number_of_vehicles+1):
                if k < (self.number_of_vehicles*depot_index + 1) or k > self.number_of_vehicles*(depot_index+1):
                    mdvrp_model += lpSum(x[i,j,k] for j in Vc) == 0
        
        # Restricao 25
        n = len(Vc)
        for k in K:
            for i in Vc:
                for j in Vc:
                    if (i != j):
                        mdvrp_model += u[i] - u[j] + n * x[i,j,k] <= n-1
        
        #restricao Extra
        for k in K:
            for i in V:
                mdvrp_model += x[i,i,k] == 0
        mdvrp_model.solve()
        with open('saida.txt', 'w') as arquivo:
            for (i,j,k) in product(V,V,K):
                print(f"x[{i},{j},{k}] = {x[i,j,k].value()}", file=arquivo)

    def distance(self, i, j):
        #Mudar o metodo get para ser um metodo de classe, design melhor de codigo
        instance1 = PositionalEntity.instances.get(i)
        if instance1:
            instance2 = PositionalEntity.instances.get(j)
            if instance2:
                return instance1.distance(instance2)
            else:
                print(f"POSITIONALENTITY-OBJECT NOT FOUND-ID={i}")
        else:
            print(f"POSITIONALENTITY-OBJECT NOT FOUND-ID={i}")
    
    def get_max_load_of_a_vehicle(self):
        return self.max_load_of_a_vehicle
    
    def get_max_time_of_a_route(self):
        return self.max_time_of_a_route
    
    def get_demand_of_a_customer(self, index):
        return self.customers[index].get_demand()
    
    def get_service_duration_of_a_customer(self, index):
        return self.customers[index].get_service_duration()
    
    def get_number_of_customers(self):
        return self.number_of_customers
    
    def get_number_of_depots(self):
        return self.number_of_depots
    
    def get_number_of_vehicles(self):
        return self.number_of_vehicles

    def __str__(self):
        res = ""
        res += f"Number of Vehicles: {self.number_of_vehicles}\n"
        res += f"Number of Customers: {self.number_of_customers}\n"
        res += f"Number of Depots: {self.number_of_depots}\n"
        res += f"Maximum Time of a route: {self.max_time_of_a_route}\n"
        res += f"Max load of a vehicle: {self.max_load_of_a_vehicle}\n"
        for i in range(len(self.customers)):
            res += str(self.customers[i])
        for i in range(len(self.depots)):
            res += str(self.depots[i])
        return res

#Caminho do arquivo com a descrição da instância
model = build_three_index("C-mdvrp/p02")
# O solver pode ser escolhido no método solve()
model.solve()

    
                


