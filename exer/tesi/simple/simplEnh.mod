set F;			#Fog nodes
set S;			#Services

set Sin;
set Sout within S;	#chiederne la fattibilità


param mu;
param lmb {j in (S union Sin)} >= 0;			#incomin req. rate at t
param Si {F} = 1 / mu;				#Proc. time at t
param R {j in S union Sin} >= 0;				#resp time service j
param Xt {j in S, i in F} binary;	#Service j on node i at t
param Ot {i in F} binary;			#Node i on at t-1
param Tsla >= 0;
param Omg;

var X{S union Sin union Sout,F} binary;	#Service j on node i at t + 1
var O{F} binary;	#node i on at t

#decisional
var gm {S union Sout union Sin,F} binary;	#service j migrate from node i
var gp {S union Sin union Sout,F} binary;	#service j migrate to node i
var Om {F} binary;		#node powered off
var Op {F} binary;		#node powerd on

#Weight
param Wmig;
param Won;
param Woff;
	

minimize Migration:
	Wmig * sum {j in S union Sin union Sout, i in F} (gp[j, i] + gm[j,i]) + sum {i in F} (Won * Op[i] + Woff * Om[i]);
	

subject to Overload {i in F}:
	sum {j in S} X[j,i] * lmb[j] <= O[i]/Si[i];
	
subject to Response_Sla {i in F}:
	mu - sum {j in S} (X[j,i] * lmb[j]) >= 1/Tsla;
	
subject to Allocation {j in S union Sin}:
	sum {i in F} X[j,i] == 1;
	
subject to Ciao {j in Sout}:
	sum {i in F} X[j,i] == 0;
#il vincolo impedisce di partire da una configurazione nulla.
#È necessario fornire una configurazione iniziale
subject to In_Out {j in S}:
	sum {i in F} gp[j,i] == sum {i in F} gm[j,i];
	
#Valutare l'ingresso di altri servizi
subject to New_In {j in Sin}:
	sum {i in F} gp[j,i] == 1;
	
subject to Old_out {j in Sout}:
	sum {i in F} gm[j,i] == 1;
#Riga per separare la mia aggiunta
	
subject to One_Mig {j in S}:
	sum {i in F} gm[j,i] <= 1;
	
subject to Leave_Pres {j in S union Sout, i in F}:
	gm[j,i] <= Xt[j,i];
	
subject to Inc_Pres {j in S union Sin, i in F}:
	gp[j,i] <= X[j,i];
	
subject to Diff_Move {j in S, i in F}:
	gm[j,i] + gp[j,i] <= 1;
	
subject to Allo_Def {j in S, i in F}:
	X[j,i] = Xt[j,i] + gp[j,i] - gm[j,i];

subject to On_if_Off {i in F}:
	Op[i] <= 1 - Ot[i];
	
subject to Off_if_On {i in F}:
	Om[i] <= Ot[i];
	
subject to Lol {i in F}:
	Om[i] + Op[i] <= 1;
	
subject to Status {i in F}:
	O[i] = Ot[i] + Op[i] - Om[i];
	
subject to OMG:
	sum {i in F} O[i] == Omg;