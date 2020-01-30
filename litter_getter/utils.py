# -*- coding: utf-8 -*-


def get_author_short_text(authors):
    # Given a list of authors, return citation.
    nAuthors = len(authors)
    if nAuthors == 0:
        return ""
    elif nAuthors == 1:
        return str(authors[0])
    elif nAuthors == 2:
        return "{0} and {1}".format(*authors)
    elif nAuthors == 3:
        return "{0}, {1}, and {2}".format(*authors)
    else:  # >3 authors
        return "{0} et al.".format(authors[0])


def try_int(val):
    try:
        return int(val)
    except Exception:
        return val
