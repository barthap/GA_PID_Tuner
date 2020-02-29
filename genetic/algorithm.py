import random
from abc import ABC, abstractmethod
from typing import List

import listtools
from config import Config
from genetic.chromosome import Chromosome


class AlgorithmBase(ABC):
    def __init__(self, *args):
        super().__init__(*args)

    @abstractmethod
    def mutation(self, chromosome: Chromosome) -> Chromosome:
        raise NotImplementedError('Mutation is not implemented!')

    @abstractmethod
    def crossover(self, parent1: Chromosome, parent2: Chromosome) -> Chromosome:
        raise NotImplementedError('Crossover is not implemented!')

    # Selekcja
    @abstractmethod
    def selection(self, fitness_values: List[float]) -> List[int]:
        raise NotImplementedError('Selection is not implemented!')

    # Funkcja przystosowania
    def fitness(self, ise: float) -> float:
        return 1.0 / ise
