from mako.template import Template

myt = Template(filename='D:\\ampl_data\mako_try\problem.dat.mako')
print(myt.render(filepro = "D:\\ampl_data\GAFog\sample\sample_input.json"))