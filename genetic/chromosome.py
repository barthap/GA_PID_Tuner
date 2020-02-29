
class Chromosome:
    def __init__(self, kp: float, Ti: float, Td: float):
        self.kp = kp
        self.Ti = Ti
        self.Td = Td

    def __str__(self):
        return "[Kp: {0:.4f}, Ti: {1:.4f}, Td: {2:.4f}]".format(self.kp, self.Ti, self.Td)
