import re

parens = re.compile(r'(\(|\))')

s = "((Many) beautiful) Colo(u)r(s)"

def break_list(string):
    lst = re.split(parens, string)
    result = []
    stack = [result]
    for item in lst:
        if item == '(':
            new = []
            stack[-1].append(new)
            stack.append(new)
        elif item == ')':
            stack.pop()
        else:
            stack[-1].append(item)
    assert stack[-1] is result
    return result

