import re

class Parser:
    r"""This is what a ``§Phrase definition  `` looks like.

    A phrase is started after the regular expression defined by 
    ``Parser.start`` matches::

        >>> p = Parser()
        >>> p.start == r'§(?!\s)'
        True

    and ends before the "phrase ending" regular expression, defined by::

        >>> p.end == r'(?!\s)§'
        True

    The ``text`` class attribute defines what a phrase can actually contain.
    It is pretty general::

        >>> p.text == r'.+?'
        True

    i.e. the shortest possible match of one or more characters.

    .. Examples::

        >>> for match in p.parse((
        ...        "This is a §phrase example§, and §this is another one§. "
        ...        "This here §contains an escaped \§§"
        ...        "and this § doesn't even start a match.")):
        ...    print(p.text_from_match(match))
        ...
        phrase example
        this is another one
        contains an escaped \§

    As you can see, if you want to use a phrase ending character within the
    phrase, you escape it with a backslash.
    """

    start = r'§(?!\s)'
    end   = r'(?!\s)§'
    text  = r'.+?'

    spaces = re.compile(r'\s+')

    def __init__(self, start=None, end=None, text=None):
        start = start or self.start
        end   = end   or self.end
        text  = text  or self.text
        klass = self.__class__.__name__

        regex = r'(?<!\\)(?:{start})(?P<{klass}>{text})(?<!\\)(?:{end})'.format(**locals())
        self.regex = re.compile(regex, flags=re.M|re.S)

    def normalize_name(self, string):
        string = string.strip()
        string = self.spaces.sub(' ', string)
        return string

    def parse_file(self, thefile):
        """Parse definitions in a file.

        :thefile: either a string or an open file-like object
                  (the latter providing at least a ``read()`` method
                  and a ``name`` attribute which contains the path
                  to the file)
        :returns: an iterable of objects (determined by ``postprocess_match()``).
        """
        if isinstance(thefile, str):
            path = thefile
            with open(thefile) as f:
                txt = f.read()
        else:
            path = thefile.name
            txt = thefile.read()

        return self.parse(txt, path)

    def parse(self, string, path=None):
        for match in self.regex.finditer(string) or []:
            yield self.postprocess_match(match, path)

    def postprocess_match(self, match, path):
        """Turn ``match`` into something useful.

        Default is to just return the match.

        >>> p = Parser()
        >>> result = list(p.parse('''This is a §test§.'''))[0]
        >>> type(result)
        <class '_sre.SRE_Match'>
        """
        # TODO: Fix this path-as-parameter-kludge.
        return match

    def text_from_match(self, match):
        return match.group(self.__class__.__name__)


class MultiParser(Parser):
    def __init__(self, *parsers):
        self.parsers = parsers
        regex = '|'.join(('(?:'+p.regex.pattern+')' for p in parsers))
        self.regex = re.compile(regex)

    def postprocess_match(self, match, path):
        groupdict = match.groupdict()
        for p in self.parsers:
            klass = p.__class__.__name__
            if groupdict[klass]:
                return p.postprocess_match(match, path)
