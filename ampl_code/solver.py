from amplpy import AMPL
from gafog.fog_problem.problem import Problem
from gafog.problem_gen.genproblem import get_problem
import json as js
import os
import sys
from ampl_code.AmplProbUtil import AmplProbUtil

config = {
    'nchain_fog': 0.4,
    'nsrv_chain': 2,
    'nchain': 2,
    'nfog': 3,
    'tchain': 10.0,
    'rho': 0.3,
    'enable_network': True,
    'delta_tchain': 0.1,
    'response': "file://sample_output.json",
}

comp_model = "ampl_code\\ampl_file\complex.mod"
simp_model = "ampl_code\\ampl_file\classic.mod"
path_data = "ampl_code\prova.dat"
VERB = True

def test_option(ampl:AMPL):
    '''
    In questo momento non conosco appieno il testing con BONMIN, la funzione è da implementare in seguito.
    '''
    #TODO
    pass

def solve_prob_simple(ampl:AMPL, data_path:str = path_data, time_list:list = None, ret = False):
    ampl.read_data(data_path)
    if(time_list):
        load_time(ampl, time_list)
    ampl.solve(verbose=VERB)
    res = ampl.solve_result_num
    if (res != 3 and res != 421):
        return False
    else:
        return True

def solve_prob_complex(ampl:AMPL, data_path:str = path_data, time_list:list = None, node:dict = None, services:dict = None):
    ampl.read_data(data_path)
    if(time_list):
        load_time(ampl, time_list)
    if not node:
        node = [0 for i in range(config["nfog"])]
    if not services:
        services = [0 for i in range(config["nchain"] * config["nsrv_chain"] * config["nfog"])]
    ampl.get_parameter("Xt").set_values(services)
    ampl.get_parameter("Ot").set_values(node)
    ampl.solve(verbose=VERB)
    res = ampl.solve_result_num
    if (res != 3 and res != 421):
        return False, services, node
    else:
        return True, ampl.get_variable("X").get_values().to_dict(), ampl.get_variable("On").get_values().to_dict()

def load_time(ampl:AMPL, time_list:list):
    ampl.get_parameter("lc").set_values(time_list)
    for ct in ampl.get_set("Ct"):
        t = ampl.get_parameter("lc").get(ct)
        for c in ampl.get_set("C").get(ct):
            ampl.get_parameter("lm").set(c, t)

def test():
    #TODO
    pass

def setup(ampl:AMPL, model:str = simp_model, solver:str = "BONMIN", time_limit = 100):
    ampl.reset()
    ampl.read(model)
    ampl.option["solver"] = solver
    #ampl.option["solver_msg"] = 0
    ampl.option["bonmin_options"] = f'''bonmin.time_limit {time_limit} 
    bonmin.algorithm B-BB bonmin.node_comparison dynamic'''
    #ampl.option["ipopt_options"] = "max_wall_time 10"

def print_sol(ampl:AMPL, filename:str, time, compl:bool = False):
    d1 = ampl.get_variable("On").get_values().to_dict()
    d_t = ampl.get_variable("X").get_values().to_dict()
    with open(filename, "w") as f:
        if compl:
            res = ampl.get_objective("Migration").value()
        else:
            res = ampl.get_objective("Active_Node").value()
        print(res)
        print(f"{ampl.solve_result_num}\t {res}", file=f)
        print(time, file=f)
        for k in d_t.keys():
            if d_t[k]:
                print(f"{k} = {d_t[k]}", file=f)
        for k in d1.keys():
            if d1[k]:
                print(f"{k} = {d1[k]}", file=f)

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
    path_work = "ampl_code\\example\\"
    simple_location = path_work + "simple"
    complex_location = path_work + "complex"
    if not os.path.isdir(path_work):
        os.mkdir(path_work)
        os.mkdir(simple_location)
        os.mkdir(complex_location)
    prob = get_problem(config)
    path_work_js = path_work + "prova.json"
    with open(path_work_js, "w+") as f:
        js.dump(prob.dump_problem(), f, indent=2)
        f.close()
    util = AmplProbUtil()
    util.lambda_changer(path_work_js, *retrive_param())
    time_l = util.csv_time_reader(path_work + "prova.csv")
    path_data = path_work + "prova.dat"
    util.write_prob(path_work_js, path_data)
    print(f"solving problem N #0 --> simple")
    setup(ampl)
    res = solve_prob_simple(ampl, path_data, time_list=time_l[0])
    services = ampl.get_variable("X").get_values().to_dict()
    print(services)
    node = ampl.get_variable("On").get_values().to_dict()
    print_sol(ampl, f"{path_work}\\res0.bo", time=time_l[0])
    for i in range(1, 25):
        print(f"solving problem N #{i} --> simple")
        setup(ampl)
        res = solve_prob_simple(ampl, path_data, time_list=time_l[i])
        print_sol(ampl, f"{simple_location}\\res{i}.bo", time=time_l[i])
        print(f"solving problem N #{i} --> complex")
        setup(ampl, model=comp_model)
        res, services, node = solve_prob_complex(ampl, data_path = path_data, time_list=time_l[i], services=services, node=node)
        print_sol(ampl, f"{complex_location}\\res{i}.bo", time=time_l[i], compl=True)