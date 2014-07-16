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

    mktags = subparsers.add_parser("tag", help="create tags file")
    mktags.set_defaults(func=cmd_mktags)

    return parser.parse_args()

class Anchor:
    anchordef = re.compile(r'(?<!\\)\|(.+?)\|', flags=re.M|re.S)
    """This is what an |Anchor definition| looks like.

    Can be escaped by either prepending the first slashes with
    a backslash (`\`).
    """

    spaces = re.compile(r'\s+')

    @classmethod
    def parse_anchors(Cls, path):
        """Extract ``Anchors``s from file at ``path``.

        :path: string that contains anchor definitions
        :returns: set of ``Anchor``'s
        """
        anchors = set()
        with open(path) as f:
            txt = f.read()
            matches = Cls.anchordef.finditer(txt) or []
            for match in matches:
                namestring = match.group(1)
                fullmatch = match.group(0)
                anchor = Cls(namestring, path, fullmatch)
                anchors.add(anchor)
        return anchors

    def __init__(self, name, path, address):
        """Create a anchor.

        :name: the anchor string (can contain spaces)
        :path: path to the file the anchor is defined in
        :address: ``ex``-command to find the definition of the anchor
        """
        # Collapse spaces (including newlines)
        self.name = name.strip()
        self.name = self.spaces.sub(' ', self.name)

        # The file path. We leave it alone.
        self.path = path

        # Replace some characters that have special meaning to the ex search 
        # pattern, so we get a 'literal' string. TODO: Do this properly, for 
        # all special characters; this is bound to blow up with some weird anchor 
        # string or another.
        address = address
        address = address.replace('\n', r'\n')
        address = address.replace('/', r'\/')
        self.address = '/' + address + '/'

    def __str__(self):
        return '{}\t{}\t{}\n'.format(self.name, self.path, self.address)

def cmd_mktags():
    tags = set()
    for filename in iglob('*.txt'):
        filetags = [str(t) for t in Anchor.parse_anchors(filename)]
        tags = tags.union(filetags)

    with open('tags', 'w') as tagfile:
        tagfile.writelines(sorted(tags))

if __name__ == "__main__":
    args = get_arguments()
    args.func()
