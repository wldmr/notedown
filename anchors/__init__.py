from itertools import chain

from . import sexp
from util.parsing import Parser

class AnchorParser(Parser):
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

    def postprocess_match(self, match, path):
        name = self.normalize_name(self.text_from_match(match))
        aliases = {self.normalize_name(a) for a in sexp.make_groups(name)}

        anchor = Anchor(name = name,
                        path = path,
                        definition = match.group(0),
                        aliases = aliases)

        return anchor

class SynonymParser(Parser):
    start = r'\(\|'
    end   = r'\|\)'
    text  = r'.+?'

    def postprocess_match(self, match, path):
        name = self.normalize_name(self.text_from_match(match))
        aliases = {self.normalize_name(a) for a in sexp.make_groups(name)}

        anchor = Synonym(aliases=aliases, definition = match.group(0))

        return anchor

class Synonym:
    def __init__(self, definition, aliases=None):
        self.definition = definition
        self.aliases = aliases or set()

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

