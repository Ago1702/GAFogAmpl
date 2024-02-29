import matplotlib.pyplot as plt
import numpy as np

periodi = []
chain_time = []
s_time = []
d_time = []
first = True
with open("C:\\Users\\david\\shared\\lol\\test8\\periodi.t") as f:
    ser = f.readline()
    ser = ser.split("\t")
    while True:
        s = f.readline()
        if not s:
            break
        perlist = s.split("\t")
        freq = []
        for i in range(1, len(perlist)):
            try:
                freq.append(float(perlist[i]))
            except ValueError:
                pass
        periodi.append(freq)
        time = []
        s = f.readline()
        perlist = s.split("\t")
        for i in range(len(ser) - 2):
            try:
                time.append(float(perlist[i]))
            except ValueError:
                pass
        s_time.append(time)
        if first:
            first = False
            d_time.append(time)
            continue
        time = []
        for i in range(len(ser) - 2 , len(ser)*2 - 4):
            try:
                time.append(float(perlist[i]))
            except ValueError:
                pass
        d_time.append(time)
    f.close()

hardcol = ["b", "g", "y", "r"]
colors = ["pink", "lightsalmon", "lightblue", "lightgreen"]
plt.ylabel("freq. richieste")
plt.xlabel("periodo")
for per in range(len(periodi)):
    lol = np.array(periodi[per])
    c = 0
    while not np.all(lol == -1):
        i = lol.argmax()
        plt.bar(per, lol[i], color=colors[i], edgecolor="k", alpha=1)
        lol[i] = -1
        c+=1
periodi = np.array(periodi)
d_time = np.array(d_time)
s_time = np.array(s_time)
for i in range(periodi.shape[0]):
    periodi[i] = periodi[i]/periodi[i].sum()
d_mean = np.sum(d_time * periodi, axis=1)
s_mean = np.sum(s_time * periodi, axis=1)
d_var = np.power(d_time - np.tile(d_mean, (4, 1)).T, 2)
s_var = np.power(s_time - np.tile(s_mean, (4, 1)).T, 2)
s_var = np.sqrt(np.sum(s_var * periodi, axis=1))
d_var = np.sqrt(np.sum(d_var * periodi, axis=1))
'''d_mean = d_time.mean(axis=1)
s_mean = s_time.mean(axis=1)
d_var = np.sqrt(d_time.var(axis=1))
s_var = np.sqrt(s_time.var(axis=1))'''
no_cap = plt.twinx()
SLA = np.ones((24,))
SLA *=100
plt.plot(range(24), SLA, color="k", label="SLA", linestyle="--")
plt.plot(range(24), d_mean, color="r", label="mod. din")
plt.plot(range(24), s_mean, color="b", label="mod. std")
plt.fill_between(range(24), d_mean - d_var, d_mean + d_var, color="r", alpha=0.3)
plt.fill_between(range(24), s_mean - s_var, s_mean + s_var, color="b", alpha=0.3)
plt.legend()
plt.ylabel("Tempo risposta medio (sec.)")
plt.show()