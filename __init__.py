from __future__ import division
from pyevolve import G1DList
from pyevolve import GSimpleGA
from pyevolve import Selectors
from itertools import product
from collections import Counter
from math import log
import logging

logger = logging.getLogger('algorithm')
logger.setLevel(logging.DEBUG)


class Color(int):
    pass


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

class Game:
    def __init__(self, colors_count, hidden_combination, algorithm_class):
        self.attempts_count = 0
        self.pegs_count = len(hidden_combination)
        self.colors_count = colors_count
        self.hidden_combination = hidden_combination
        self.algorithm = algorithm_class()
        self.algorithm.setup(self.colors_count, self.pegs_count)

    def reset(self):
        self.combinations = []
        self.scores = []
        self.attempts = 0
        self.evolutions = 0

    def attempt(self):
        answer = self.algorithm.attempt(self.combinations, self.scores)
        score = answer.score(self.hidden_combination)
        self.attempts += 1
        self.evolutions += self.algorithm.ga.getCurrentGeneration()
        self.combinations.append(answer)
        self.scores.append(score)
        return answer, score

    def play(self):
        self.reset()
        logger.info("Hidden combination: %s" % self.hidden_combination.__str__())

        while True:
            answer, score = self.attempt()
            logger.info("Attempt: %s, Score: %s" % (answer, score))
            if self.win(score):
                logger.info("Win after %d attempts, %d evolutions" % (self.attempts, self.evolutions))
                logger.debug("Combinations played: %s" % self.combinations)
                break

    def win(self, score):
        return score[0] == self.pegs_count

    def pegs_count(self):
        return 4

class Algorithm:
    def setup(self, colors_count, pegs_count):
        raise NotImplementedError

    def attempt(self, before_combinations, old_scores):
        raise NotImplementedError


class EvoAlg(Algorithm):
    def entropy(self, combination):
        XI_i = Counter(
            combination.score(c) for c in filter(self.is_feasible, self.possibilities)
        ).values()
        SUM_XI_i = sum(XI_i)
        return -sum(
            p_i * log(p_i) for p_i in (
                XI_ibw / SUM_XI_i for XI_ibw in XI_i if XI_ibw
            )
        )

    def setup(self, colors_count, pegs_count):
        self.colors_count = colors_count
        self.pegs_count = pegs_count
        self.possibilities = list(
            product(
                range(self.colors_count),
                repeat=self.pegs_count
           )
        )

    def attempt(self, before_combinations, old_scores):
        self.answers = before_combinations
        self.scores = old_scores
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
        logger.debug(best)
        return Combination([Color(c) for c in best])

    def create_genome(self):
        genome = G1DList.G1DList(self.pegs_count)
        genome.setParams(rangemin=0, rangemax=self.colors_count)

        def eval_func(chromosome):
            game = self
            combination = Combination([Color(c) for c in chromosome])
            if not game.is_feasible(combination):
                return 0.0
            return 1.0 + self.entropy(combination)

        genome.evaluator.set(eval_func)
        return genome

    def is_feasible(self, combination):
        for answer,score in zip(self.answers,self.scores):
            if answer.score(combination) != score:
                return False
        return True

if __name__ == '__main__':
    game = Game(6, Combination.from_symbols('3211'), EvoAlg)
    game.play()
