# Small utility methods.
import logging
import re

logger = logging.getLogger('utils')

WRONG_IN_VERSION = ['svn', 'dev', '(']


def extract_option(buildout_lines, option_name, startline=None, endline=None):
    """Return info on an option (like 'develop=...').

    Return start/end line numbers, actual option lines and a list of
    options.
    """
    pattern = re.compile(r"""
    ^%s        # Line that starts with the option name
    \W*=       # Followed by an '=' with possible whitespace before it.
    """ % option_name, re.VERBOSE)
    line_number = 0
    first_line = None
    if startline is not None:
        logger.debug("Searching in specific lines: %s",
                     '\n'.join(buildout_lines[startline:endline]))

    for line in buildout_lines:
        if startline is not None:
            if line_number < startline or line_number > endline:
                line_number += 1
                continue
        match = pattern.search(line)
        if match:
            logger.debug("Matching %s line found: %r", option_name, line)
            start = line_number
            first_line = line
            break
        line_number += 1
    if not first_line:
        logger.error("'%s = ....' line not found.", option_name)
        return (None, None, None, None)
    option_values = [first_line.split('=')[1]]
    for line in buildout_lines[start + 1:]:
        line_number += 1
        if ('=' in line or '[' in line):
            if not '#egg=' in line:
                end = line_number
                break
        option_values.append(line)
    option_values = [item.strip() for item in option_values
                        if item.strip()]
    logger.info("Found option values: %r.", option_values)
    option_section = buildout_lines[start:end]
    return (start,
            end,
            option_values,
            option_section)


def extract_parts(buildout_lines, partname=None):
    """Return info on the parts (like [development]) in the buildout.

    Return list of dicts with start/end line numbers, part name and the
    actual part lines.
    """
    results = []
    pattern = re.compile(r"""
    ^\[          # A '[' at the start of a line
    \S+          # Followed by one continuous word
    \]           # Closing ']'
    \W*$         # Followed by optional whitespace and nothing more.
    """, re.VERBOSE)
    line_number = 0
    start = None
    name = None
    # TODO below
    for line in buildout_lines:
        match = pattern.search(line)
        if match:
            # Handle previous part if we already have some data.
            if start is not None:
                results.append(dict(start=start,
                                   end=line_number,
                                   name=name))
            logger.debug("Matching line found: %r", line)
            line = line.strip()
            line = line.replace('[', '')
            line = line.replace(']', '')
            name = line
            start = line_number
        line_number += 1
    # Handle last part
    results.append(dict(start=start,
                       end=line_number,
                       name=name))
    if partname is not None:
        for result in results:
            if result['name'] == partname:
                return result
        return None
    return results


def format_option(name, options):
    """Return lines with formatted option."""
    lines = ['%s =' % name]
    for option in options:
        if option.startswith('#'):
            # Comments must start in the first column, so don't indent them.
            lines.append(option)
        else:
            lines.append('    %s' % option)
    lines.append('')
    return lines
