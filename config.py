import multiprocessing
from typing import Dict, Any

Config = Dict[str, Any]  # definicja typu

config: Config = {
    # overall config
    'population_size' : 15,
    'max_runs': 50,
    'max_gain_value' : 10,
    'max_integral_value': 5,
    'max_derivative_value': 10,

    # genetic config
    'mutation_probability': .1,
    'crossover_rate': .9,

    # model sim config
    'step_time': 0.01,              # integration step
    'simulation_time': 25,
    'pade_N': 4,                    # Pade approx level
    'D_T': 0.01,                    # Derivative time constant

    # plant config
    'tf_num': [1],          # Transfer function numerator
    'tf_den': [5, 1],       # Transfer function denominator
    'delay': 1.0,           # Transfer function delay

    # multithreading config
    'threading_enabled': False,
    'num_threads': multiprocessing.cpu_count()
}