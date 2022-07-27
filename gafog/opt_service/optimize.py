#!/usr/bin/python3
import sys
import json
import argparse
import requests
from enum import Enum

from ..fog_problem.problem import Problem
from ..fog_problem.solution import Solution
from ..ga import ga as gamod

class Algorithms(Enum):
    GA='GA'
    VNS='VNS'
    MBFD='MBFD'
    AMPL='AMPL'

available_algorithms=[Algorithms.GA]

def algorithm_by_name(algo):
    for a in available_algorithms:
        if algo == a.name:
            return a
    return None

def write_solution(fout, sol):
    with open(fout, "w+") as f:
        json.dump(sol.dump_solution(), f, indent=2)


def solve_problem(problem: Problem, algo):
    match algo:
        case Algorithms.GA:
            return gamod.solve_problem(problem)

def send_response(sol: Solution, default_url=None):
    resp=sol.get_problem().get_response_url()
    if resp is None:
        if default_url is None:
            return
        else:
            resp=default_url
    if resp.startswith('file://'):
        write_solution(resp.lstrip('file://'), sol)
    else:
        # use requests package to send results
        requests.post(data['response'], json=sol.dump_solution())

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='input file. Default sample_input2.json')
    parser.add_argument('-a', '--algo', help='algorithm. Available: GA (default), MBFD, VNS, AMPL')
    args = parser.parse_args()
    fname='sample/' + (args.file or'sample_input2.json')
    algoname=args.algo or 'GA'
    algo=algorithm_by_name(algoname)
    if not(algo):
        raise NameError(f'algorithm {algoname} is not valid')
    with open(fname,) as f:
        data = json.load(f)
    sol=solve_problem(Problem(data), algo)
    print(sol)
    if sol:
        send_response(sol)