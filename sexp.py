import sys
import re

parens = re.compile(r'(\(|\))')

def parse_hierarchy(string):
    """Turn a parenthesized string into a tree.

    >>> parse_hierarchy("This is a ((very) good) Example")
    ['This is a ', [['very'], ' good'], ' Example']

    :string: string with parens

    :returns: list of lists and strings
    """
    result = []
    stack = [result]
    for item in re.split(parens, string):
        if item == '(':
            new = []
            stack[-1].append(new)
            stack.append(new)
        elif item == ')':
            stack.pop()
        elif item:
            stack[-1].append(item)
    assert stack[-1] is result
    return result

def flatten_hierarchy(tree):
    """Return a set of strings from a tree.

    >>> tree = parse_hierarchy("This is a ((very) good) Example")
    >>> sorted(flatten_hierarchy(tree))
    ['This is a  Example', 'This is a  good Example', 'This is a very good Example']

    Note that whitespace is not handled intelligently (i.e. whitespace will
    neither be collapsed nor trimmed).

    :tree: a list of lists and strings as returned by ``parse_hierarchy()``

    :returns: A set of strings
    """
    acc = set([""])

    for item in tree:
        if isinstance(item, str):  # It's a leaf.
            # Append the new string to each existing one in the accumulator.
            acc = {start + item for start in acc}
        else:  # It's a tree, which means its contents are optional.
            # So the accumulator will contain both the original strings
            # and the appended versions.
            acc |= { start + end
                     for start in acc
                     for end in flatten_hierarchy(item) }

    return acc

def make_groups(string):
    tree = parse_hierarchy(string)
    return flatten_hierarchy(tree)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
