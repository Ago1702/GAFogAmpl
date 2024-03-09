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
    'nfog': 10,
    'tchain': 10.0,
    'rho': 0.5,
    'enable_network': True,
    'delta_tchain': 0.1,
    'response': "file://sample_output.json",
}

comp_model = "exer\\tesi\enhanced.mod"
simp_model = "ampl_code\\ampl_file\classic.mod"
path_data = "ampl_code\prova.dat"
VERB = True

def test_option(ampl:AMPL):
    '''
    In questo momento non conosco appieno il testing con BONMIN, la funzione è da implementare in seguito.
    '''
    #TODO
    pass

def solve_prob(ampl:AMPL, data_path:str = path_data):
    ampl.read_data(data_path)
    ampl.solve(verbose=VERB)
    res = ampl.solve_result_num
    if (res != 3 and res != 421):
        return False
    else:
        return True


def load_time():
    #TODO
    pass


def test():
    #TODO
    pass

def setup(ampl:AMPL, model:str = simp_model, solver:str = "BONMIN", time_limit = 200):
    ampl.reset()
    ampl.read(model)
    ampl.option["solver"] = solver
    #ampl.option["solver_msg"] = 0
    ampl.option["bonmin_options"] = f"bonmin.time_limit {time_limit} print_level 0 bonmin.bb_log_level 0"
    #ampl.option["ipopt_options"] = "max_wall_time 10"

def retrive_param():
    base = config["rho"]
    config["rho"] = 0.8
    prob = get_problem(config).dump_problem()
    max_ = prob["sensor"]["S1"]["lambda"]
    config["rho"] = 0.3
    prob = get_problem(config).dump_problem()
    min_ = prob["sensor"]["S1"]["lambda"]
    delta = round((max_ - min_)/8, 3)
    config["rho"] = base
    return max_, min_, delta



if __name__ == '__main__':
    ampl = AMPL()
    max_, min_, delta = retrive_param()
    prob = get_problem(config)
    with open("ampl_code\prova.json", "w+") as f:
        js.dump(prob.dump_problem(), f, indent=2)
        f.close()
    util = AmplProbUtil()
    util.lambda_changer("ampl_code\prova.json", max_, min_, delta)
    util.write_prob("ampl_code\prova.json", "ampl_code\prova.dat")

    solved = False
    i = 0
    while(not solved):
        setup(ampl)
        test_option(ampl)
        solved = solve_prob(ampl)
        if i == 5:
            break
    d1 = ampl.get_variable("On").get_values().to_dict()
    d_t = ampl.get_variable("X").get_values().to_dict()
    print(ampl.solve_result_num)
    ampl.reset()
    sys.exit(1)
    setup(ampl)
    with open("res.bo", "w") as f:
        for k in d_t.keys():
            if d_t[k]:
                print(f"{k} = {d_t[k]}", file=f)
        for k in d1.keys():
            if d1[k]:
                print(f"{k} = {d1[k]}", file=f)