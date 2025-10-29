import json
from ..fog_problem.problem import Problem

class ProblemPerf(Problem):
    
    def __init__(self, problem_dct):
        super().__init__(problem_dct)
        self.compute_service_params()
        self.compute_chain_params()

    def get_solution(self, chromosome):
        from ..fog_problem.solution_perf import SolutionPerf
        return SolutionPerf(chromosome, self)

    def dump_problem(self):
        """ Returns a dict of the problem's values. """
        rv=super().dump_problem()
        return rv

    def __str__(self):
        return 'services: %s' % str(list(self.microservice.keys()))

    def compute_service_params(self):
        """ Computes rate and cv for all the microservices in the list. """
        super().compute_service_params()

    def compute_chain_params(self):
        """ 
            Computes the params of all the servicechain. 
            It calculates lambda and weight.    
        """
        super().compute_chain_params()
    
if __name__ == '__main__':
    with open('sample/sample_input2.json') as f:
        data = json.load(f)
    
    p = ProblemPerf(data)
    print(p)
    
    for ms in p.get_microservice_list():
        print(ms, p.get_microservice(ms))