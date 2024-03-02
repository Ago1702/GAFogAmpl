from mako.template import Template
from mako import exceptions
from gafog.fog_problem.problem import Problem
import json
import pdb
import sys
import os



if __name__ == "__main__":
    print(os.getcwd())
    os.system("python -m gafog.problem_gen.genproblem")
    filen="mako_try\problem.dat.mako"
    mt = Template(filename="mako_try\problem.dat.mako")
    try:
        rd_mt=mt.render_unicode(filepro = "sample\sample_problem.json")
    except:
        print(exceptions.text_error_template().render() + "\n")
        sys.exit(-1)
    with open("exer\\tesi\mako.dat", "wb") as f:
        f.write(rd_mt.encode())
        f.close()