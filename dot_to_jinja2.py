import re

##############################################################################
# DoT to Jinja2 conversion

# Each search string gets compiled into one big alternation, between {{ and
# }}, so we don't need to repeat them in every search.

# NOTE: Javascript allows properties to be separated from their object
# by spaces - e.g. pydata. property.  Jinja2 doesn't.  This can happen
# anywhere an expression is valid - so in interpolation, for loop list
# objects, and in conditions.  The first two are relatively easy to detect
# and correct; the latter isn't.  At this point in time we do not attempt to
# convert these.

patterns = {
    'interpolate': {
        'search': r'=\s*(?P<var>[^}]+?)\s*',
        'replace': r'{{ \g<var> }}'
    },
    'condition': {
        'search': r'\?\s*(?P<cond>[^}?]+?)\s*',
        'replace': r'{% if \g<cond> %}',
    },
    'else': {
        'search': r'\?\?',
        'replace': r'{% else %}',
    },
    'endif': {
        'search': r'\?',
        'replace': r'{% endif %}',
    },
    's_loop_begin': {
        'search': r'~\s*(?P<list>[^:\s]+?)\s*:\s*(?P<var>[^}:\s]+)\s*',
        'replace': r'{% for \g<var> in \g<list> %}'
    },
    's_indexed_loop_begin': {
        'search': (r'~\s*(?P<list>[^:\s]+?)\s*:\s*(?P<var>[^}:\s]+):\s*'
                   +r'(?P<idx>[^}\s]+)\s*'),
        'replace': r'{% for \g<var> in \g<list> %}'
    },
    's_loop_end': {
        'search': r'~',
        'replace': r'{% endfor %}',
    },
    'j_loop_begin': {
        'search': (r'\s*for\s*\(\s*(?:var\s+)?(?P<var>\S+)\s+in\s+'
                   + r'(?P<list>\S+)\s*\)\s*\{\s*''),
        'replace': r'{% for \g<var> in \g<list> %}'
    },
    'j_loop_end': {
        'search': r'\s*}\s*',
        'replace': r'{% endfor %}',
    },
}


def dot_to_jinja(text):
    # The regexes work best across text that's all one block, not split up
    # into lines.  For now, just accept a string.
    assert isinstance(text, str)

    # We have to do translation of Object.keys(...) before DoT to Jinja
    # translation because Object.keys(...) can be used inside DoT expressions.
    text = re.sub(
        r'Object.keys\((?P<dict>[^)]+)\).length',
        r'\g<dict>|length',
        text,
        flags=re.MULTILINE + re.DOTALL
    )

    # DoT allows users to index a for loop with {{~list:var:index}}.  In
    # Jinja2, you can get the loop index with loop.index, so we have to find
    # uses of this and replace both the for loop syntax and then the index
    # variable usage.
    match = re.search(patterns['s_indexed_loop_begin']['search'], text)
    if match:
        # print("Found indexed loop in " + match.group() + ", replacing "
        #     + match.group('idx') + ' with loop.index.'
        #     )
        # Just replace the use of {{=index}} here.  Replacement of for
        # loop itself happens later.
        text =re.sub(
            r'\{\{=\s*' + match.group('idx') + r'\s*\}\}',
            r'{{ loop.index }}',
            text
        )

    # Now do all the substitutions, one at a time.  Because they don't
    # overlap and the Jinja2 expressions can't be misinterpreted as
    # DoT expressions, we don't need to step through in any particular order.
    # As far as we know, touch wood :-)
    # print("Processing text " + text)
    for name, patdata in patterns.items():
        # print("... pattern {n} ('{p}') on text {t}".format(
        #     n=name, p=patdata['search'], t=text
        # ))

        # Now do the substitution
        text = re.sub(
            re.compile(r'\{\{' + patdata['search'] + r'\}\}'),
            patdata['replace'],
            text
        )

    # print(">>> result is" + text)
    return text


"""
import re
from api2.utils import patterns
for p in patterns.values():
    print("testing", p['search'])
    r = re.compile(r'\{\{' + p['search'] + r'\}\}')
"""
