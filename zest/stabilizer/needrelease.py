"""Show last logs of our packages so you can see which are releasable.
"""
import logging
from commands import getoutput

from zest.releaser import utils

from zest.stabilizer import stabilize

logger = logging.getLogger('stabilize')
PARTNAME = 'ourpackages'


def main():
    logging.basicConfig(level=utils.loglevel(),
                        format="%(levelname)s: %(message)s")
    stabilize.check_for_files()
    directories = stabilize.development_eggs()
    for directory in directories:
        print directory
        print getoutput('svn up %s' % directory)
        print getoutput('svn log --limit 1 %s' % directory)
        print
        print
