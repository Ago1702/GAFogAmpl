<%!
    import json
    import pdb
    from gafog.fog_problem.problem import Problem

    def check_next(p, m1, m2):
        if(m1 == m2):
            return 0
        prec = False
        for sc in p.get_servicechain_list():
            if m1 not in p.get_microservice_list(sc):
                continue
            if len(p.get_microservice_list(sc)) == 1:
                return 0
            for ms in p.get_microservice_list(sc):
                if(ms == m2 and prec):
                    return 1
                elif(ms == m1):
                    prec = True
                else:
                    prec = False
        return 0
%>\
<%
    with open(filepro) as f:
        p = Problem(json.load(f))
%>\
param K := 10;
param eps := 0.001;

set Ct:=\
%for sc in p.get_servicechain_list():
 ${sc}\
%endfor
;
set M :=\
%for ms in p.get_microservice_list():
 ${ms}\
%endfor
;
set F :=\
%for fn in p.get_fog_list():
 ${fn}\
%endfor
;
%for sc in p.get_servicechain_list():
set C["${sc}"] :=\
    %for ms in p.get_microservice_list(sc):
 ${ms}\
    %endfor
;
%endfor

param:      lm      Sm      Om      :=
%for ms in p.get_microservice_list():
${ms}       ${p.get_microservice(ms)["lambda"]}       ${p.get_microservice(ms)["meanserv"]}      ${p.get_microservice(ms)["stddevserv"]}
%endfor
;

param:  lc  :=
%for sc in p.get_servicechain_list():
${sc}   ${p.get_servicechain(sc)["lambda"]}
%endfor
;

param   P   :=
%for fn in p.get_fog_list():
 ${fn}  ${p.get_fog(fn)["capacity"]}
%endfor
;

param   o:\
%for ms in p.get_microservice_list():
    ${ms}\
%endfor
    :=
%for sc in p.get_servicechain_list():
    %for ms1 in p.get_microservice_list(sc):
    ${ms1}\
        %for ms2 in p.get_microservice_list():
    ${check_next(p, ms2, ms1)}\
        %endfor

    %endfor
%endfor
;

param   d:\
%for fn in p.get_fog_list():
    ${fn}\
%endfor
    :=
%for f1 in p.get_fog_list():
    ${f1}\
    %for f2 in p.get_fog_list():
        %if p.get_delay(f1, f2) != None:
    ${p.get_delay(f1, f2)["delay"]}\
        %else:
    Infinity\
        %endif
    %endfor

%endfor
;