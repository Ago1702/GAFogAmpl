import json as js
from pathlib import Path

PATH = '/home/ampl/agos/fog/GAFogAmpl/ampl_code/example_c0'

lol = Path(PATH)
for num in range(10):
    p = lol / f'prob{num}'
    if(not Path.exists(p / 'res0.json')):
        continue
    with open(p / 'res0.json') as json:
        res = js.load(json)
    nodes_s = set()
    for ms in res['microservice']:
        nodes_s.add(res['microservice'][ms])
    p = p / 'complex'

    nodes_p = set()
    for i in range(1, 25):
        tmp = p / f'res{i}-S.json'
        if(not tmp.exists()):
            continue
        with open(tmp) as json:
            res = js.load(json)
        nodes_p.clear()
        nodes_p.update(nodes_s)
        nodes_s.clear()
        for ms in res['microservice']:
            nodes_s.add(res['microservice'][ms])
        node_off = list(nodes_p.difference(nodes_s))
        node_on = list(nodes_s.difference(nodes_p))
        res['set_on'] = node_on
        res['set_off'] = node_off
        tmp = p / f'res{i}-S1.json'
        with open(p / f'res{i}-S1.json', 'w+') as f:
            js.dump(res, f, indent=2)