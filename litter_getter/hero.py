# -*- coding: utf-8 -*-
import json
import logging

import requests

from . import utils


"""
HERO API (example function call):
GET http://hero.epa.gov/ws/index.cfm/api/1.0/search/heroid/1203

All query fields are passed as name/value pairs in the URL. For example:

JSON
https://hero.epa.gov/hero/ws/index.cfm/api/1.0/search/criteria/mercury.json
https://hero.epa.gov/hero/ws/index.cfm/api/1.0/search/singleyear/1990/any/inhalation

XML
https://hero.epa.gov/hero/ws/index.cfm/api/1.0/search/criteria/mercury.xml
https://hero.epa.gov/hero/ws/index.cfm/api/1.0/search/singleyear/1990/any/inhalation%20reference.xml
https://hero.epa.gov/hero/ws/index.cfm/api/1.0/search/singleyear/1990/any/inhalation%20reference/recordsperpage/5.xml

RIS
https://hero.epa.gov/hero/ws/index.cfm/api/1.0/search/criteria/mercury.ris

Getting multiple HERO ids (records per page required)
https://hero.epa.gov/hero/ws/index.cfm/api/1.0/search/criteria/1200,1201,1203,1204/recordsperpage/500.xml

"""


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
                        self.content.append(self._parse_article(ref))
                else:
                    self.failures.extend([str(pk) for pk in pks.split(",")])
                    logging.info("HERO request failure: {url}".format(url=url))
            except requests.exceptions.Timeout:
                self.failures.extend([str(pk) for pk in pks.split(",")])
                logging.info("HERO request timeout: {url}".format(url=url))
        self._get_missing_ids()
        return dict(success=self.content, failure=self.failures,)

    def _get_missing_ids(self):
        found_ids = set([str(v["HEROID"]) for v in self.content])
        needed_ids = set(self.ids)
        missing = list(needed_ids - found_ids)
        if len(missing) > 0:
            self.failures.extend(missing)

    def _force_float_or_none(self, val):
        try:
            return float(val)
        except Exception:
            return None

    def _parse_pseudo_json(self, d, field):
        # built-in json parser doesn't identify nulls in HERO returns
        v = d.get(field, None)
        if v == "null":
            return None
        else:
            return v

    def _parse_article(self, article):
        d = dict(
            json=json.dumps(article),
            HEROID=str(self._parse_pseudo_json(article, "REFERENCE_ID")),
            PMID=str(self._parse_pseudo_json(article, "PMID")),
            title=self._parse_pseudo_json(article, "TITLE"),
            abstract=self._parse_pseudo_json(article, "ABSTRACT"),
            source=self._parse_pseudo_json(article, "SOURCE"),
            year=self._force_float_or_none(self._parse_pseudo_json(article, "YEAR")),
        )
        logging.debug("Parsing results for HEROID: {heroid}".format(heroid=d["HEROID"]))
        d.update(self._authors_info(article.get("AUTHORS", None)))
        return d

    @classmethod
    def _try_single_find(cls, xml, search):
        try:
            return xml.find(search).text
        except Exception:
            return ""

    def _authors_info(self, names_string):
        names = []
        if names_string:
            names = names_string.split("; ")
            names = [name.replace(", ", " ") for name in names]
        return dict(authors_list=names, authors_short=utils.get_author_short_text(names))
