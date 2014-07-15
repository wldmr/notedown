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

class Tag:
    tagdef = re.compile(r'(?<!\\|:)//(.+?)//', flags=re.M|re.S)
    """This is what a //tag definition// looks like.

    Can be escaped by either prepending the first slashes with
    either ``\`` or a ``:`` (so URIs like ``http://...``
    don't become tag definitions).
    """

    spaces = re.compile(r'\s+')

    @classmethod
    def make_tags(Cls, path):
        """Extract ``Tag``'s from file at ``path``.

        :path: string that contains tag definitions
        :returns: set of ``Tag``'s
        """
        tags = set()
        with open(path) as f:
            txt = f.read()
            matches = Cls.tagdef.finditer(txt) or []
            for match in matches:
                namestring = match.group(1)
                fullmatch = match.group(0)
                tag = Cls(namestring, path, fullmatch)
                tags.add(tag)
        return tags

    def __init__(self, name, path, address):
        """Create a tag.

        :name: the tag string (can contain spaces)
        :path: path to the file the tag is defined in
        :address: ``ex``-command to find the definition of the tag
        """
        # Collapse spaces (including newlines)
        self.name = name.strip()
        self.name = self.spaces.sub(' ', self.name)

        # The file path. We leave it alone.
        self.path = path

        # Replace some characters that have special meaning to the ex search 
        # pattern, so we get a 'literal' string. TODO: Do this properly, for 
        # all special characters; this is bound to blow up with some weird tag 
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
        filetags = [str(t) for t in Tag.make_tags(filename)]
        tags = tags.union(filetags)
        print(tags)

    with open('tags', 'w') as tagfile:
        tagfile.writelines(sorted(tags))

if __name__ == "__main__":
    args = get_arguments()
    args.func()
