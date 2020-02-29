import numpy as np
from abc import ABC, abstractmethod
from typing import NewType, Tuple

from genetic.chromosome import Chromosome

TimeVector = NewType('TimeVector', np.ndarray)
ResponseVector = NewType('ResponseVector', np.ndarray)


class AbstractSimModel(ABC):
    def __init__(self, *args):
        super().__init__(*args)
        self.supports_threading = False

    @abstractmethod
    def simulate_for_fitness(self, chromosome: Chromosome) -> Tuple[float, TimeVector, ResponseVector]:
        raise NotImplementedError('Model simulation is not implemented!')
