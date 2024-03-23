import os
import sys
import argparse
import json as js
from pathlib import Path
from amplpy import AMPL
from gafog.fog_problem.problem import Problem
from gafog.problem_gen.genproblem import get_problem
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


VERB = False
SOLVE_TIME = 100
COMP_MODE = "ampl_code\\ampl_file\\complex.mod"
SIMP_MODEL = "ampl_code\\ampl_file\\classic.mod"
PATH_DATA = "ampl_code\\prova.dat"
PATH_WORK = "ampl_code\\example\\"


def input_param(args:argparse.Namespace):
    global VERB, PATH_WORK, SOLVE_TIME
    VERB = args.verbose
    SOLVE_TIME = args.time
    if args.destination is not None:
        PATH_WORK = str.rstrip(args.destination,"\\/") + "\\"
    try:
        p = Path(PATH_WORK)
    except:
        print("incorrect path format, default path set")
        PATH_WORK = "ampl_code\\example\\"
        p = Path(PATH_WORK)
    return p

def dir_creation(p:Path):
    simple_location = p / "simple"
    complex_location = p / "complex"
    try:
        Path.mkdir(p, parents=True, exist_ok=True)
        Path.mkdir(simple_location, parents=True, exist_ok=True)
        Path.mkdir(complex_location, parents=True, exist_ok=True)
    except FileExistsError:
        print("One of the necessary path already exists and is a file, default option will be set")
        global PATH_WORK
        PATH_WORK = "ampl_code\\example\\"
        p = Path(PATH_WORK)
        simple_location = p / "simple"
        complex_location = p / "complex"
        Path.mkdir(p, parents=True, exist_ok=True)
        Path.mkdir(simple_location, parents=True, exist_ok=True)
        Path.mkdir(complex_location, parents=True, exist_ok=True)
    return p, simple_location, complex_location

def test_option(ampl:AMPL):
    '''
    In questo momento non conosco appieno il testing con BONMIN, la funzione è da implementare in seguito.
    '''
    #TODO
    pass

def solve_prob_simple(ampl:AMPL, data_path:str = PATH_DATA, time_list:list = None, ret = False):
    ampl.read_data(data_path)
    if(time_list):
        load_time(ampl, time_list)
    ampl.solve(verbose=VERB)
    res = ampl.solve_result_num
    if (res != 3 and res != 421):
        return False
    else:
        return True

def solve_prob_complex(ampl:AMPL, data_path:str = PATH_DATA, time_list:list = None, node:dict = None, services:dict = None):
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

def setup(ampl:AMPL, model:str = SIMP_MODEL, solver:str = "BONMIN", time_limit = SOLVE_TIME):
    print(time_limit)
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
    '''
    Un primo tentativo, abbastanza brutto ma funzionale di ottenere i parametri di variazione dei lambda.
    '''
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
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action= "store_true", help="Verbose output, display solver's verbose output")
    parser.add_argument('-d', '--destination', help = "specify the dir where files will be saved")
    parser.add_argument('-t', '--time', help=f"set the maximum solving time (s) for each problem, default {SOLVE_TIME}", type=int)
    p = input_param(parser.parse_args())
    ampl = AMPL()
    p, simple_location, complex_location = dir_creation(p)
    prob = get_problem(config)
    path_work_js = p / "prob.json"
    with open(path_work_js, "w+") as f:
        js.dump(prob.dump_problem(), f, indent=2)
        f.close()
    util = AmplProbUtil()
    csv_path = util.lambda_changer(path_work_js.__str__(), *retrive_param())
    time_l = util.csv_time_reader(csv_path)
    PATH_DATA = PATH_WORK + "prova.dat"
    util.write_prob(path_work_js, PATH_DATA)
    print(f"solving problem N #0 --> simple")
    setup(ampl, time_limit=SOLVE_TIME)
    res = solve_prob_simple(ampl, PATH_DATA, time_list=time_l[0])
    services = ampl.get_variable("X").get_values().to_dict()
    node = ampl.get_variable("On").get_values().to_dict()
    print_sol(ampl, p / "res0.bo", time=time_l[0])
    for i in range(1, 25):
        print(f"solving problem N #{i} --> simple")
        setup(ampl, time_limit=SOLVE_TIME)
        res = solve_prob_simple(ampl, PATH_DATA, time_list=time_l[i])
        print_sol(ampl, simple_location / f"res{i}.bo", time=time_l[i])
        print(f"solving problem N #{i} --> complex")
        setup(ampl, model=COMP_MODE, time_limit=SOLVE_TIME)
        res, services, node = solve_prob_complex(ampl, data_path = PATH_DATA, time_list=time_l[i], services=services, node=node)
        print_sol(ampl, complex_location / f"res{i}.bo", time=time_l[i], compl=True)