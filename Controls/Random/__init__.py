from libdesklets.controls import Control

from IRandom import IRandom

import random


#
# Control for random-related stuff.
#
class Random(Control, IRandom):

    def __init__(self):

        self.__sequence = ""
        Control.__init__(self)
        

    def __get_randrange(self):
        start = self.__sequence[0]
        stop = self.__sequence[1]
        step = self.__sequence[2]
        return random.randrange(start, stop, step)

    def __get_randint(self):
        a = self.__sequence[0]
        b = self.__sequence[1]
        return random.randint(a, b)

    def __get_choice(self):
        return random.choice(self.__sequence)

    def __get_sample(self):
        population =  self.__sequence[0]
        k = self.__sequence[1]
        return random.sample(population, k)

    def __get_random(self):
        return random.random()

    def __get_uniform(self):
        a = self.__sequence[0]
        b = self.__sequence[1]
        return random.uniform(a, b)

    def __get_betavariate(self):
        alpha = self.__sequence[0]
        beta = self.__sequence[1]
        return random.betavariate(alpha, beta)

    def __get_expovariate(self):
        lambd = self.__sequence[0]
        return random.expovariate(lambd)

    def __get_gammavariate(self):
        alpha = self.__sequence[0]
        beta = self.__sequence[1]
        return random.gammavariate(alpha, beta)

    def __get_gauss(self):
        mu = self.__sequence[0]
        sigma = self.__sequence[1]
        return random.gauss(mu, sigma)

    def __get_lognormvariate(self):
        mu = self.__sequence[0]
        sigma = self.__sequence[1]
        return random.lognormvariate(mu, sigma)

    def __get_normalvariate(self):
        mu = self.__sequence[0]
        sigma = self.__sequence[1]
        return random.normalvariate(mu, sigma)

    def __get_vonmisesvariate(self):
        mu = self.__sequence[0]
        kappa = self.__sequence[1]
        return random.vonmisesvariate(mu, kappa)

    def __get_paretovariate(self):
        alpha = self.__sequence[0]
        return random.paretovariate(alpha)

    def __get_weibullvariate(self):
        alpha = self.__sequence[0]
        beta = self.__sequence[1]
        return random.weibullvariate(alpha, beta)

    def __get_sequence(self):
        return self.__sequence

    def __set_sequence(self, sequence):
        self.__sequence = sequence



    randrange       = property(__get_randrange, doc = "Return a randomly selected element from range(start, stop, step). Sequence: (start, stop, step).")
    randint         = property(__get_randint, doc = "Return a random integer N such that a <= N <= b. Sequence: (a, b).")
    choice          = property(__get_choice, doc = "Return a random element from the non-empty sequence seq. Sequence: (seq). ")
    sample          = property(__get_sample, doc = "Return a k length list of unique elements chosen from the population sequence. Sequence: (population, k).")
    random          = property(__get_random, doc = "Return the next random floating point number in the range [0.0, 1.0). Sequence: ().")
    uniform         = property(__get_uniform, doc = "Return a random real number N such that a <= N < b. Sequence: (a, b).")
    betavariate     = property(__get_betavariate, doc = "Beta distribution. Conditions on the parameters are alpha > 0 and beta > 0. Returned values range between 0 and 1. Sequence: (alpha, beta).")
    expovariate     = property(__get_expovariate, doc = "Exponential distribution. lambd is 1.0 divided by the desired mean. Sequence: (lambd, ).")
    gammavariate    = property(__get_gammavariate, doc = "Gamma distribution. (Not the gamma function!) Conditions on the parameters are alpha > 0 and beta > 0. Sequence: (alpha, beta).")
    gauss           = property(__get_gauss, doc = "Gaussian distribution. mu is the mean, and sigma is the standard deviation. Sequence: (mu, sigma).")
    lognormvariate  = property(__get_lognormvariate, doc = "Log normal distribution. Sequence: (mu, sigma).")
    normalvariate   = property(__get_normalvariate, doc = "Normal distribution. mu is the mean, and sigma is the standard deviation. Sequence: (mu, sigma).")
    vonmisesvariate = property(__get_vonmisesvariate, doc = "mu is the mean angle, expressed in radians between 0 and 2*pi, and kappa is the concentration parameter, which must be greater than or equal to zero. Sequence: (mu, kappa).")
    paretovariate   = property(__get_paretovariate, doc = "Pareto distribution. alpha is the shape parameter. Sequence: (alpha, ).")
    weibullvariate  = property(__get_weibullvariate, doc = "Weibull distribution. alpha is the scale parameter and beta is the shape parameter. Sequence: (alpha, beta).")
    sequence        = property(__get_sequence, __set_sequence, doc = "The sequence/tuple to be used.")


def get_class(): return Random
