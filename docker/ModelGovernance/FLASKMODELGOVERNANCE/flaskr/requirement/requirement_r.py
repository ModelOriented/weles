import re


def create_requirements(requirements, req_fd):
    """
    Function used to standarize requirements
    requirements - file storage for requirements
    """

    with open("flaskr/requirement/possible_requirements_r.txt", 'r') as fd:
        req = fd.read()[:-1]

    reg = re.compile(req)

    result = []

    # casting
    for line in requirements.stream.read().decode('utf-8').splitlines():
        if reg.match(line) == None:
            result.append(line)
    # sorting
    result.sort()

    n = len(result)

    # writing result
    for line in result:
        req_fd.write(line + "\n")

    return n
