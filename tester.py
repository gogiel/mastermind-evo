# coding: utf-8

from __init__ import Game, Combination, EvoAlg
from gettext import gettext as _
import argparse
import random
import logging
from numpy import mean, std

DEFAULT_C = 7
DEFAULT_L = 4

eye_catcher = lambda x: x.center(60, '=')

logger = logging.getLogger('tester')
logger.setLevel(logging.INFO)

parser = argparse.ArgumentParser()

parser.add_argument(
    '-c',
    help = _('number of colors (default: %s)') % DEFAULT_C,
    default = DEFAULT_C,
    type = type(DEFAULT_C),
)

parser.add_argument(
    '-s',
    help = _('secret combination (default: random)'),
)

parser.add_argument(
    '-l',
    help = _('length of random secret combination (default: %s)') % DEFAULT_L,
    default = DEFAULT_L,
    type = type(DEFAULT_L),
)

parser.add_argument(
    '-v',
    help = _('shows algorithm debugs'),
    action = 'store_true',
)

args = parser.parse_args()

if not args.v:
    logging.getLogger('algorithm').setLevel(logging.INFO)

counter = 0
attempts = []
evolutions = []

while True:
    counter += 1
    logger.info(eye_catcher(_(' NEW GAME %s ') % counter))
    s = args.s or random.sample(range(args.c) * args.l, args.l)
    game = Game(args.c - 1, Combination.from_symbols(s), EvoAlg)
    game.play()
    attempts.append(game.attempts)
    evolutions.append(game.evolutions)
    logger.info(eye_catcher(_(' STATS AFTER GAME %s ') % counter))
    for d, v in (
        ('Attempts', attempts),
        ('Evolutions', evolutions),
    ):
        logger.info('%s (min max avg dev): %s %s %s %s' % (d, min(v), max(v), mean(v), std(v)))
