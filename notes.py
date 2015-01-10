#!/bin/env python3

import sys
from glob import iglob
from argparse import ArgumentParser

from parsing.anchors import Anchor, AnchorParser, Synonym, SynonymParser, AnchorTagRenderer
from parsing.util import MultiParser
from parsing.references import Reference, ReferenceParser

def get_arguments():
    parser = ArgumentParser(description="Handle notes, my way.")
    subparsers = parser.add_subparsers(title="Commands")

    mktags = subparsers.add_parser("tags", help="create tags file")
    mktags.set_defaults(func=cmd_mktags)

    mklinks = subparsers.add_parser("links", help="print links")
    mklinks.set_defaults(func=cmd_mklinks)

    #parser.set_defaults(func=cmd_mktags)
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

def cmd_mklinks():
    class NS: pass
    parser = MultiParser(AnchorParser(), SynonymParser(), ReferenceParser())

    print("digraph g {")
    print("node [shape=none]; overlap=false;")
    current_anchor = NS()
    current_anchor.name = "---"
    current_anchor.aliases = set()
    for filename in iglob('*.txt'):
        for item in parser.parse_file(filename):
            if isinstance(item, Anchor):
                current_anchor = item
                print('"{}"'.format(item.name))
            elif isinstance(item, Synonym):
                current_anchor.aliases.update(item.aliases)
                debug(item.aliases)
            elif isinstance(item, Reference):
                print('"{}" -> "{}";'.format(current_anchor.name, item.target))
            else:
                raise Exception(str(item))
    print("}")


if __name__ == "__main__":
    args = get_arguments()
    args.func()
