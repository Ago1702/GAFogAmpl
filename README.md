# Ampl Solver

Un script di risoluzione che fa uso di AMPL
- __python -m ampl_code.solver__ è il comando da eseguire nella directory GAFogAmpl per avviare la risoluzione di due problemi
- Il primo sarà quello semplice che ha, come obiettivo principale la riduzione dei nodi accesi
- Il secondo sarà quello dinamico che punta alla riduzione delle varizioni nel sistema
I risultati dei vari problemi verranno salvati di default nella cartella ampl_code\example:
- __prova.dat__ è il file dove viene salvata la configurazione del problema
- __prob.json__ è il file json generato dal generatore di problemi in __fog_problem__
- __prob.csv__ un file csv contenente tutte la variazioni di tempo del sistema
- __res0.bo__ prima configurazione ottenuta dal solver comune a entrambi i problemi
- __complex/__, __simple/__ directory contenenti i file __.bo__ con le configurazioni relative ai due problemi

È possibile, per ora, fornire i seguenti argomenti da linea di comando:
- __-v__ per attivare la modalità verbose
- __-d__ per cambiare la posizione di default dell'output (_ampl_code\example_)
- __-t__ per modificare il tempo (s) massimo di risoluzione di un problema, default 200

# Original
# Fog GA with Docker integration

Joint work with university of Bologna

## List of services

- __charact_service__: measures the service time of a microservice
- __ga__: optimizes the deployment of service chains composed of multiple microservices
- __graph_service__: creates a graphic representation of a service chain deployment (Graphviz .dot file or .svg image)
- __problem_gen__: generates experiment to test the performance of the available algorithms

## Other relevant functions

- __fog_problem__: general framework to define problem and solutions. Includes objective function, ability to read/dump data in JSON format
- __mbfd__: modified best fit decreasing based euristic, it searches the optimal solution of microservices' deployment
- __mm1_mg1_omnet__: GA-based algorithm to design the deployment scheme of a fog infrastructure and simulate its performance using Omnet++
- __opt_service__: not-yet working service to implement a Variable Neighborhood Search algorithm top optimize deployment of microservices
- __vns__: variation of neighborhood search algorithm to minimize the object function
