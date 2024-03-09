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
    'nchain': 4,
    'nfog': 10,
    'tchain': 10.0,
    'rho': 0.3,
    'enable_network': True,
    'delta_tchain': 0.1,
    'response': "file://sample_output.json",
}

comp_model = "exer\\tesi\enhanced.mod"
simp_model = "ampl_code\\ampl_file\classic.mod"
path_data = "ampl_code\prova.dat"
VERB = False

def test_option(ampl:AMPL):
    '''
    In questo momento non conosco appieno il testing con BONMIN, la funzione è da implementare in seguito.
    '''
    #TODO
    pass

def solve_prob(ampl:AMPL, data_path:str = path_data, time_list:list = None):
    ampl.read_data(data_path)
    if(time_list):
        load_time(ampl, time_list)
    ampl.solve(verbose=VERB)
    res = ampl.solve_result_num
    if (res != 3 and res != 421):
        return False
    else:
        return True


def load_time(ampl:AMPL, time_list:list):
    ampl.get_parameter("lc").set_values(time_list)
    for ct in ampl.get_set("Ct"):
        t = ampl.get_parameter("lc").get(ct)
        for c in ampl.get_set("C").get(ct):
            ampl.get_parameter("lm").set(c, t)


def test():
    #TODO
    pass

def setup(ampl:AMPL, model:str = simp_model, solver:str = "BONMIN", time_limit = 200):
    ampl.reset()
    ampl.read(model)
    ampl.option["solver"] = solver
    #ampl.option["solver_msg"] = 0
    ampl.option["bonmin_options"] = f'''bonmin.time_limit {time_limit} 
    bonmin.algorithm B-BB bonmin.node_comparison dynamic 
    bonmin.cutoff {config["nfog"]}'''
    #ampl.option["ipopt_options"] = "max_wall_time 10"

def retrive_param():
    base = config["rho"]
    config["rho"] = 0.7
    prob = get_problem(config).dump_problem()
    max_ = prob["sensor"]["S1"]["lambda"]
    config["rho"] = 0.2
    prob = get_problem(config).dump_problem()
    min_ = prob["sensor"]["S1"]["lambda"]
    delta = round((max_ - min_)/12, 3)
    config["rho"] = base
    return max_, min_, delta

if __name__ == '__main__':
    ampl = AMPL()
    prob = get_problem(config)
    with open("ampl_code\prova.json", "w+") as f:
        js.dump(prob.dump_problem(), f, indent=2)
        f.close()
    util = AmplProbUtil()
    util.lambda_changer("ampl_code\prova.json", *retrive_param())
    time_l = util.csv_time_reader("ampl_code\prova.csv")
    util.write_prob("ampl_code\prova.json", "ampl_code\prova.dat")
    solved = False
    for i in range(25):
        print(f"solving problem N #{i}")
        setup(ampl)
        solve_prob(ampl, time_list=time_l[i])
        d1 = ampl.get_variable("On").get_values().to_dict()
        d_t = ampl.get_variable("X").get_values().to_dict()
        with open(f"ampl_code\\res_data\\res{i}.bo", "w") as f:
            res = ampl.get_objective("Active_Node").value()
            print(res)
            print(f"{ampl.solve_result_num}\t {res}", file=f)
            print(time_l[i], file=f)
            for k in d_t.keys():
                if d_t[k]:
                    print(f"{k} = {d_t[k]}", file=f)
            for k in d1.keys():
                if d1[k]:
                    print(f"{k} = {d1[k]}", file=f)