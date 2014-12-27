import re

class Parser:
    def __init__(self, start, end, text):
        regex = ''.join((
            r'(?<!\\)' + start,
            '(' + text + ')',
            r'(?<!\\)' + end))
        print(regex)
        self.regex = re.compile(regex, flags=re.M|re.S)

    def parse(self, txt):
        """Find occurrences of a pattern in ``txt``
        and emit an iterable of matches.

        A match.group(1) contains the text of the match,
        while match.group(0) contains the whole match
        (i.e. without any delimiters).
        """
        return self.regex.finditer(txt) or []

