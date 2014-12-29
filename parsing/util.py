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

        >>> for text in p.parse((
        ...        "This is a §phrase example§, and §this is another one§. "
        ...        "This here §contains an escaped \§§"
        ...        "and this § doesn't even start a match.")):
        ...    print(text)
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
        """Initialize the Parser.

        Can be customized on a per-instance basis to parse different 
        constructs. Has an empty path attribute on creation.

            >>> p = Parser(start="X", end="Y", text="[a-z]+")
            >>> print(p.path)
            None

            >>> list(p.parse('''A XmatchY; not a XMatchY'''))
            ['match']
        """
        start = start or self.start
        end   = end   or self.end
        text  = text  or self.text
        klass = self.__class__.__name__

        regex = r'(?<!\\)(?:{start})(?P<{klass}>{text})(?<!\\)(?:{end})'.format(**locals())
        self.regex = re.compile(regex, flags=re.M|re.S)

        self.path = None

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

        During parsing, sets ``self.path`` to ``thefile`` if it is a string,
        or to ``thefile.name`` if it is a file-like object.

        Fails if the object doesn't have a ``name`` attribute.

            >>> from io import StringIO
            >>> fakefile = StringIO("§One§, §Two§")
            >>> p = Parser()
            >>> try:
            ...     list(p.parse_file(fakefile))
            ... except AttributeError as e:
            ...     print(e)
            '_io.StringIO' object has no attribute 'name'

        (let's fix that)

            >>> fakefile.name = "Somefile"
            >>> results = p.parse_file(fakefile)

        If you start parsing now, ``p.path`` will not be none;
        this can be used to determine if you are parsing a file or not.

            >>> p.path is None  # None before parsing.
            True
            >>> for result in results:
            ...     print("{result} in {p.path}".format(**locals()))
            One in Somefile
            Two in Somefile
            >>> p.path is None  # None after parsing again.
            True

        If given a string, open the file given by the string,
        and then parse that::

            >>> from tempfile import mkstemp
            >>>
            >>> handle, path = mkstemp(text=True)
            >>> with open(path, 'w') as f:
            ...     bytecount = f.write("This is a §test§")
            >>> list(p.parse_file(path))
            ['test']

        Clean up after ourselves::

            >>> import os
            >>> os.path.exists(path), os.remove(path), os.path.exists(path)
            (True, None, False)
        """
        if isinstance(thefile, str):
            path = thefile
            with open(thefile) as f:
                txt = f.read()
        else:
            path = thefile.name
            txt = thefile.read()

        self.path = path
        for result in self.parse(txt):
            yield result
        self.path = None

    def parse(self, string):
        for match in self.regex.finditer(string) or []:
            yield self.postprocess_match(match)

    def postprocess_match(self, match):
        """Turn ``match`` into something useful.

        Default is to just return ``self.text_from_match(match)``.

        >>> p = Parser()
        >>> list(p.parse('''This is a §test§.'''))
        ['test']

        An overriding function can check whether ``self.path`` is not ``None``
        and can then make use of that.
        """
        return self.text_from_match(match)

    def text_from_match(self, match):
        return match.group(self.__class__.__name__)


class MultiParser(Parser):
    def __init__(self, *parsers):
        self.parsers = parsers
        regex = '|'.join(('(?:'+p.regex.pattern+')' for p in parsers))
        self.regex = re.compile(regex)

    def postprocess_match(self, match):
        groupdict = match.groupdict()
        for p in self.parsers:
            klass = p.__class__.__name__
            if groupdict[klass]:
                return p.postprocess_match(match)
