# -*- coding: utf-8 -*-
from typing import List
import re


# First-group is rest of reference; second-group are initials
# with optional second initial (middle-name) with optional periods
RE_AUTHOR = re.compile(r"([\-\,\w]+)\s([\s?\w{1,1}\.?]+)$", flags=re.UNICODE)
RE_TWO_INITIALS = re.compile(r"^([\w])[\,\.]{0,2}\s([\w])[\,\.]{0,2}$", flags=re.UNICODE)


def normalize_author(author: str) -> str:
    # for cases which may appear to be to be an individual's name
    num_words = len(author.split())
    if num_words > 1 and num_words < 4:
        matches = RE_AUTHOR.match(author)
        if matches:
            matches2 = RE_TWO_INITIALS.match(matches.group(2))
            if matches2:
                initials = matches.group(2).replace(",", "").replace(".", "").replace(" ", "")
            else:
                initials = matches.group(2).replace(",", "").replace(".", "")

            surname = matches.group(1).replace(",", "")
            author = "{0} {1}".format(surname, initials)
    return author


def normalize_authors(authors: List[str]) -> List[str]:
    return [normalize_author(author) for author in authors]


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
