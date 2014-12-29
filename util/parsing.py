import re

class Parser:
    """Abstract Base Class."""
    start = None
    end   = None
    text  = None

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

        for match in self.regex.finditer(txt) or []:
            yield self.postprocess_match(match, path)

    def postprocess_match(self, match, path):
        # TODO: Fix this path-as-parameter-kludge.
        raise NotImplemented("Must override ``postprocess_match`` to convert matches to useful objects.")

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
