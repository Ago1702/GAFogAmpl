param K;
param eps;

set Ct;
set F;			#Fog nodes
set M;			#Services
set C{Ct} within M;

var X{m in M,f in F} binary;	#Service j on node i at t + 1

param lc {c in Ct} >= 0;
param lm {j in M} >= 0;			#incomin req. rate at t
var lf {i in F} = 
	sum {j in M} lm[j]*X[j,i];

param l = sum {c in Ct} lc[c];
param wc {c in Ct} = lc[c]/l;

param P {i in F} >= 0;				#comp power node i
param o {M,M} binary;		#microserv order
param d {F,F} >= 0;			#delay between 2 nodes

param Sm {j in M} >= 0;				#proc time service j
param Om {j in M} >= 0;			#resp time service j

param Xt {j in M, i in F} binary;	#Service j on node i at t
param Ot {i in F} binary;			#Node i on at t-1


param Tsla {c in Ct} = K*(sum {m in C[c]} Sm[m]);

var Si {i in F} = 
				if lf[i] == 0
				then 0
				else (sum {j in M} X[j,i] * (lm[j]/lf[i]) * Sm[j])/P[i];

var O2i {i in F} = 
					if lf[i] == 0
					then 0
					else (sum {j in M} X[j,i] * (lm[j]/lf[i]) * (Sm[j]^2 + Om[j]^2))/(P[i]^2) - Si[i]^2;

var Wf {i in F} =
				/*if lf[i]*Si[i] == 1
				then Infinity
				else*/ (Si[i]^2 + O2i[i]) * lf[i]/(2*(1 - lf[i]*Si[i]));

var Rc {c in Ct} = 
	sum {m in C[c]} sum {f in F} X[m,f] * (Wf[f] + Sm[m]/P[f]) +
	sum {m1 in C[c], m2 in C[c]} (sum {f1 in F, f2 in F} (o[m1,m2] * X[m1,f1] * X[m2,f2] * d[f1,f2]));

var tot_time = sum {c in Ct} Rc[c] * wc[c];

#decisional
var gm {M,F} binary;	#service j migrate from node i
var gp {M,F} binary;	#service j migrate to node i
var om {F} binary;		#node powered off
var op {F} binary;		#node powerd on

var On {i in F} binary;

#Weight
param Wmig = 1;
param Won = 10;
param Woff = 5;
param Wnode = 20;

minimize Migration:
	Wmig * sum {j in M, i in F} (gp[j, i] + gm[j,i]) + sum {i in F} (Won * op[i] + Woff * om[i] + Wnode * On[i]);
	
subject to Overload {i in F}:
	lf[i]*Si[i] <= On[i]*(1 - eps);

subject to Allocation {m in M}:
	sum {f in F} X[m, f] == 1;
	
subject to Response_Sla {c in Ct}:
	Rc[c] <= Tsla[c];
	
subject to In_Out {j in M}:
	sum {i in F} gp[j,i] == sum {i in F} gm[j,i];
	
subject to One_Mig {j in M}:
	sum {i in F} gm[j,i] <= 1;
	
subject to Leave_Pres {j in M, i in F}:
	gm[j,i] <= Xt[j,i];
	
subject to Inc_Pres {j in M, i in F}:
	gp[j,i] <= X[j,i];
	
subject to Diff_Move {j in M, i in F}:
	gm[j,i] + gp[j,i] <= 1;
	
subject to Allo_Def {j in M, i in F}:
	X[j,i] = Xt[j,i] + gp[j,i] - gm[j,i];

subject to On_if_Off {i in F}:
	op[i] <= 1 - Ot[i];
	
subject to Off_if_On {i in F}:
	om[i] <= Ot[i];
	
subject to Lol {i in F}:
	om[i] + op[i] <= 1;	#node i on at t;