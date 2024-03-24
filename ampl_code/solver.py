import os
import sys
import math
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
    'nfog': 4,
    'tchain': 10.0,
    'rho': 0.3,
    'enable_network': True,
    'delta_tchain': 0.1,
    'response': "file://sample_output.json",
}


VERB = False
SOLVE_TIME = 100
STUPID = False
COMP_MODE = "ampl_code\\ampl_file\\complex.mod"
SIMP_MODEL = "ampl_code\\ampl_file\\classic.mod"
PATH_DATA = "ampl_code\\prova.dat"
PATH_WORK = "ampl_code\\example\\"


def input_param(args:argparse.Namespace):
    global VERB, PATH_WORK, SOLVE_TIME, STUPID
    VERB = args.verbose
    STUPID = args.stupid
    if args.time is not None:
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

def json_sol(ampl:AMPL) -> dict:
    sol = {}
    servicechain = {}
    for service_c in ampl.get_set("Ct"):
        s_chain = {}
        s_chain["resptime"] = ampl.get_variable("Rc").get_values().to_dict()[service_c]
        s_chain["resptime_old"] = s_chain["resptime"] - config["tchain"]
        nt = ampl.get_variable("Wc").get_values().to_dict()[service_c]
        s_chain["waittime"] = s_chain["resptime_old"] - nt
        s_chain["servicetime"] = config["tchain"]
        s_chain["networktime"] = nt
        services = {}
        for service in ampl.get_set("C").get(service_c):
            s_dict = {}
            s_dict["meanserv"] = ampl.get_parameter("Sm").get(service)
            s_dict["stddevserv"] = ampl.get_parameter("Om").get(service)
            s_dict["rate"] = 1/s_dict["meanserv"]
            s_dict["cv"] = s_dict["stddevserv"]/s_dict["meanserv"]
            s_dict["lambda"] = ampl.get_parameter("lm").get(service)
            services[service] = s_dict
        s_chain["services"] = services
        servicechain[service_c] = s_chain
    sol["servicechain"] = servicechain
    microservice = {}
    X = ampl.get_variable("X").get_values().to_dict()
    for ms in ampl.get_set("M"):
        for f in ampl.get_set("F"):
            if X[ms, f] == 1:
                microservice[ms] = f
    sol["microservice"] = microservice
    fog = {}
    for f in ampl.get_set("F"):
        fog_dict = {}
        fog_dict["rho"] = ampl.get_data("{f in F} lf[f] * Sf[f]").to_dict()[f]
        fog_dict["capacity"] = ampl.get_parameter("P").get_values().to_dict()[f]
        fog_dict["tserv"] = ampl.get_variable("Sf").get_values().to_dict()[f]
        fog_dict["stddev"] = math.sqrt(ampl.get_variable("O2f").get_values().to_dict()[f])
        fog_dict["mu"] = 1 / fog_dict["tserv"] if fog_dict["tserv"] != 0 else 0
        fog_dict["cv"] = fog_dict["stddev"] / fog_dict["tserv"] if fog_dict["tserv"] != 0 else 0
        fog_dict["lambda"] = ampl.get_variable("lf").get_values().to_dict()[f]
        fog_dict["twait"] = ampl.get_variable("Wf").get_values().to_dict()[f]
        fog[f] = fog_dict
    sol["fog"] = fog
    try:
        extra = {"obj_func" : ampl.get_objective("Migration").value()}
    except:
        extra = {"obj_func" : ampl.get_objective("Active_Node").value()}
    finally:
        sol["extra"] = extra
    network = []
    delay = ampl.get_parameter("d").get_values().to_dict()
    for f1 in ampl.get_set("F"):
        n_line = []
        for f2 in ampl.get_set("F"):
            n_line.append(delay[f1, f2])
        network.append(n_line)
    sol["network"] = network
    return sol

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
    ampl.reset()
    ampl.read(model)
    ampl.option["solver"] = solver
    #ampl.option["solver_msg"] = 0
    ampl.option["bonmin_options"] = f"bonmin.time_limit {time_limit} bonmin.node_comparison dynamic" 
    #bonmin.enable_dynamic_nlp no bonmin.number_strong_branch 10 bonmin.tree_search_strategy dfs-dive'''
    #ampl.option["ipopt_options"] = "max_wall_time 10"

def print_sol(ampl:AMPL, filename:str, time, compl:bool = False):
    d1 = ampl.get_variable("On").get_values().to_dict()
    d_t = ampl.get_variable("X").get_values().to_dict()
    with open(filename, "w") as f:
        if compl:
            res = ampl.get_objective("Migration").value()
        else:
            res = ampl.get_objective("Active_Node").value()
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
    config["rho"] = 0.65
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
    parser.add_argument('-s', '--stupid', action= "store_true", help="Enable the first horrible save")
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
    if res:
        print("Solved")
    else:
        print("Failed")
    if not res:
        sys.exit(1)
    services = ampl.get_variable("X").get_values().to_dict()
    node = ampl.get_variable("On").get_values().to_dict()
    with open(path_work_js.parent / "res0.json", "w+") as f:
        js.dump(json_sol(ampl), f, indent=2)
        f.close()
    if STUPID:
        print_sol(ampl, p / "res0.bo", time=time_l[0])
    for i in range(1, 25):
        print(f"solving problem N #{i} --> simple")
        setup(ampl, time_limit=SOLVE_TIME)
        res = solve_prob_simple(ampl, PATH_DATA, time_list=time_l[i])
        if res:
            print("Solved")
        else:
            print("Failed")
        if STUPID:
            print_sol(ampl, simple_location / f"res{i}.bo", time=time_l[i])
        with open(simple_location / f"res{i}.json", "w+") as f:
            js.dump(json_sol(ampl), f, indent=2)
            f.close()
        print(f"solving problem N #{i} --> complex")
        setup(ampl, model=COMP_MODE, time_limit=SOLVE_TIME)
        res, services, node = solve_prob_complex(ampl, data_path = PATH_DATA, time_list=time_l[i], services=services, node=node)
        if res:
            print("Solved")
        else:
            print("Failed")
        if STUPID:
            print_sol(ampl, complex_location / f"res{i}.bo", time=time_l[i], compl=True)
        with open(complex_location / f"res{i}.json", "w+") as f:
            js.dump(json_sol(ampl), f, indent=2)
            f.close()