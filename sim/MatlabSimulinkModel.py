import numpy as np
from typing import Tuple

from config import Config
from genetic.chromosome import Chromosome
from sim.AbstractSimModel import AbstractSimModel, TimeVector, ResponseVector
import matlab.engine


class MatlabSimulinkModel(AbstractSimModel):
    def __init__(self, cfg: Config, *args):
        super().__init__(*args)
        self.cfg = cfg
        self.engine = matlab.engine.start_matlab()
        self.engine.cd(r'./matlab',nargout=0)
        print("MATLAB Working directory:", self.engine.pwd())

    def __del__(self):
        self.engine.quit()

    def simulate_for_fitness(self, chromosome: Chromosome) -> Tuple[float, TimeVector, ResponseVector]:
        sim_step = self.cfg['step_time']*1.0
        sim_time = self.cfg['simulation_time']*1.0

        kp = chromosome.kp*1.0
        ti = chromosome.Ti*1.0
        td = chromosome.Td*1.0

        T = self.cfg['D_T']*1.0
        tau = self.cfg['delay']*1.0  # opóźnienie
        num = matlab.double(self.cfg['tf_num'])  # licznik transmitancji
        den = matlab.double(self.cfg['tf_den'])  # mianownik transmitancji

        # trzeba to dodac do workspace żeby Simulink czytał parametry
        self.engine.workspace['sim_step'] = sim_step
        self.engine.workspace['sim_time'] = sim_time
        self.engine.workspace['kp'] = kp
        self.engine.workspace['Ti'] = ti
        self.engine.workspace['Td'] = td
        self.engine.workspace['T'] = T
        self.engine.workspace['tau'] = tau
        self.engine.workspace['num'] = num
        self.engine.workspace['den'] = den

        # uruchom skrypt simulate.m
        result = self.engine.simulate(sim_step,sim_time,kp,ti,td,T,tau,num,den, nargout=3)
        ise: float = result[0]
        mat_t = result[1]
        mat_y = result[2]
        t: TimeVector = np.array([x for x in mat_t])    # konwertuj z formatu Matlab do numpy
        y: ResponseVector = np.array([x for x in mat_y])

        return ise, t, y



