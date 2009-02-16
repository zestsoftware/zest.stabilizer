"""Various actions to fix up unstable.cfg files
"""
import logging
import os

from zest.releaser import utils

import buildoututils
import stabilize

logger = logging.getLogger('unstable')


def develop_to_infrae():
    """Move development eggs from 'develop=' to infrae.subversion"""
    unstable_lines = open('unstable.cfg').read().splitlines()
    buildout_part = buildoututils.extract_parts(unstable_lines,
                                                partname='buildout')
    if not buildout_part:
        logger.debug("No [buildout] part, so I'm not looking for dev eggs")
        return
    (start,
     end,
     directories,
     development_section) = buildoututils.extract_option(
        unstable_lines,
        'develop',
        startline=buildout_part['start'],
        endline=buildout_part['end'])
    if not directories:
        logger.debug("No develop section in [buildout].")
        return
    # Remove develop contents
    new = ['develop =', '']
    unstable_lines[start:end] = new
    contents = '\n'.join(unstable_lines)
    # Add newline at end of file:
    contents += '\n'
    open('unstable.cfg', 'w').write(contents)

    # Write new part
    checkouts = []
    start_dir = os.path.abspath('.')
    for directory in directories:
        logger.debug("Determining svn url for %s...", directory)
        os.chdir(directory)
        url = utils.svn_info()
        checkouts.append(url)
        os.chdir(start_dir)
    stabilize.add_new_part(checkouts, filename='unstable.cfg')

    logger.info("Moved development eggs to infrae.subversion.")
    logger.info("Make sure part %s is actually called.", stabilize.PARTNAME)
    logger.info("Make sure ${%s:eggs} is actually included.",
                stabilize.PARTNAME)
    logger.info("Delete src/ dir from svn and add it to svn:ignore.")


def main():
    logging.basicConfig(level=utils.loglevel(),
                        format="%(levelname)s: %(message)s")
    develop_to_infrae()
