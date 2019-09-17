import re


def parse(text, dots=False):
    """Parse the query

    Parameters
    ----------
    text : string
        query
    dots : bool
        if query contains dots

    Returns
    -------
    dict
        dictionary with parsed query
    """

    if text is None:
        return {'less': None, 'equal': None, 'greater': None}

    # creating regexp
    if dots:
        # case when query contatins dots
        less = re.compile('(?<=<)[0123456789.]*?(?=;)')
        greater = re.compile('(?<=>)[0123456789.]*?(?=;)')
        equal = re.compile('(?<==)[0123456789.]*?(?=;)')
    else:
        # case without dots
        less = re.compile('(?<=<)[0123456789]*?(?=;)')
        greater = re.compile('(?<=>)[0123456789]*?(?=;)')
        equal = re.compile('(?<==)[0123456789]*?(?=;)')

    # searching
    less = less.search(text)
    if less is not None:
        less = less.group(0)
    equal = equal.search(text)
    if equal is not None:
        equal = equal.group(0)
    greater = greater.search(text)
    if greater is not None:
        greater = greater.group(0)

    # constructing result
    result = {'less': less, 'equal': equal, 'greater': greater}

    return result


def check_values(name, x, as_text=False):
    """Check if values in the query are correct and form them into parts of the general query

    Parameters
    ----------
    name : string
        name of the variable
    x : dict
        parsed query, result from parse function
    as_text : bool
        if values are text or numerical

    Returns
    -------
    string/bool
        Formed part of the general query or False if values are wrong of True if there is no restrictions
    """

    # no restrictions
    if x['less'] is None and x['equal'] is None and x['greater'] is None:
        return True

    if x['equal'] is not None:
        if x['greater'] is not None or x['less'] is not None:
            # wrong query
            return False
        if as_text:
            return name + ' = ' + '\'' + x['equal'] + '\''
        else:
            return name + ' = ' + x['equal']

    if x['greater'] is not None and x['less'] is not None:
        if int(x['greater']) >= int(x['less']):
            # wrong query
            return False
        if as_text:
            return name + ' > ' + '\'' + x['greater'] + '\'' + ' and ' + name + ' < ' + '\'' + x['less'] + '\''
        else:
            return name + ' > ' + x['greater'] + ' and ' + name + ' < ' + x['less']

    if x['greater'] is not None:
        if as_text:
            return name + ' > ' + '\'' + x['greater'] + '\''
        else:
            return name + ' > ' + x['greater']

    if x['less'] is not None:
        if as_text:
            return name + ' < ' + '\'' + x['less'] + '\''
        else:
            return name + ' < ' + x['less']


def add_to_query(query, x, first):
    """Add partially formed query to the general query

    Parameters
    ----------
    query : string
        general query
    x : string
        partially formed query
    first : bool
        flag if this the first restriction in the general query

    Returns
    -------
    query : string
        general query with added partial query
    first : bool
        flag if the first restriction appeared
    """

    if x != True:
        if first:
            query += x
            first = False
        else:
            query += ' and ' + x
            first = False

    return query, first
