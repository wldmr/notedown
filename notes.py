#!/bin/env python3

import sys
from glob import iglob
from argparse import ArgumentParser

from anchors import Anchor, AnchorParser, AnchorTagRenderer

def debug(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def get_arguments():
    parser = ArgumentParser(description="Handle notes, my way.")
    subparsers = parser.add_subparsers(title="Commands")

    mktags = subparsers.add_parser("tags", help="create tags file")
    mktags.set_defaults(func=cmd_mktags)

    parser.set_defaults(func=cmd_mktags)
    return parser.parse_args()

def cmd_mktags():
    parser = AnchorParser()

    anchors = set()
    for filename in iglob('*.txt'):
        new_anchors = parser.parse_file(filename)
        anchors.update(new_anchors)

    renderer = AnchorTagRenderer()
    lines = renderer.render_anchors(anchors)
    with open('tags', 'w') as tf:
        tf.writelines(lines)

if __name__ == "__main__":
    args = get_arguments()
    args.func()
