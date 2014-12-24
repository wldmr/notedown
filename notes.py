#!/bin/env python3

import sys
import re
from glob import iglob
from argparse import ArgumentParser

import sexp

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

    anchor_start = r'(?<!\\)\|'
    anchor_end   = r'(?<!\\)\|'
    anchor_text  = r'(.+?)'

    spaces = re.compile(r'\s+')

    def __init__(self, start=None, end=None, text=None):
        anchordef = ''.join((
            start or self.anchor_start,
            text  or self.anchor_text,
            end   or self.anchor_end))
        self.anchordef = re.compile(anchordef, flags=re.M|re.S)

    def normalize_name(self, string):
        string = string.strip()
        string = self.spaces.sub(' ', string)
        return string

    def parse(self, path, txt):
        """Extract ``Anchors``s from ``file_like``.

        :path: Anchors need to point to a file, so give the path here.
               nothing is actually done with this string, other than
               storing it in the path field of the anchor.
        :txt: string to parse

        :returns: generator of ``Anchor``'s
        """
        matches = self.anchordef.finditer(txt) or []
        for match in matches:

            name = self.normalize_name(match.group(1))
            aliases = {self.normalize_name(a) for a in sexp.make_groups(name)}

            anchor = Anchor(name = name,
                            path = path,
                            definition = match.group(0),
                            aliases = aliases)

            yield anchor

    def parse_file(self, thefile):
        """Convenience function for parsing files.

        :thefile: either a string or an open file-like object
                  (the latter providing at least a ``read()`` method
                  and a ``name`` attribute which contains the path
                  to the file.
        :returns: same as ``parse()``
        """
        if isinstance(file, str):
            return self.parse(path=thefile, txt=open(thefile).read())
        else:
            return self.parse(path=thefile.name, txt=thefile.read())

class Anchor:
    """Represents a location within a piece of text.

    Instance attributes:

    :name: Human readable name for this anchor.
    :path: Path to the file this anchor refers to.
    :definition: text that defined the anchor;
                 to be used as a search string.
    :aliases: A set of strings that are also names of this anchor;
              (besides the main ``name``)
    """

    def __init__(self, name, path, definition, aliases=None):
        """Create an anchor."""
        self.name = name
        self.path = path
        self.definition = definition

        self.aliases = aliases or set()


    def __repr__(self):
        return "{}(name='{}', path='{}')".format(
                self.__class__.__name__,
                self.name,
                self.path)

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
