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
    anchor_start = r'(?<!\\)\|'
    anchor_end   = r'(?<!\\)\|'
    anchor_text  = r'.+?'
    """This is what an |Anchor definition| looks like.

    Can be escaped by either prepending the first slashes with
    a backslash (`\`).
    """

    def __init__(self, start=None, end=None, text=None):
        anchordef = r'({})({})({})'.format(
            start or self.anchor_start,
            text  or self.anchor_text,
            end   or self.anchor_end)
        self.anchordef = re.compile(anchordef, flags=re.M|re.S)

    def parse_anchors(self, path):
        """Extract ``Anchors``s from file at ``path``.

        :path: string that contains anchor definitions
        :returns: generator of ``Anchor``'s
        """
        with open(path) as f:
            txt = f.read()
            matches = self.anchordef.finditer(txt) or []
            for match in matches:
                yield Anchor(
                    path  = path,
                    pos   = match.start(),
                    start = match.group(1),
                    end   = match.group(3),
                    text  = match.group(2))

class Anchor:
    def __init__(self, path, pos, start, end, text):
        """Create an anchor.

        :path: path to the file the anchor is defined in
        :pos: position of the first character of the anchor within the file
        :start: delimiter that comes before the anchor text
        :end: delimiter that comes after the anchor text
        :text: the actual anchor string (without delimiters)
        """
        self.path = path
        self.pos = pos
        self.start = start
        self.end = start
        self.text = text

class AnchorTagRenderer:

    tagline = '{name}\t{path}\t{address}\n'
    spaces = re.compile(r'\s+')

    def __init__(self, tagfile='tags'):
        self.tagfile = tagfile

    def render(self, anchors, tagfile=None):
        """Take an iterable of ``Anchor``s and write them out to the tagfile."""
        tags = set()
        for a in anchors:
            # Collapse spaces (including newlines)
            name = a.text.strip()
            name = self.spaces.sub(' ', name)

            # The file path. We leave it alone.
            path = a.path

            # Replace some characters that have special meaning to the ex search 
            # pattern, so we get a 'literal' string. TODO: Do this properly, for 
            # all special characters; this is bound to blow up with some weird anchor 
            # string or another.
            address = a.start + a.text + a.end
            address = address.replace('\n', r'\n')
            address = address.replace('/', r'\/')
            address = '/' + address + '/'

            tags.add(self.tagline.format(
                name=name,
                path=path,
                address=address))

        open(tagfile or self.tagfile, 'w').writelines(sorted(tags))


def cmd_mktags():
    parser = AnchorParser()

    anchors = set()
    for filename in iglob('*.txt'):
        anchors.update(parser.parse_anchors(filename))

    renderer = AnchorTagRenderer()
    renderer.render(anchors)

if __name__ == "__main__":
    args = get_arguments()
    args.func()
