"""Stabilize unstable.cfg's development eggs into tag checkouts for stable.cfg
"""
import difflib
import logging
import sys
import os
from pkg_resources import parse_version

from zest.releaser import utils

import buildoututils

logger = logging.getLogger('stabilize')
PARTNAME = 'ourpackages'


def check_for_files():
    """Make sure stable.cfg and unstable.cfg are present"""
    required_files = ['stable.cfg', 'unstable.cfg']
    available = os.listdir('.')
    for required in required_files:
        if required not in available:
            logger.critical("Required file %s not found.", required)
            sys.exit()
    logger.debug("stable.cfg and unstable.cfg found.")


def development_eggs():
    """Return list of development egg directories from unstable.cfg.

    Zest assumption: we've placed them in src/*

    """
    unstable_lines = open('unstable.cfg').read().split('\n')
    part = buildoututils.extract_parts(unstable_lines,
                                       partname=PARTNAME)
    if not part:
        logger.error("No [%s] part, unstable.cfg isn't up-to-date.",
                     PARTNAME)
        return
    (start,
     end,
     specs,
     url_section) = buildoututils.extract_option(
        unstable_lines,
        'urls',
        startline=part['start'],
        endline=part['end'])
    development_eggs = []
    for spec in specs:
        url, name = spec.split()
        development_eggs.append('src/%s' % name)
    return development_eggs


def determine_tags(directories):
    """Return desired tags for all development eggs"""
    results = []
    start_dir = os.path.abspath('.')
    for directory in directories:
        logger.debug("Determining tag for %s...", directory)
        os.chdir(directory)
        version = utils.extract_version()
        logger.debug("Current version is %r.", version)
        available_tags = utils.available_tags()
        # We seek a tag that's the same or less than the version as determined
        # by setuptools' version parsing. A direct match is obviously
        # right. The 'less' approach handles development eggs that have
        # already been switched back to development.
        available_tags.reverse()
        found = available_tags[0]
        parsed_version = parse_version(version)
        for tag in available_tags:
            parsed_tag = parse_version(tag)
            parsed_found = parse_version(found)
            if parsed_tag == parsed_version:
                found = tag
                logger.debug("Found exact match: %s", found)
                break
            if (parsed_tag >= parsed_found and
                parsed_tag < parsed_version):
                logger.debug("Found possible lower match: %s", tag)
                found = tag
        url = utils.svn_info()
        name, base = utils.extract_name_and_base(url)
        full_tag = base + 'tags/' + found
        logger.debug("Picked tag %r for %s (currently at %r).",
                     full_tag, name, version)
        results.append(full_tag)
        os.chdir(start_dir)
    return results


def url_list():
    """Return version lines"""
    stable_lines = open('stable.cfg').read().split('\n')
    part = buildoututils.extract_parts(stable_lines, partname=PARTNAME)
    if not part:
        return []
    (start,
     end,
     specs,
     url_section) = buildoututils.extract_option(
        stable_lines,
        'urls',
        startline=part['start'],
        endline=part['end'])
    # http://somethinglong/tags/xyz something
    interesting = [spec.split('tags/')[1] for spec in specs]
    logger.debug("Version lines: %s", interesting)
    return interesting


def remove_old_part():
    """If PARTNAME already exists, remove it"""
    stable_lines = open('stable.cfg').read().split('\n')
    old_part = buildoututils.extract_parts(stable_lines, partname=PARTNAME)
    if old_part:
        del stable_lines[old_part['start']:old_part['end']]
    contents = '\n'.join(stable_lines)
    open('stable.cfg', 'w').write(contents)
    logger.debug("New stable.cfg written: old part removed.")


def add_new_part(tags, filename='stable.cfg'):
    """Add PARTNAME part"""
    new = ['[%s]' % PARTNAME]
    new.append('recipe = infrae.subversion >= 1.4')
    checkouts = []
    for tag in tags:
        name, base = utils.extract_name_and_base(tag)
        checkouts.append('%s %s' % (tag, name))
    lines = buildoututils.format_option('urls', checkouts)
    new += lines

    new.append('as_eggs = true')
    new.append('location = src')
    new.append('')
    new.append('')
    lines = open(filename).read().splitlines()
    first = buildoututils.extract_parts(lines)[0]
    insertion_point = first['end']
    lines[insertion_point:insertion_point] = new
    contents = '\n'.join(lines)
    # Add newline at end of file:
    contents += '\n'
    open(filename, 'w').write(contents)
    logger.debug("New %s written. Added %s", filename, new)


def check_stable():
    """Check whether common tasks are handled"""
    logger.info("Make sure part %s is actually called.", PARTNAME)
    logger.info("Make sure ${%s:eggs} is actually included.", PARTNAME)


def insert_msg_into_history(msg):
    filename = utils.history_file()
    if not filename:
        return
    lines = open(filename).read().splitlines()
    headings = utils.extract_headings_from_history(lines)
    if not headings:
        return
    # Hardcoded zest assumptions.
    target_line = headings[0]['line'] + 3
    if len(lines) < target_line:
        return
    if 'nothing yet' in lines[target_line].lower():
        del lines[target_line]
    # Msg formatting:
    msg = msg[:]
    msg = ['  %s' % line for line in msg]
    msg += ['']
    firstline = msg[0]
    firstline = '-' + firstline[1:]
    msg[0] = firstline
    lines[target_line:target_line] = msg
    contents = '\n'.join(lines)
    # Add newline at end of file:
    contents += '\n'
    open(filename, 'w').write(contents)
    logger.debug("Written change to history file")


def main():
    logging.basicConfig(level=utils.loglevel(),
                        format="%(levelname)s: %(message)s")
    check_for_files()
    directories = development_eggs()
    if not directories:
        sys.exit()
    old_situation = url_list()
    tags = determine_tags(directories)
    remove_old_part()
    add_new_part(tags)
    new_situation = url_list()
    diff = list(difflib.ndiff(old_situation, new_situation))
    logger.debug("Diff: %s", diff)
    check_stable()

    msg = ["Stabilized buildout to most recent svn tags of our packages:"]
    msg += diff
    insert_msg_into_history(msg)
    msg = '\n'.join(msg)
    
    utils.show_diff_offer_commit(msg)
