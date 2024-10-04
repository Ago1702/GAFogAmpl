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
import itertools

config = {
    'nchain_fog': 0.4,
    'nsrv_chain': 4,
    'nchain': 4,
    'nfog': 8,
    'tchain': 10.0,
    'rho': 0.3,
    'enable_network': True,
    'delta_tchain': 0.1,
    'response': "file://sample_output.json",
}


VERB = False
SOLVE_TIME = 350
STUPID = False
COMP_MODE = "ampl_code/ampl_file/complex.mod"
SIMP_MODEL = "ampl_code/ampl_file/classic.mod"
PATH_DATA = "ampl_code/prova.dat"
PATH_WORK = "ampl_code/example/"
ALT = False

#TODO modificare il json inserendo le migrazioni e gli spegnimenti


def input_param(args:argparse.Namespace):
    #TODO aggiungere un metodo di input della configurazione

    global VERB, PATH_WORK, SOLVE_TIME, STUPID, ALT
    VERB = args.verbose
    STUPID = args.stupid
    ALT = args.constant
    if args.time is not None:
        SOLVE_TIME = args.time
    if args.destination is not None:
        PATH_WORK = str.rstrip(args.destination,"\\/") + "/"
    try:
        p = Path(PATH_WORK)
    except:
        print("incorrect path format, default path set", flush=True)
        PATH_WORK = "ampl_code/example/"
        p = Path(PATH_WORK)
    return p

def dir_creation(p:Path):
    simple_location = p / "simple"
    complex_location = p / "complex"
    global PATH_WORK
    try:
        PATH_WORK = p.__str__() + "/"
        Path.mkdir(p, parents=True, exist_ok=True)
        Path.mkdir(simple_location, parents=True, exist_ok=True)
        Path.mkdir(complex_location, parents=True, exist_ok=True)
    except FileExistsError:
        print("One of the necessary path already exists and is a file, default option will be set", flush=True)
        PATH_WORK = "ampl_code/example/"
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
    if not (res < 200 or (res >= 400 and res < 410)):
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
    if  not (res < 200 or (res >= 400 and res < 410)):
        return False, services, node
    else:
        return True, ampl.get_variable("X").get_values().to_dict(), ampl.get_variable("On").get_values().to_dict()

def json_sol(ampl:AMPL) -> dict:
    res_num = ampl.solve_result_num
    res = True
    if not (res_num < 200 or (res_num >= 400 and res_num < 410)):
        res = False
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
            if round(X[ms, f]) == 1:
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
        if(not res):
            extra = {"obj_func" : -1}
        sol["extra"] = extra
    network = []
    delay = ampl.get_parameter("d").get_values().to_dict()
    for f1 in ampl.get_set("F"):
        n_line = []
        for f2 in ampl.get_set("F"):
            n_line.append(delay[f1, f2])
        network.append(n_line)
    sol["network"] = network
    try:
        mig_in = ampl.get_variable("gp").get_values().to_dict()
        mig_out = ampl.get_variable("gm").get_values().to_dict()
        node = ampl.get_set("F")
        migration = {}
        for f1, f2, ms  in itertools.product(node, node, ampl.get_set("M")):
            if(round(mig_in[ms, f1]) == 1 and round(mig_out[ms, f2]) == 1):
                migration[ms] = [f1, f2]
        sol["migrations"] = migration
        set_off = []
        set_on = []
        accesi = ampl.get_variable("op").get_values().to_dict()
        spenti = ampl.get_variable("om").get_values().to_dict()
        for f in node:
            if round(spenti[f]) == 1:
                set_off.append(f)
            if round(accesi[f]) == 1:
                set_on.append(f)
        sol["set_on"] = set_on
        sol["set_off"] = set_off
    except:
        pass
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

def setup(ampl:AMPL, model:str = SIMP_MODEL, solver:str = "knitro", time_limit = SOLVE_TIME):
    ampl.reset()
    ampl.read(model)
    ampl.option["solver"] = solver
    ampl.option["knitro_options"] = f"outlev=6 mip_rootalg=3 restarts=4 mip_numthreads=1 maxtime_real={time_limit} ms_maxtime_real={time_limit} ma_maxtime_real={time_limit} mip_maxtime_real={time_limit}"
    #maxtime_real=300 ms_maxtime_real=300 ma_maxtime_real=300 mip_maxtime_real=300
    #ampl.option["solver_msg"] = 0
    #ampl.option["bonmin_options"] = f"bonmin.time_limit {time_limit} bonmin.node_comparison dynamic" 
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
        print(f"{ampl.solve_result_num}\t {res}", file=f, flush=True)
        print(time, file=f, flush=True)
        for k in d_t.keys():
            if d_t[k]:
                print(f"{k} = {d_t[k]}", file=f, flush=True)
        for k in d1.keys():
            if d1[k]:
                print(f"{k} = {d1[k]}", file=f, flush=True)

def retrive_param():
    '''
    Un primo tentativo, abbastanza brutto ma funzionale di ottenere i parametri di variazione dei lambda.
    '''
    base = 0.3
    config["rho"] = 0.8
    prob = get_problem(config).dump_problem()
    max_ = prob["sensor"]["S1"]["lambda"]
    config["rho"] = 0.2
    prob = get_problem(config).dump_problem()
    min_ = prob["sensor"]["S1"]["lambda"]
    delta = round((max_ - min_)/12, 3)
    config["rho"] = base
    return max_, min_, delta

def variable_prob(path_work_js, util):
    config["rho"] = 0.7
    prob = get_problem(config)
    config["rho"] = 0.3
    supp = get_problem(config)
    supp = supp.dump_problem()
    max_, min_, delta_ = retrive_param()
    prob_d = prob.dump_problem()
    for sc in prob_d["sensor"]:
        prob_d["sensor"][sc]["lambda"] = supp["sensor"][sc]["lambda"]
        chain = prob_d["sensor"][sc]["servicechain"]
        prob_d["servicechain"][chain]["lambda"] = supp["servicechain"][chain]["lambda"]
        for sv in prob_d["servicechain"][chain]["services"]:
            prob_d["microservice"][sv]["lambda"] = supp["microservice"][sv]["lambda"]
    with open(path_work_js, "w+") as f:
        js.dump(prob.dump_problem(), f, indent=2)
        f.close()
    csv_path = util.lambda_changer(path_work_js.__str__(), max_, min_, delta_)
    return prob, csv_path

def const_prob(path_work_js, util):
    base = config["rho"]
    config["rho"] = 0.7
    prob = get_problem(config)
    config["rho"] = base
    max_, min_, delta = retrive_param()
    delta = delta / 2
    prob_d = prob.dump_problem()
    for i, sc in enumerate(prob_d["sensor"]):
        if i < config['nchain'] // 2:
            prob_d["sensor"][sc]["lambda"] = max_
            chain = prob_d["sensor"][sc]["servicechain"]
            prob_d["servicechain"][chain]["lambda"] = max_
            for sv in prob_d["servicechain"][chain]["services"]:
                prob_d["microservice"][sv]["lambda"] = max_
        else:
            prob_d["sensor"][sc]["lambda"] = min_
            chain = prob_d["sensor"][sc]["servicechain"]
            prob_d["servicechain"][chain]["lambda"] = min_
            for sv in prob_d["servicechain"][chain]["services"]:
                prob_d["microservice"][sv]["lambda"] = min_
    
    with open(path_work_js, "w+") as f:
        js.dump(prob_d, f, indent=2)
        f.close()
    csv_path = util.lambda_constant(path_work_js.__str__(), max_, min_, delta)
    return prob, csv_path

def solve_problem(p):
    p, simple_location, complex_location = dir_creation(p)
    print(PATH_WORK, flush=True)
    path_work_js = p / "prob.json"
    util = AmplProbUtil()
    
    #prob = get_problem(config)
    #with open(path_work_js, "w+") as f:
    #    js.dump(prob.dump_problem(), f, indent=2)
    #    f.close()
    #csv_path = util.lambda_changer(path_work_js.__str__(), *retrive_param())
    if(ALT):
        prob, csv_path = const_prob(path_work_js, util)
    else:
        prob, csv_path = variable_prob(path_work_js, util)
    time_l = util.csv_time_reader(csv_path)
    PATH_DATA = PATH_WORK + "prova.dat"
    print(PATH_DATA, flush=True)
    util.write_prob(path_work_js, PATH_DATA)
    print(f"solving problem N #0 --> simple", flush=True)
    ampl = AMPL()
    setup(ampl, time_limit=SOLVE_TIME)
    res = solve_prob_simple(ampl, PATH_DATA, time_list=time_l[0])
    if res:
        print("Solved", flush=True)
    else:
        print("Failed", flush=True)
    if not res:
        return
    services = ampl.get_variable("X").get_values().to_dict()
    node = ampl.get_variable("On").get_values().to_dict()
    for key in services.keys():
        services[key] = round(services[key])
    for key in node.keys():
        node[key] = round(node[key])
    with open(path_work_js.parent / "res0.json", "w+") as f:
        js.dump(json_sol(ampl), f, indent=2)
        f.close()
    if STUPID:
        print_sol(ampl, p / "res0.bo", time=time_l[0])
    for i in range(1, 25):
        print(f"solving problem N #{i} --> simple", flush=True)
        setup(ampl, time_limit=SOLVE_TIME)
        res = solve_prob_simple(ampl, PATH_DATA, time_list=time_l[i])
        if res:
            print("Solved", flush=True)
            name = f"res{i}-S.json"
        else:
            print("Failed", flush=True)
            name = f"res{i}-F.json"
        if STUPID:
            print_sol(ampl, simple_location / f"res{i}.bo", time=time_l[i])
        with open(simple_location / name, "w+") as f:
            js.dump(json_sol(ampl), f, indent=2)
            f.close()
        print(f"solving problem N #{i} --> complex", flush=True)
        setup(ampl, model=COMP_MODE, time_limit=SOLVE_TIME)
        res, services, node = solve_prob_complex(ampl, data_path = PATH_DATA, time_list=time_l[i], services=services, node=node)
        for key in services.keys():
            services[key] = round(services[key])
        for key in node.keys():
            node[key] = round(node[key])
        if res:
            print("Solved", flush=True)
            name = f"res{i}-S.json"
        else:
            print("Failed", flush=True)
            name = f"res{i}-F.json"
        if STUPID:
            print_sol(ampl, complex_location / f"res{i}.bo", time=time_l[i], compl=True)
        with open(complex_location / name, "w+") as f:
            js.dump(json_sol(ampl), f, indent=2)
            f.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action= "store_true", help="Verbose output, display solver's verbose output")
    parser.add_argument('-c', '--constant', action="store_true", help="Modalità alternativa")
    parser.add_argument('-s', '--stupid', action= "store_true", help="Enable the first horrible save")
    parser.add_argument('-d', '--destination', help = "specify the dir where files will be saved")
    parser.add_argument('-t', '--time', help=f"set the maximum solving time (s) for each problem, default {SOLVE_TIME}", type=int)
    p = input_param(parser.parse_args())
    for i in range(10):
        solve_problem(p / f"prob{i}/")