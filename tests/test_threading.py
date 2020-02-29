import unittest
from time import sleep
from typing import List, Tuple

from genetic.algorithm import AlgorithmBase
from genetic.algorithms.impl1 import GeneticAlgorithmImpl
from genetic.chromosome import Chromosome
from genetic.simulation import Simulation
from sim.AbstractSimModel import AbstractSimModel, TimeVector, ResponseVector
from sim.PythonSimulatedModel import PythonSimulatedModel


class MockAlgorithm(AlgorithmBase):
    def mutation(self, chromosome: Chromosome) -> Chromosome:
        pass

    def crossover(self, parent1: Chromosome, parent2: Chromosome) -> Chromosome:
        pass

    def selection(self, fitness_values: List[float]) -> List[int]:
        pass

    def fitness(self, ise: float) -> float:
        return ise


class MockModel(AbstractSimModel):

    def __init__(self, *args):
        super().__init__(*args)
        self.supports_threading = False

    def simulate_for_fitness(self, chromosome: Chromosome) -> Tuple[float, TimeVector, ResponseVector]:
        return chromosome.kp, None, None


class ThreadingTests(unittest.TestCase):

    def test_threading(self):
        config = {
            'population_size': 5,
            'threading_enabled': True,
            'num_threads': 3
        }

        model = MockModel()
        algorithm = MockAlgorithm()
        simulation = Simulation(config, model, algorithm)

        simulation.population = [
            Chromosome(1.0, 0.0, 0.0),
            Chromosome(3.0, 0.0, 0.0),
            Chromosome(2.0, 0.0, 0.0),
            Chromosome(5.0, 0.0, 0.0),
            Chromosome(4.0, 0.0, 0.0)
        ]

        simulation.calculate_fitness()
        fitness_std = simulation.fitness_values
        print("Non Threaded", fitness_std)

        simulation.sim_model.supports_threading = True

        simulation.calculate_fitness()
        fitness_thd = simulation.fitness_values
        print("Threaded", fitness_thd)

        self.assertListEqual(fitness_std, fitness_thd)

