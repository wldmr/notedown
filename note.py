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

def cmd_mktags():
    class rgx:
        spaces = re.compile(r'\s+')
        tag = re.compile(r'(?<!\\|:)//(.+?)//', flags=re.M|re.S)
        # Every string //like this// is a tag, but only if the start of the 
        # pattern isn't prefixed with a '\' (to generically escape it) or a ':' 
        # (because URIs may have a "http://..." part).

    def tagname(string):
        """Collapse spaces"""
        txt = string.strip()
        txt = rgx.spaces.sub(' ', txt)
        return txt

    tagline = '{}\t{}\t{}\n'

    tags = set()
    for filename in iglob('*.txt'):
        with open(filename) as f:
            txt = f.read()
            matches = rgx.tag.finditer(txt) or []
            for match in matches:
                s = match.group(1)
                address = match.group(0)
                # Replace newline character with the string '\n',
                # so it works in the search pattern.
                address = address.replace('\n', r'\n')
                address = address.replace('/', r'\/')
                address = '/' + address + '/'
                tag = tagline.format(tagname(s), filename, address)
                tags.add(tag)

    with open('tags', 'w') as tagfile:
        tagfile.writelines(sorted(tags))

if __name__ == "__main__":
    args = get_arguments()
    args.func()
