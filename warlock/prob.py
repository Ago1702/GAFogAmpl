import numpy as np
import json as js
import csv
from ..gafog.fog_problem.problem import Problem
from ..gafog.problem_gen.genproblem import get_problem

dir = 'C:\\Users\\david\\Uni\\Paper\\fog\\GAFog\\warlock\\sample1\\'

config = {
    'nchain_fog': 0.4,
    'nsrv_chain': 5,
    'nchain': 4,
    'nfog': 5,
    'tchain': 10.0,
    'rho': 0.4,
    'enable_network': True,
    'delta_tchain': 0.05,
    'response': "file://sample_output.json",
}

def random(arr: np.array, categories: list, prob: list, delta=0.01, max = 0.14, min = 0.07):
    n = np.size(arr)
    draw = np.random.choice(categories, n, p=prob)
    arr = np.add(arr, delta*draw)
    arr = np.where(arr > max, max, arr)
    arr = np.where(arr < min, min, arr)
    return arr


def lambda_changer(filename:str):
    categories = [-1, 0, 1]
    prob = [0.15, 0.15, 0.7]
    l = []

    with open(filename) as f:
        j = js.load(f)
        for sc in j['servicechain']:
            l.append(j['servicechain'][sc]['lambda'])
        f.close()
    filename = filename.replace("json", "csv")

    l = np.array(l)
    with open(filename, 'w', encoding="UTF-8", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(j['servicechain'])
        for i in range(12):
            l = random(l, categories, prob)
            writer.writerow(map(lambda t: "%.3f" % t, l))
        for i in range(12):
            l = random(l, categories, prob[::-1])
            writer.writerow(map(lambda t: "%.3f" % t, l))

if __name__ == '__main__':
    prob = get_problem(config)
    for i in range(5):
        with open(f"{dir}prova{i}.json", "w+") as f:
            js.dump(prob.dump_problem(), f, indent=2)
            f.close()
        lambda_changer(f"{dir}prova{i}.json")
    

        
    