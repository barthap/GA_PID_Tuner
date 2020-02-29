from typing import Tuple, NewType

from config import Config
from genetic.chromosome import Chromosome
from sim.AbstractSimModel import AbstractSimModel, TimeVector, ResponseVector

from control.matlab import *
import matplotlib.pyplot as plt
import numpy as np


class PythonSimulatedModel(AbstractSimModel):
    def __init__(self, cfg: Config, *args):
        super().__init__(*args)
        self.cfg = cfg
        self.supports_threading = True

    @staticmethod
    def _err(y1, y2, delta: float) -> float:
        squares = (y1 - y2) ** 2  # kwadraty uchybu
        return np.sum(squares * delta).astype(float)  # mnożymy razy dt, sumujemy

    def simulate_for_fitness(self, chromosome: Chromosome) -> Tuple[float, TimeVector, ResponseVector]:
        czas_symulacji = self.cfg['simulation_time']  # [s]
        dt = self.cfg['step_time']  # krok symulacji

        ### PID parameters
        kp = chromosome.kp  # gain
        Ti = chromosome.Ti  # integration time
        Td = chromosome.Td  # derivative time
        T = self.cfg['D_T']  # derivative part innertion time constant

        ### PARAMETRY OBIEKTU REGULOWANEGO
        tau = self.cfg['delay']  # opóźnienie
        num = self.cfg['tf_num']  # licznik transmitancji
        den = self.cfg['tf_den']  # mianownik transmitancji
        pade_N = self.cfg['pade_N']  # stopień aproksymacji Padego

        # aproksymacja opóźnienia Padego
        pade_num, pade_den = pade(tau, pade_N)
        tf_delay = tf(pade_num, pade_den)
        tf_obj = tf(num, den)  # transmitancja regulowanego obiektu

        # transmitancje PID G(s) = kp(1 + 1/Ti*s + Td*s/Ts+1)
        tf_P = tf([kp], [1])
        tf_I = tf([1], [Ti, 0])
        tf_D = tf([Td, 0], [T, 1])
        tf_PID = tf_P * (tf([1], [1]) + tf_I + tf_D)

        tf_open = tf_PID * tf_delay * tf_obj
        tf_loop = feedback(tf_open, 1)  # pętla sprzężenia zwrotnego

        time_vec = np.arange(0, czas_symulacji, dt)  # wektor czasu
        y, t = step(tf_loop, T=time_vec)  # symulacja odpowiedzi układu na skok
        y_in, _ = step(tf([1], [1]), T=t)  # symulacja idealnego skoku jednostkowego

        # ISE - integral square error --- całka z e^2 dt = suma[ (y1-y2)^2*dt ] po wszystkich y
        ise = self._err(y, y_in, dt)

        return ise, t, y
