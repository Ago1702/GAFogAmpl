import matplotlib.pyplot as plt
import numpy as np

periodi = []
with open("C:\\Users\\david\\shared\\din_test\\test10\\periodi.t") as f:
    s = f.readline()
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
    f.close()

dm_in = []
dm_ou = []
dm_on = []
dm_of = []
dm_ac = []
sm_in = []
sm_ou = []
sm_on = []
sm_of = []
sm_ac = []

with open("C:\\Users\\david\\shared\\din_test\\test10\\mig.res") as f:
    s = f.readline()
    while True:
        s = f.readline()
        if not s:
            break
        data = s.split("\t")
        sm_in.append(float(data[1]))
        sm_ou.append(float(data[2]))
        sm_on.append(float(data[3]))
        sm_of.append(float(data[4]))
        sm_ac.append(float(data[5]))
        dm_in.append(float(data[7]))
        dm_ou.append(float(data[8]))
        dm_on.append(float(data[9]))
        dm_of.append(float(data[10]))
        dm_ac.append(float(data[11]))
    f.close()

sm_in = np.array(sm_in)
sm_ou = np.array(sm_ou)
sm_on = np.array(sm_on)
sm_of = np.array(sm_of)
sm_ac = np.array(sm_ac)
dm_in = np.array(dm_in)
dm_ou = np.array(dm_ou)
dm_on = np.array(dm_on)
dm_of = np.array(dm_of)
dm_ac = np.array(dm_ac)
ddata = [dm_in, dm_on, dm_of, dm_ac]
sdata = [sm_in, sm_on, sm_of, sm_ac]
hardcol = ["b", "g", "y", "r"]
colors = ["pink", "lightsalmon", "lightblue", "lightgreen"]
plt.ylabel("freq. richieste")
plt.xlabel("periodo")
for per in range(1, len(periodi)):
    lol = np.array(periodi[per])
    c = 0
    while not np.all(lol == -1):
        i = lol.argmax()
        plt.bar(per, lol[i], color=colors[i], edgecolor="k", alpha=1)
        lol[i] = -1
        c+=1
plt.title("Modello ottimizzazione Resp. Time")
no_cap = plt.twinx()
#no_cap.plot(range(1, 24), ddata, label="din model", color="r", marker="D")
#no_cap.plot(range(1, 24), sdata, label="time opt model", color="b", marker="D")
hardcol = ["b", "g", "purple", "r"]
labels = ["migrazioni", "accesi", "spenti", "attivi"]
markers = ["p","H", "D", "s"]
for i in range(len(sdata)):
    no_cap.plot(range(1, 24), ddata[i], label=labels[i], color=hardcol[i], marker=markers[i])
no_cap.legend()
no_cap.set_ybound(-1,25)
no_cap.set_yticks(range(0,24,2))
#plt.ylabel("obj. func.")
no_cap.legend()
#no_cap.set_ybound(50,260)
plt.show()