param N;					#number of chain
param K;					#constant for SLA
param eps;

set M;						#Set micro-serv
set F;						#Set of fog-nodes
set C {1..N} within M;		#Set of service chain

var X {M,F} binary;			#dec. var

param lc {1..N} >= 0;		#In req rate to chain
param lm {m in M} >= 0;
var lf {f in F} =			#In req rate to fog node
	sum {m in M} X[m,f] * lm[m];
param l =					#In req rate global
	sum {c in {1..N}}(lc[c]);

param wc {c in {1..N}} = lc[c]/l;

param P {F} >= 0;			#Power of fog node f
param o {M,M} binary;		#microserv order
param d {F,F} >= 0;			#delay between 2 nodes

param Sm {M};				#service time of microservice m
param Om {M};				#std dev of Sm


param SLA {c in {1..N}} = K*(sum {m in C[c]} Sm[m]);

var Sf {f in F} = (if lf[f] = 0
					then 0 
					else (sum {m in M} X[m,f] * (lm[m]/lf[f]) * Sm[m])/P[f]);
					
var O2f{f in F} = (if lf[f] = 0
					then 0
					else (sum {m in M} X[m,f] * (lm[m]/lf[f]) * (Sm[m]^2 + Om[m]^2))/(P[f]^2) - Sf[f]^2);
					
var Wf {f in F} = /*(if lf[f] * Sf[f] = 1
					then Infinity
					else*/ (Sf[f]^2 + O2f[f]) * lf[f] / (2 * (1 - lf[f]*Sf[f]));		#Expected waiting time from Pollaczek Khinchin eq.
var Rc {c in {1..N}} = 
	sum {m in C[c]} sum {f in F} X[m,f] * Wf[f] +
	sum {mm in C[c]} Sm[mm] +
	sum {m1 in C[c], m2 in C[c]} (sum {f1 in F, f2 in F} (o[m1,m2] * X[m1,f1] * X[m2,f2] * d[f1,f2]));
	
	
	
minimize Response_Time:
	sum {c in {1..N}} Rc[c] * wc[c];
	
subject to Presence {m in M}:
	sum {f in F} X[m,f] = 1;

subject to Overload {f in F}:
	lf[f] * Sf[f] <= 1 - eps;
	
subject to Service_Level {c in {1..N}}:
	Rc[c] <= SLA[c];
	