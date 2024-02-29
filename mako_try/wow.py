from mako.template import Template
from mako import exceptions
from ..GAFog.gafog.fog_problem.problem import Problem
import json
import pdb
import sys
import os



if __name__ == "__main__":
    os.chdir("D:\\ampl_data\GAFog")
    os.system("python -m gafog.problem_gen.genproblem")
    filen="D:\\ampl_data\mako_try\problem.dat.mako"
    mt = Template(filename="D:\\ampl_data\mako_try\problem.dat.mako")
    try:
        rd_mt=mt.render_unicode(filepro = "D:\\ampl_data\GAFog\sample\sample_problem.json")
    except:
        print(exceptions.text_error_template().render() + "\n")
        sys.exit(-1)
    with open("D:\\ampl_data\exer\\tesi\mako.dat", "wb") as f:
        f.write(rd_mt.encode())
        f.close()