from util.parsing import Parser

class ReferenceParser(Parser):
    """This is what a ´Reference definition´ looks like.

    Can be escaped by either prepending the first slashes with
    a backslash (`\`).
    """

    start = r'->|→'
    end   = r'\.|\,|  |(?={})'.format(start)
    text  = r'.+?'

    def postprocess_match(self, match, path):
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
