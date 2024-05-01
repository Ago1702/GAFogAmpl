#import pdb
import sys
import os
import csv
import numpy as np
import json as js
from mako.template import Template
from mako import exceptions
from gafog.fog_problem.problem import Problem
from gafog.problem_gen.genproblem import get_problem



mako_path = "ampl_code\problem.dat.mako"

config = {
    'nchain_fog': 0.4,
    'nsrv_chain': 4,
    'nchain': 3,
    'nfog': 5,
    'tchain': 10.0,
    'rho': 0.4,
    'enable_network': True,
    'delta_tchain': 0.05,
    'response': "file://sample_output.json",
}

class AmplProbUtil:
    delta = 0
    max_ = 0
    min_ = 0

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
            
    def write_prob(self, json_path:str = "sample\sample_problem.json", dat_path:str = "exer\\tesi\mako.dat"):
        '''
        funzione atta a convertire il .json in un file .dat leggibile da AMPL
        '''
        mt = Template(filename=mako_path)
        try:
            rd_mt=mt.render_unicode(filepro = json_path)
        except:
            print(exceptions.text_error_template().render() + "\n")
            sys.exit(-1)
        with open(dat_path, "wb") as f:
            f.write(rd_mt.encode())
            f.close()
    
    def random(self, arr: np.array, categories: list, prob: list):
        '''Una semplice funzione per la generazione delle variazioni nelle frequenze di attivazione'''
        n = np.size(arr)
        draw = np.random.choice(categories, n, p=prob)
        arr = np.add(arr, self.delta*draw)
        arr = np.where(arr > self.max_, self.max_, arr)
        arr = np.where(arr < self.min_, self.min_, arr)
        return arr

    def lambda_changer(self, filename:str, max_, min_, delta):
        '''Funzione atta a leggere i file json del problema e variare le frequenze di attivazione ad ogni TS.
        I nuovi TS verranno salvati in un file .csv'''
        self.max_ = max_
        self.min_ = min_
        self.delta = delta
        categories = [-1, 0, 1]
        prob = [0.10, 0.10, 0.8]
        l = []

        with open(filename) as f:
            j = js.load(f)
            for sc in j['servicechain']:
                l.append(j['servicechain'][sc]['lambda'])
            f.close()
        filename = filename.replace("json", "csv")

        l = np.array(l)
        with open(filename, 'w', encoding="UTF-8", newline='') as f:
            writer = csv.writer(f, quotechar="'")
            writer.writerow(f'"{s}"' for s in j['servicechain'])
            writer.writerow(map(lambda t: "%.3f" % t, l))
            for i in range(12):
                l = self.random(l, categories, prob)
                writer.writerow(map(lambda t: "%.3f" % t, l))
            for i in range(12):
                l = self.random(l, categories, prob[::-1])
                writer.writerow(map(lambda t: "%.3f" % t, l))
        return filename

'''if __name__ == '__main__':
    prob = get_problem(config)
    for i in range(5):
        with open(f"{dir}prova{i}.json", "w+") as f:
            js.dump(prob.dump_problem(), f, indent=2)
            f.close()
        AmplProbUtil.lambda_changer(f"{dir}prova{i}.json")'''