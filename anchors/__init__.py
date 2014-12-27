import re
from itertools import chain

from . import sexp
from util.parsing import Parser

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

    start = r'\|'
    end   = r'\|'
    text  = r'.+?'

    spaces = re.compile(r'\s+')

    def __init__(self, start=None, end=None, text=None):
        self.parser = Parser(start or self.start,
                             end   or self.end,
                             text  or self.text)

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
        for match in self.parser.parse(txt):

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

    def anchor_to_tags(self, anchor):
        """Return a single tagfile line (including newline at the end).

        ``anchor`` must have the following attributes:
        ``name``, ``path``, ``definition``.
        If not, throw hissy fit (in the Form of ``AttributeError``).
        """
        # Replace some characters that have special meaning to the ex search 
        # pattern, so we get a 'literal' string. TODO: Do this properly, for 
        # all special characters; this is bound to blow up with some weird 
        # anchor string or another.
        address = anchor.definition
        address = address.replace('\n', r'\n')
        address = address.replace('/', r'\/')
        address = '/' + address + '/'

        for name in {anchor.name} | anchor.aliases:
            yield self.tagline.format(
                    name    = name,
                    path    = anchor.path,
                    address = address)

    def render_anchors(self, anchors):
        """Take an iterable of ``Anchor``s and return a sorted list of tagfile lines."""
        tags = (list(self.anchor_to_tags(a)) for a in anchors)
        return sorted(chain.from_iterable(tags))

