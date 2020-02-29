import random
from typing import List

import listtools
from config import Config
from genetic.algorithm import AlgorithmBase
from genetic.chromosome import Chromosome


class GeneticAlgorithmImpl(AlgorithmBase):
    def __init__(self, config: Config, *args):
        super().__init__(*args)
        self.config = config

    # Mutation
    def mutation(self, chromosome: Chromosome) -> Chromosome:
        random.seed()
        max_P_value = self.config['max_gain_value']
        max_I_value = self.config['max_integral_value']
        max_D_value = self.config['max_derivative_value']

        if random.random() < self.config['mutation_probability'] / 3:
            if random.random() < 1/2:
                chromosome.kp = chromosome.kp + random.random() / 10.0 * max_P_value
            else:
                chromosome.kp = chromosome.kp - random.random() / 10.0 * max_P_value
        if chromosome.kp < 0 or chromosome.kp > max_P_value:
            chromosome.kp = random.random() * max_P_value

        elif random.random() < self.config['mutation_probability'] * 2 / 3:
            if random.random() < 1 / 2:
                chromosome.Ti = chromosome.Ti + random.random() / 10.0 * max_I_value
            else:
                chromosome.Ti = chromosome.Ti - random.random() / 10.0 * max_I_value
        if chromosome.Ti < 0 or chromosome.Ti > max_I_value:
            chromosome.Ti = random.random() * max_I_value

        elif random.random() < self.config['mutation_probability']:
            if random.random() < 1 / 2:
                chromosome.Td = chromosome.Td + random.random() / 10.0 * max_D_value
            else:
                chromosome.Td = chromosome.Td - random.random() / 10.0 * max_D_value
        if chromosome.Td < 0 or chromosome.Td > max_D_value:
            chromosome.Td = random.random() * max_D_value

        return chromosome

    # Crossover
    def crossover(self, parent1: Chromosome, parent2: Chromosome) -> Chromosome:
        random.seed()

        if random.random() > self.config['crossover_rate']:
            return parent1
        else:
            # random combination crossover
            number = random.random()
            if number < 1.0 / 6:
                return Chromosome(parent1.kp, parent2.Ti, parent2.Td)
            elif number < 2.0 / 6:
                return Chromosome(parent2.kp, parent1.Ti, parent1.Td)
            elif number < 3.0 / 6:
                return Chromosome(parent1.kp, parent2.Ti, parent1.Td)
            elif number < 4.0 / 6:
                return Chromosome(parent1.kp, parent1.Ti, parent2.Td)
            elif number < 5.0 / 6:
                return Chromosome(parent2.kp, parent1.Ti, parent2.Td)
            else:
                return Chromosome(parent2.kp, parent2.Ti, parent2.Td)

    # Selection
    def selection(self, fitness_values: List[float]) -> List[int]:

        probabilities = listtools.normListSumTo(fitness_values, 1)
        parent_indices = []
        random.seed()
        parent1_probability = random.random()
        parent2_probability = random.random()

        summ = 0
        for i in range(self.config['population_size']):
            if len(parent_indices) == 2:
                break
            next_sum = summ + probabilities[i]
            if next_sum >= parent1_probability >= summ:
                parent_indices.append(i)
            if next_sum >= parent2_probability >= summ:
                parent_indices.append(i)
            summ = next_sum
        return parent_indices

    def fitness(self, ise: float) -> float:
        return 1.0/(ise - self.config['delay'])
