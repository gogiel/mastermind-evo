from __future__ import division
from pyevolve import G1DList
from pyevolve import GSimpleGA
from pyevolve import Selectors
from itertools import product
from collections import Counter
from math import log
import logging

import sys

logger = logging.getLogger('algorithm')
logger.setLevel(logging.DEBUG)

cache = {}

#current_population = []

class Color(int):
    pass

class Game:
    def reset(self):
        self.current_population=[]
        self.combinations = []
        self.scores = []
        self.attempts = 0
        self.evolutions = 0


    def __init__(self, colors_count, hidden_combination):
        self.current_population = []
        self.attempts = 0
        self.evolutions = 0
        self.colors_count = colors_count
        self.hidden_combination = hidden_combination
        self.pegs_count = len(hidden_combination)
        self.attempts_count = 0
        self.possibilities = list(
            product(
                range(self.colors_count),
                repeat=self.pegs_count
           )
        )

    def play(self):
        self.reset()
        logger.info("Hidden combination: %s" % self.hidden_combination.__str__())

        while True:
            genome = self.create_genome()
            self.ga = GSimpleGA.GSimpleGA(genome)
            self.ga.setPopulationSize(50)
            self.ga.selector.set(Selectors.GTournamentSelector)
            self.ga.setCrossoverRate(0.9)
            self.ga.setMutationRate(1 / self.pegs_count)
            self.ga.setElitism(True)
            self.ga.setGenerations(500)

            self.ga.evolve()

            best = self.ga.bestIndividual()
            self.current_population = self.ga.getPopulation()
            logger.debug(best)
            answer = Combination([Color(c) for c in best])


            score = answer.score(self.hidden_combination)
            self.attempts += 1
            self.evolutions += self.ga.getCurrentGeneration()

            self.combinations.append(answer)
            self.scores.append(score)

            logger.info("Attempt: %s, Score: %s" % (answer, score))
            if self.win(score):
                logger.info("Win after %d attempts, %d evolutions" % (self.attempts, self.evolutions))
                logger.debug("Combinations played: %s" % self.combinations)
                break

    def win(self, score):
        return score[0] == self.pegs_count

    def entropy(self, combination):
        #print self.ga.getPopulation().__str__()
        combination_string = combination.__str__()
        if combination_string in cache:
            return cache[combination_string]
        XI_i = Counter(
            combination.score(c) for c in self.current_population
        ).values()
        SUM_XI_i = sum(XI_i)
        cache[combination_string] = -sum(
            p_i * log(p_i) for p_i in (
                XI_ibw / SUM_XI_i for XI_ibw in XI_i if XI_ibw
            )
        )
        return cache[combination_string]

    def is_feasible(self, combination):
        for answer, score in zip(self.combinations, self.scores):
            if answer.score(combination) != score:
                return False
        return True

    def create_genome(self):
        genome = G1DList.G1DList(self.pegs_count)
        genome.setParams(rangemin=0, rangemax=self.colors_count)

        def eval_func(chromosome):
            game = self
            combination = Combination([Color(c) for c in chromosome])
        #    print 'PART:'
        #    for c in chromosome:
		#		sys.stdout.write(str(c))
        #    print '\n'

            if not game.is_feasible(combination):
                return 0.0
            return 1.0 + self.entropy(combination)

        genome.evaluator.set(eval_func)
        return genome


class Combination(list):
    def score(self, other):
        first = len([speg for speg, opeg in zip(self, other) if speg == opeg])
        # TODO change it, now it demands 7 colors
        colors_count = max(max(self),max(other))+1
        return first, sum([min(self.count(j), other.count(j)) for j in range(colors_count)]) - first

    def __str__(self):
        return "".join([str(x) for x in self])

    @staticmethod
    def from_symbols(symbols):
        return Combination([Color(int(c)) for c in symbols])