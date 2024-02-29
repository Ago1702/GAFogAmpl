import matplotlib.pyplot as plt
import matplotlib.pyplot as frq
import matplotlib.pyplot as fun
import numpy as np


m1 = [7, 3, 3, 3, 3, 2, 2, 2, 8, 8, 7, 1, 8, 6, 6]
m2 = [8, 8, 8, 4, 4, 2, 2, 2, 8, 9, 7, 1, 8, 6, 6]
m3 = [9, 9, 9, 9, 5, 2, 2, 8, 9, 9, 7, 1, 8, 9, 9]
m4 = [1, 1, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 3]


period = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])
obj_f = [60, 60, 47, 42, 40, 27, 20, 52, 72, 60, 60, 34, 84, 60, 62]
mig = np.array([0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 2, 2, 0, 1])
onn =          [3, 3, 3, 2, 2, 1, 1, 2, 3, 3, 3, 1, 3, 3, 3]
spe =          [0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 2, 0, 0, 0]
acc =          [0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 2, 0, 0]
bwidth=0.50
pattern=["+","x","."]

colors = ["pink", "lightsalmon", "lightblue", "lightgreen"]

freq = plt.subplot()
freq.bar(period, m3, label="µ-service 1", width=bwidth, alpha=1, edgecolor="black",color=colors[0], hatch="\\\\")
freq.bar(period, m2, label="µ-service 2", width=bwidth, alpha=1, edgecolor="black",color=colors[1], hatch="oo")
freq.bar(period, m1, label="µ-service 3", width=bwidth, alpha=1, edgecolor="black",color=colors[2], hatch="//")
freq.bar(period, m4, label="µ-service 4", width=bwidth, alpha=1, edgecolor="black",color=colors[3], hatch="x")
func = freq.twinx()
#func.plot(period, obj_f, label="objective function", color="red", marker="P")
func.plot(period, onn, label="active node", marker="P", color="black")
func.plot(period, acc, label="powered on", marker='H', color="red")
func.plot(period, spe, label="powered off", marker='D', color="purple")
func.plot(period, mig  * 2, label="migration", marker='s', color="navy")
box = func.get_position()
#func.set_position([box.x0, box.y0, box.width * 0.8, box.height])
func.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=3, fancybox=True, shadow=True)
func.set_ylim([-0.25,5])
func.set_yticks([0,1,2,3,4])
freq.legend(loc="upper left")
freq.set_ylabel("Request frequency")
freq.set_xlabel("Period")
plt.show()




'''ampl: include simple.run;
SCIP 8.0.3: SCIP 8.0.3: optimal solution; objective 62
4 simplex iterations
1 branching nodes
X [*,*]
:   f1  f2  f3    :=
m1   0   0   1
m2   0   1   0
m3   1   0   0
;

Migration = 62

O [*] :=
f1 1   f2 1   f3 1
;

ampl: include simple.run;
SCIP 8.0.3: SCIP 8.0.3: optimal solution; objective 60
3 simplex iterations
1 branching nodes
X [*,*]
:   f1  f2  f3    :=
m1   0   0   1
m2   0   1   0
m3   1   0   0
;

Migration = 60

O [*] :=
f1 1   f2 1   f3 1
;

ampl: include simple.run;
SCIP 8.0.3: SCIP 8.0.3: optimal solution; objective 60
3 simplex iterations
1 branching nodes
X [*,*]
:   f1  f2  f3    :=
m1   0   0   1
m2   0   1   0
m3   1   0   0
;

Migration = 60

O [*] :=
f1 1   f2 1   f3 1
;

ampl: include simple.run;
SCIP 8.0.3: SCIP 8.0.3: optimal solution; objective 47
7 simplex iterations
1 branching nodes
X [*,*]
:   f1  f2  f3    :=
m1   0   0   1
m2   0   0   1
m3   1   0   0
;

Migration = 47

O [*] :=
f1 1   f2 0   f3 1
;

ampl: reset;
ampl: include simple.run;
SCIP 8.0.3: SCIP 8.0.3: optimal solution; objective 40
8 simplex iterations
1 branching nodes
X [*,*]
:   f1  f2  f3    :=
m1   0   0   1
m2   0   0   1
m3   1   0   0
;

Migration = 40

O [*] :=
f1 1   f2 0   f3 1
;

ampl: include simple.run;
SCIP 8.0.3: SCIP 8.0.3: optimal solution; objective 27
7 simplex iterations
1 branching nodes
X [*,*]
:   f1  f2  f3    :=
m1   0   0   1
m2   0   0   1
m3   0   0   1
;

Migration = 27

O [*] :=
f1 0   f2 0   f3 1
;

ampl: include simple.run;
SCIP 8.0.3: SCIP 8.0.3: optimal solution; objective 20
0 simplex iterations
1 branching nodes
X [*,*]
:   f1  f2  f3    :=
m1   0   0   1
m2   0   0   1
m3   0   0   1
;

Migration = 20

O [*] :=
f1 0   f2 0   f3 1
;

ampl: include simple.run;
SCIP 8.0.3: SCIP 8.0.3: optimal solution; objective 84
4 simplex iterations
1 branching nodes
X [*,*]
:   f1  f2  f3    :=
m1   1   0   0
m2   0   1   0
m3   0   0   1
;

Migration = 84

O [*] :=
f1 1   f2 1   f3 1
;

ampl: include simple.run;
SCIP 8.0.3: SCIP 8.0.3: optimal solution; objective 60
3 simplex iterations
1 branching nodes
X [*,*]
:   f1  f2  f3    :=
m1   1   0   0
m2   0   1   0
m3   0   0   1
;

Migration = 60

O [*] :=
f1 1   f2 1   f3 1
;

ampl: '''