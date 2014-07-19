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

def make_groups(string):
    from collections import defaultdict
    from itertools import product
    import pdb

    parts = re.split(parens, string)

    ### Break the sequence into groups
    groupnumber = 0
    groupstack = [groupnumber]
    groups = defaultdict(list)
    for n, part in enumerate(parts):
        if part == '(':
            groupnumber += 1
            groupstack.append(groupnumber)
        elif part == ')':
            groupstack.pop()
        else:
            current = groupstack[-1]
            groups[current].append(n)
    print(groups)
    ### Assemble all permutations of the groups
    out = []
    assert len(groups) == groupnumber+1
    combinations = product((True, False), repeat=groupnumber)
    for combination in combinations:
        # Gather all indices
        selected = set(groups[0])
        for n in range(groupnumber):
            if combination[n]:
                selected.update(groups[n+1])
        # Combine all selected parts
        val = "".join(parts[n]
            for n in range(len(parts))
            if n in selected)
        out.append(val)
    return out

g = make_groups(s)
