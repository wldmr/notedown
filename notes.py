#!/bin/env python3

import sys
import re
from glob import iglob
from argparse import ArgumentParser

def debug(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def get_arguments():
    parser = ArgumentParser(description="Handle notes, my way.")
    subparsers = parser.add_subparsers(title="Commands")

    mktags = subparsers.add_parser("tags", help="create tags file")
    mktags.set_defaults(func=cmd_mktags)

    parser.set_defaults(func=cmd_mktags)
    return parser.parse_args()

class AnchorParser:
    """This is what an |Anchor definition| looks like.

    Can be escaped by either prepending the first slashes with
    a backslash (`\`).

    The emitted instances have the following attributes:

    :pos: position of the first character of the anchor within the string
    :start: delimiter that comes before the anchor text
    :end: delimiter that comes after the anchor text
    :text: the actual anchor string (without delimiters)

    Note that ``start``+``text``+``end`` are equal the
    exact string found in the file.
    """

    anchor_start = r'((?<!\\)\|)'
    anchor_end   = r'((?<!\\)\|)'
    anchor_text  = r'(.+?)'

    def __init__(self, start=None, end=None, text=None):
        anchordef = ''.join((
            start or self.anchor_start,
            text  or self.anchor_text,
            end   or self.anchor_end))
        self.anchordef = re.compile(anchordef, flags=re.M|re.S)

    def parse(self, txt, **default_values):
        """Extract ``Anchors``s from ``txt``.

        :txt: string that contains anchor definitions
        :default_values: values that each anchor gets; use
                         this for any information that can not be gleaned
                         from ``txt`` (such as the file path).
                         Values that *can* be gleaned from ``txt``
                         override values given here.

        :returns: generator of ``Anchor``'s
        """
        matches = self.anchordef.finditer(txt) or []
        for match in matches:
            anchor       = Anchor(**default_values)
            anchor.pos   = match.start()
            anchor.start = match.group(1)
            anchor.end   = match.group(3)
            anchor.text  = match.group(2)
            yield anchor

class Anchor:
    """Represents a location within a piece of text."""
    def __init__(self, **values):
        """Create an anchor."""
        self.__dict__.update(values)

class AnchorTagRenderer:
    """Renders a collection of ``Ànchors`` to a `vim tagfile`_.

    .. _`vim tagfile`: <http://usevim.com/2013/01/18/tags/>
    """

    tagline = '{name}\t{path}\t{address}\n'
    spaces = re.compile(r'\s+')

    def render_anchor(self, anchor):
        """Return a single tagfile line (including newline at the end).

        ``anchor`` must have the following attributes:
        ``text``, ``path``, ``start``, ``end``.
        If not, throw hissy fit (in the Form of ``AttributeError``).
        """
        # Collapse spaces (including newlines)
        name = anchor.text.strip()
        name = self.spaces.sub(' ', name)

        # The file path. We leave it alone.
        path = anchor.path

        # Replace some characters that have special meaning to the ex search 
        # pattern, so we get a 'literal' string. TODO: Do this properly, for 
        # all special characters; this is bound to blow up with some weird anchor 
        # string or another.
        address = anchor.start + anchor.text + anchor.end
        address = address.replace('\n', r'\n')
        address = address.replace('/', r'\/')
        address = '/' + address + '/'
        return self.tagline.format(
            name=name,
            path=path,
            address=address)

    def render_anchors(self, anchors):
        """Take an iterable of ``Anchor``s and return a sorted list of tagfile lines."""
        tags = {self.render_anchor(a) for a in anchors}
        return sorted(tags)


def cmd_mktags():
    parser = AnchorParser()

    anchors = set()
    for filename in iglob('*.txt'):
        with open(filename) as f:
            txt = f.read()
            new_anchors = parser.parse(txt, path=filename)
            anchors.update(new_anchors)

    renderer = AnchorTagRenderer()
    lines = renderer.render_anchors(anchors)
    with open('tags', 'w') as tf:
        tf.writelines(lines)

if __name__ == "__main__":
    args = get_arguments()
    args.func()
