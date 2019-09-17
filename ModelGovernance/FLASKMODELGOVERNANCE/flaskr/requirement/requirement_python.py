import re


def create_requirements(requirements, req_fd):
    # reading supported requirements
    with open('flaskr/requirement/possible_requirements_python.txt', 'r') as fd:
        reg = fd.read()[:-1]

    # creating regular expression
    reg = re.compile(reg)

    result = []

    # casting
    for line in requirements.stream.read().decode('utf-8').splitlines():
        if reg.match(line) != None:
            result.append(line)
    # sorting
    result.sort()

    n = len(result)

    # writing result
    for line in result:
        req_fd.write(line + "\n")

    return n
