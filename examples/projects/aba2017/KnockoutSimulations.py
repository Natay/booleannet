import os
import json

# import directly from booleannet repo
os.chdir('../../..')
print(os.listdir())
# Simulation Parameters
import boolean2
from boolean2 import util

os.chdir('./pro')
# Boolean Rules
text = open('ABAC2017.txt').read()
# Simulations
repeat = 2500
# number of Time Steps
steps = 30
targets = ['CPK213', 'HATPase', 'NOGC1', 'NAD', 'ABA', 'Microtubule', 'Depolar', 'InsP3', 'SphK12', 'ABH1', 'InsP6', 'CIS', 'AnionEM', 'GAPC',
           'KEfflux', 'H2OEfflux', 'VPpase', 'PP2CA', 'MRP5', 'CPK23', 'Vacidification', 'DAG', 'ROP11', 'NO', 'pHc', 'PIP21', 'PEPC', 'NitrocGMP',
           'HAB1', 'DAGK', 'PLDd', 'PC', 'CPK6', 'PA', 'PLDa', 'PLC', 'PI3P5K', 'ROS', 'AtRAC1', 'OST1', 'cGMP', 'Ca2ATPase', 'GCR1', 'RCN1', 'PIP2',
           'QUAC1', 'S1P', 'Malate', 'KOUT', 'NADPH', 'MAPK912', 'KEV', 'SCAB1', 'CaIM', 'TCTP', 'VATPase', 'GPA1', 'PtdIns35P2', 'GTP', 'GEF1410', 'ARP23',
           'PtdInsP4', 'Sph', 'ABI1', 'NIA12', 'ADPRc', 'RCARs', 'PtdInsP3', 'Nitrite', 'ABI2', 'SPP1', 'RBOH', 'Actin', 'ERA1', 'NtSyp121', 'Ca2c', 'GHR1',
           'cADPR', 'SLAH3', 'SLAC1']

def runSimulations(targets, steps, repeat, knockouts=True):
    data = {}
    for target in targets:
        if knockouts is True:
            mtext = boolean2.modify_states(text=text, turnoff=target)
            fname = 'knockouts_py3.json'
        else:
            mtext = boolean2.modify_states(text=text, turnon=target)
            fname = 'overexpression_py3.json'
        model = boolean2.Model(mode='async', text=mtext)
        coll = util.Collector()
        for i in range(repeat):
            model.initialize(missing=util.randbool)
            model.iterate(steps=steps)
            coll.collect(states=model.states, nodes='Closure')
        data[target] = {'Timesteps': coll.get_averages(normalize=True)}
        data[target]['Closure AUC'] = sum(data[target]['Timesteps']['Closure'])
    with open(fname, 'w') as fp:
        json.dump(data, fp)

if __name__ == '__main__':
    runSimulations(targets, steps, repeat, knockouts=True)
