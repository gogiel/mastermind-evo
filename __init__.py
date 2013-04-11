from pyevolve import G1DList
from pyevolve import GSimpleGA
from itertools import product
import logging

logger = logging.getLogger('algorithm')
logger.setLevel(logging.INFO)

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

    def attempt(self):
        answer = self.algorithm.attempt(self.combinations, self.scores)
        score = answer.score(self.hidden_combination)
        self.attempts += 1
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
                logger.info("Win after %d attempts" % self.attempts)
                logger.info("Combinations played: %s" % self.combinations)
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
    def setup(self, colors_count, pegs_count):
        self.colors_count = colors_count
        self.pegs_count = pegs_count

    def attempt(self, before_combinations, old_scores):
        self.answers = before_combinations
        self.scores = old_scores
        genome = self.create_genome()
        ga = GSimpleGA.GSimpleGA(genome)
        ga.evolve()
        best =  ga.bestIndividual()
        logger.info(best)
        return Combination([Color(c) for c in best])

    def create_genome(self):
        genome = G1DList.G1DList(self.pegs_count)
        genome.setParams(rangemin=0, rangemax=self.colors_count)

        def eval_func(chromosome):
            game = self
            combination = Combination([Color(c) for c in chromosome])
            if not game.is_feasible(combination):
                return 0.0
            entropy = 0.0 # TODO
            return 1.0 + entropy

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
