from parsing.util import Parser

class ReferenceParser(Parser):
    """This is what a ``^Reference definition^``looks like.

    >>> p = ReferenceParser()
    >>> for ref in p.parse("This is a ^reference to something^."):
    ...     print(ref.target)
    ...
    reference to something
    """

    start = r'\^(?!\s)'
    end = r'(?!\s)\^'

    def postprocess_match(self, match):
        target = self.normalize_name(self.text_from_match(match))

        ref = Reference(target = target,
                        definition = match.group(0))

        return ref


class Reference:
    def __init__(self, target, definition):
        """Initiate a reference

        :target: normalized string that names an anchor
        :definition: the string that defined the reference
        """
        self.target = target
        self.definition = definition
