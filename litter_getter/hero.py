# -*- coding: utf-8 -*-
import json
import logging
from typing import Any, Dict, Optional

import requests

from . import utils


def _parse_pseudo_json(d: Dict, field: str) -> Any:
    # built-in json parser doesn't identify nulls in HERO returns
    v = d.get(field, None)
    if v == "null":
        return None
    else:
        return v


def _force_float_or_none(val) -> Optional[float]:
    try:
        return float(val)
    except Exception:
        return None


def parse_article(content: Dict) -> Dict:
    authors = utils.normalize_authors(content.get("AUTHORS", "").split("; "))
    authors_short = utils.get_author_short_text(authors)
    return dict(
        json=content,
        HEROID=str(_parse_pseudo_json(content, "REFERENCE_ID")),
        PMID=str(_parse_pseudo_json(content, "PMID")),
        title=_parse_pseudo_json(content, "TITLE"),
        abstract=_parse_pseudo_json(content, "ABSTRACT"),
        source=_parse_pseudo_json(content, "SOURCE"),
        year=_force_float_or_none(_parse_pseudo_json(content, "YEAR")),
        authors=authors,
        authors_short=authors_short,
    )


class HEROFetch:
    """
    Handler to search and retrieve literature from US EPA's HERO database.

    Given a list of HERO IDs, fetch the content for each one and return a
    list of dictionaries of citation information. Note that this citation
    includes the PubMed ID, if available in HERO.
    """

    base_url = r"https://hero.epa.gov/hero/ws/index.cfm/api/1.0/search/criteria/{pks}/recordsperpage/{rpp}.json"
    default_settings = {"recordsperpage": 100}

    def __init__(self, id_list, **kwargs):
        if id_list is None:
            raise Exception("List of IDs are required for a PubMed search")
        self.ids = id_list
        self.ids_count = len(id_list)
        self.content = []
        self.failures = []
        self.settings = HEROFetch.default_settings.copy()
        for k, v in kwargs.items():
            self.settings[k] = v

    def get_content(self):
        rng = list(range(0, self.ids_count, self.settings["recordsperpage"]))
        for recstart in rng:
            pks = ",".join(
                [str(pk) for pk in self.ids[recstart : recstart + self.settings["recordsperpage"]]]
            )
            url = HEROFetch.base_url.format(pks=pks, rpp=self.settings["recordsperpage"])
            try:
                r = requests.get(url, timeout=30.0)
                if r.status_code == 200:
                    data = json.loads(r.text)
                    for ref in data["results"]:
                        self.content.append(parse_article(ref))
                else:
                    self.failures.extend([str(pk) for pk in pks.split(",")])
                    logging.info("HERO request failure: {url}".format(url=url))
            except requests.exceptions.Timeout:
                self.failures.extend([str(pk) for pk in pks.split(",")])
                logging.info("HERO request timeout: {url}".format(url=url))
        self._get_missing_ids()
        return dict(success=self.content, failure=self.failures)

    def _get_missing_ids(self):
        found_ids = set([str(v["HEROID"]) for v in self.content])
        needed_ids = set(self.ids)
        missing = list(needed_ids - found_ids)
        if len(missing) > 0:
            self.failures.extend(missing)

    @classmethod
    def _try_single_find(cls, xml, search):
        try:
            return xml.find(search).text
        except Exception:
            return ""
