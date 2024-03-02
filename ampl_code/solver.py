from amplpy import AMPL
from gafog.fog_problem.problem import Problem
from gafog.problem_gen.genproblem import get_problem
import json as js
import os
import sys
from ampl_code.AmplProbUtil import AmplProbUtil

config = {
    'nchain_fog': 0.4,
    'nsrv_chain': 5,
    'nchain': 5,
    'nfog': 5,
    'tchain': 10.0,
    'rho': 0.7,
    'enable_network': True,
    'delta_tchain': 0.05,
    'response': "file://sample_output.json",
}

path_tesi_model = "exer\\tesi\enhanced.mod"
path_model = "ampl_code\\ampl_file\classic.mod"
path_data = "exer\\tesi\mako.dat"

def test_option(ampl:AMPL):
    #TODO
    return

def solve_prob(ampl:AMPL, data_path:str = path_data):
    ampl.read_data(data_path)
    ampl.solve()
    res = ampl.solve_result_num
    if (res != 3 and res != 421):
        pass

def load_time():
    #TODO
    pass


def test():
    #TODO
    pass

def setup(ampl:AMPL, model:str = path_model, solver:str = "BONMIN"):
    ampl.read(model)
    ampl.option["solver"] = solver
    #ampl.option["solver_msg"] = 0
    ampl.option["bonmin_options"] = "bonmin.time_limit 20 print_level 0 bonmin.bb_log_level 0"
    #ampl.option["ipopt_options"] = "max_wall_time 10"


if __name__ == '__main__':
    ampl = AMPL()
    prob = get_problem(config)
    with open("ampl_code\prova.json", "w+") as f:
        js.dump(prob.dump_problem(), f, indent=2)
        f.close()
    util = AmplProbUtil()
    util.write_prob("ampl_code\prova.json", "ampl_code\prova.dat")
    setup(ampl, model=path_tesi_model)
    ampl.read_data("ampl_code\prova.dat")
    ampl.solve(verbose=False)
    d = ampl.get_variable("X").get_values().to_dict()
    print(ampl.solve_result_num)
    ampl.reset()
    setup(ampl)
    ampl.read_data("ampl_code\prova.dat")
    ampl.solve(verbose=False)
    print(ampl.solve_result_num)
    d1 = ampl.get_variable("On").get_values().to_dict()
    d_t = ampl.get_variable("X").get_values().to_dict()
    with open("res.bo", "w") as f:
        for k in d_t.keys():
            if d[k]:
                print(f"{k} = {d_t[k]}", file=f)
        for k in d_t.keys():
            if d[k]:
                print(f"{k} = {d[k]}", file=f)
        for k in d1.keys():
            if d1[k]:
                print(f"{k} = {d1[k]}", file=f)