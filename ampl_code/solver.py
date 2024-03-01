from amplpy import AMPL
import os

path_model = "exer\\tesi\enhanced.mod"
path_data = "exer\\tesi\ex1.dat"

def solve_prob():
    #TODO
    pass

def load_time():
    #TODO
    pass


def test():
    #TODO
    pass

def setup(model:str = path_model, solver:str = "BONMIN"):
    ampl = AMPL()
    ampl.read(model)
    ampl.option["solver"] = solver
    return ampl


if __name__ == '__main__':
    ampl = setup()
    ampl.read_data(path_data)
    ampl.solve()
    print(ampl.get_variable("X").get_values().to_dict())
    