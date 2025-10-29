import sys
import os
import csv
import numpy as np
import json as js

from gafog.fog_problem.problem import Problem
from gafog.problem_gen.genproblem import get_problem

base_config = {
    'nchain_fog': 0.8,
    'nsrv_chain': 4,
    'nchain': 10,
    'nfog': 32,
    'tchain': 10.0,
    'rho': 0.3,
    'enable_network': True,
    'delta_tchain': 0.1,
    'response': "file://sample_output.json",
}

def csv_time_reader(self, filename:str):
    time_l = []
    with open(filename, 'r', encoding="UTF-8", newline='') as f:
        has_header = csv.Sniffer().has_header(f.read(1024))
        f.seek(0)  # Rewind.
        reader = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
        if has_header:
            next(reader)
        for row in reader:
            time_l.append(row)
        f.close()
    return time_l

class AmplProbUtil:
    def __init__(self):
        self.delta = 0
        self.max_ = 0
        self.min_ = 0

    def print_csv(self, csv_path, servicechains, lambdas):
        """
        Stampa un file csv contenente i vari lambda per le servicechain

        Args:
            csv_path (str): csv path
            servicechains (list[str]): i nomi delle varie catene
            lambdas (list[np.ndarray]): i vari lambda per ogni ts
        """
        with open(csv_path, 'w', encoding="UTF-8", newline='') as f:
            writer = csv.writer(f, quotechar="'")
            writer.writerow(f'"{s}"' for s in servicechains)
            for l in lambdas:
                writer.writerow(map(lambda t: "%.3f" % t, l))

    def variable_lambda_generator(self, arr: np.array, categories: list, prob: list) -> np.ndarray:
        """
        Funzione che modifica i valori di un array di una certa frazione di self.delta
        secondo una probabilità categorica.

        Args:
            arr (np.array): array di valori
            categories (list): frazioni di delta
            prob (list): probabilità delle frazioni

        Returns:
            np.array: vettore modificato
        """
        n = np.size(arr)
        draw = np.random.choice(categories, n, p=prob)
        arr = np.add(arr, self.delta*draw)
        arr = np.where(arr > self.max_, self.max_, arr)
        arr = np.where(arr < self.min_, self.min_, arr)
        return arr

    def varible_ts(self, problem, categories=[-1, 0, 1], prob=[0.15, 0.25, 0.6], num_ts=24):
        """
        Generatore di un vettore di lambda con carico variabile: una fase num_ts/2 di crescita
        e una seguente di decrescita

        Args:
            problem (dict): dizionario json con i dati del problema.
            categories (list, optional): Frazioni di variazioni delta. Defaults to [-1, 0, 1].
            prob (list, optional): Probabilità delle varie frazioni. Defaults to [0.15, 0.25, 0.6].
            num_ts (int, optional): Numero di Time Slot. Defaults to 24.

        Returns:
            list: lista contenente il nome delle catene
            list: lista di num_ts + 1 lambda
        """
        l = []
        servicechain = []
        for sc in problem['servicechain']:
            l.append(problem['servicechain'][sc]['lambda'])
            servicechain.append(sc)
        l = np.array(l)
        lambdas = [l.tolist()]
        for i in range(num_ts // 2):
            l = self.variable_lambda_generator(l, categories, prob)
            lambdas.append(l.tolist())
        for i in range(num_ts // 2, num_ts):
            l = self.variable_lambda_generator(l, categories, prob[::-1])
            lambdas.append(l.tolist())
        return servicechain, lambdas
    
    def constant_lambda_generator(self, arr: np.ndarray, categories: list, prob: list) -> np.ndarray:
        """
        Funzione che modifica i valori della prima metà di un array di una certa frazione di self.delta
        secondo una probabilità categorica. Rispettivamente la seconda metà per una frazione di -self.delta

        Args:
            arr (np.ndarray): array di valori
            categories (list): frazioni di delta
            prob (list): probabilità delle frazioni

        Returns:
            np.array: vettore modificato
        """
        n = np.size(arr)
        draw = np.random.choice(categories, n, p=prob)
        arr[:n//2] = np.add(arr[:n//2], -self.delta*draw[:n//2])
        arr[n//2:] = np.add(arr[n//2:], self.delta*draw[n//2:])
        arr = np.where(arr > self.max_, self.max_, arr)
        arr = np.where(arr < self.min_, self.min_, arr)
        return arr
    
    def const_ts(self, problem:dict, categories = [-1, 0, 1], prob = [0.10, 0.20, 0.7], num_ts=24):
        """
        Generatore di un vettore di lambda con carico costante: una metà dei lambda cresce
        mentre l'altra metà decresce.

        Args:
            problem (dict): dizionario json con i dati del problema.
            categories (list, optional): Frazioni di variazioni delta. Defaults to [-1, 0, 1].
            prob (list, optional): Probabilità delle varie frazioni. Defaults to [0.10, 0.20, 0.7].
            num_ts (int, optional): Numero di Time Slot. Defaults to 24.

        Returns:
            list: lista contenente il nome delle catene
            list: lista di num_ts + 1 lambda
        """
        l = []
        servicechain = []
        for sc in problem['servicechain']:
            l.append(problem['servicechain'][sc]['lambda'])
            servicechain.append(sc)
        l = np.array(l)
        lambdas = [l.tolist()]
        for i in range(num_ts):
            l = self.constant_lambda_generator(l, categories, prob)
            lambdas.append(l.tolist())
        return servicechain, lambdas
    
    def lambda_changer(self, filename:str, max_, min_, delta):
        """
        Funzione che, dato il file json di un problema, genera un csv contenete le variazioni
        dei lambda per un problema a carico variabile

        Args:
            filename (str): path del file json
            max_ (float): valore massimo dei lambda
            min_ (float): valore minimo dei lambda
            delta (float): unità di variazione

        Returns:
            str: path del file csv
        """

        self.max_ = max_
        self.min_ = min_
        self.delta = delta
        l = []

        with open(filename) as f:
            problem = js.load(f)
            f.close()
        filename = filename.replace("json", "csv")
        
        servicechains, lambdas = self.varible_ts(problem)

        self.print_csv(filename, servicechains, lambdas)

        return filename

    def lambda_constant(self, filename:str, max_, min_, delta):
        """
        Funzione che, dato il file json di un problema, genera un csv contenete le variazioni
        dei lambda per un problema a carico costante

        Args:
            filename (str): path del file json
            max_ (float): valore massimo dei lambda
            min_ (float): valore minimo dei lambda
            delta (float): unità di variazione

        Returns:
            str: path del file csv
        """
        self.max_ = max_
        self.min_ = min_
        self.delta = delta
        l = []

        with open(filename) as f:
            problem = js.load(f)
            f.close()
        filename = filename.replace("json", "csv")

        l = np.array(l)

        servicechains, lambdas = self.const_ts(problem)

        self.print_csv(filename, servicechains, lambdas)
        return filename

def retrive_param(config):
    """
    Un primo, semplice metodo per estrarre dei parametri del problema.

    Args:
        config (dict): parametri del problema

    Returns:
        float: valore massimo di lambda
        float: valori minimo di lambda
        float: variazione di lambda tra i TS
    """
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

def variable_problem(problem_path, util:AmplProbUtil, config=base_config):
    """
    Generatore del problema a carico variabile

    Args:
        problem_path (str): posizione del file json del problema
        util (AmplProbUtil): classe per la gestione delle variazioni dei lambda
        config (dict, optional): json contenete le impostazioni di configurazione. Defaults to base_config.

    Returns:
        ProblemPerf|ProblemPwr: il problema al time slot 0
        csv_path: la poszione del file csv
    """
    config['rho'] = 0.7
    prob = get_problem(config)
    config['rho'] = 0.3
    supp = get_problem(config).dump_problem()
    max_, min_, delta_ = retrive_param(config)
    prob_d = prob.dump_problem()
    for sc in prob_d["sensor"]:
        prob_d["sensor"][sc]["lambda"] = supp["sensor"][sc]["lambda"]
        chain = prob_d["sensor"][sc]["servicechain"]
        prob_d["servicechain"][chain]["lambda"] = supp["servicechain"][chain]["lambda"]
        for sv in prob_d["servicechain"][chain]["services"]:
            prob_d["microservice"][sv]["lambda"] = supp["microservice"][sv]["lambda"]
    with open(problem_path, "w+") as f:
        js.dump(prob.dump_problem(), f, indent=2)
        f.close()
    csv_path = util.lambda_changer(problem_path.__str__(), max_, min_, delta_)
    return prob, csv_path

def const_problem(problem_path, util:AmplProbUtil, config=base_config):
    """
    Generatore del problema a carico costante

    Args:
        problem_path (str): posizione del file json del problema
        util (AmplProbUtil): classe per la gestione delle variazioni dei lambda
        config (dict, optional): json contenete le impostazioni di configurazione. Defaults to base_config.

    Returns:
        ProblemPerf|ProblemPwr: il problema al time slot 0
        csv_path: la poszione del file csv
    """
    base = config["rho"]
    config["rho"] = 0.7
    prob = get_problem(config)
    config["rho"] = base
    max_, min_, delta = retrive_param(config)
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
    
    with open(problem_path, "w+") as f:
        js.dump(prob_d, f, indent=2)
        f.close()
    csv_path = util.lambda_constant(problem_path.__str__(), max_, min_, delta)
    return prob, csv_path

if __name__ == '__main__':
    util = AmplProbUtil()
    const_problem(".\\example\\const.json", util)
    variable_problem(".\\example\\var.json", util)
    