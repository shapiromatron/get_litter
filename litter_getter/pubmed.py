# -*- coding: utf-8 -*-
import logging
import re
import xml.etree.ElementTree as ET
from itertools import chain

import requests

from . import utils


class PubMedSettings:
    """Module-level settings to check that PubMed requests registered."""

    PLACEHOLDER = "PLACEHOLDER"

    def __init__(self):
        self.api_key = self.PLACEHOLDER

    def connect(self, api_key: str):
        self.api_key = api_key


# global singleton
settings = PubMedSettings()


def connect(api_key: str):
    settings.connect(api_key)


class PubMedUtility:
    """Register tools with this utility class to import PubMed settings."""

    def _register_instance(self):
        if settings.api_key != PubMedSettings.PLACEHOLDER:
            self.settings["api_key"] = settings.api_key


class PubMedSearch(PubMedUtility):
    """Search PubMed with search-term and return a complete list of PubMed IDs."""

    base_url = r"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    default_settings = dict(retmax=5000, db="pubmed",)

    def __init__(self, term, **kwargs):
        self.id_count = None
        self.settings = PubMedSearch.default_settings.copy()
        self._register_instance()
        self.settings["term"] = term
        for k, v in kwargs.items():
            self.settings[k] = v

    def _get_id_count(self):
        data = dict(db=self.settings["db"], term=self.settings["term"], rettype="count",)
        r = requests.post(PubMedSearch.base_url, data=data)
        if r.status_code == 200:
            txt = ET.fromstring(r.text)
            self.id_count = int(txt.find("Count").text)
            logging.info("{c} references found.".format(c=self.id_count))
        else:
            raise Exception("Search query failed; please reformat query or try again later")

    def _parse_ids(self, txt):
        def parse_id(xml):
            return str(xml.text)

        id_list = ET.fromstring(txt).find("IdList")
        ids = id_list.findall("Id")
        return list(map(parse_id, ids))

    def _fetch_ids(self):
        ids = []
        data = self.settings.copy()
        if self.id_count is None:
            self._get_id_count()
        rng = list(range(0, self.id_count, self.settings["retmax"]))
        self.request_count = len(rng)
        for retstart in rng:
            data["retstart"] = retstart
            r = requests.post(PubMedSearch.base_url, data=data)
            if r.status_code == 200:
                ids.extend(self._parse_ids(r.text))
            else:
                raise Exception("Search query failed; please reformat query or try again later")
        self.ids = ids

    def get_ids_count(self):
        self._get_id_count()

    def get_ids(self):
        self._fetch_ids()
        return self.ids

    def get_changes_from_previous_search(self, old_ids_list):
        """Return a dictionary with additions and removals of PMIDs."""
        return {
            "added": set(self.ids) - set(old_ids_list),
            "removed": set(old_ids_list) - set(self.ids),
        }


class PubMedFetch(PubMedUtility):
    """Given a list of PubMed IDs, return list of dict of PubMed citation."""

    base_url = r"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    default_settings = dict(retmax=1000, db="pubmed", retmode="xml",)

    ARTICLE = 0
    BOOK = 1

    DOI_ARTICLE_SEARCH_STRING = 'MedlineCitation/Article/ELocationID[@EIdType="doi"]'
    ABSTRACT_ARTICLE_SEARCH_STRING = "MedlineCitation/Article/Abstract/AbstractText"

    DOI_BOOK_SEARCH_STRING = 'BookDocument/ArticleIdList/ArticleId[@IdType="doi"]'
    ABSTRACT_BOOK_SEARCH_STRING = "BookDocument/Abstract/AbstractText"

    def __init__(self, id_list, **kwargs):
        if id_list is None:
            raise Exception("List of IDs are required for a PubMed search")
        self.ids = id_list
        self.content = []
        self.settings = PubMedFetch.default_settings.copy()
        self._register_instance()
        for k, v in kwargs.items():
            self.settings[k] = v

    def get_content(self):
        data = self.settings.copy()
        rng = list(range(0, len(self.ids), self.settings["retmax"]))
        self.request_count = len(rng)
        for retstart in rng:
            data["id"] = self.ids[retstart : retstart + self.settings["retmax"]]
            r = requests.post(PubMedFetch.base_url, data=data)
            if r.status_code == 200:
                articles = ET.fromstring(r.text.encode("utf-8")).findall("PubmedArticle")
                for article in articles:
                    self.content.append(self._parse_article(article))
                books = ET.fromstring(r.text.encode("utf-8")).findall("PubmedBookArticle")
                for book in books:
                    self.content.append(self._parse_book(book))
            else:
                logging.error("Pubmed failure: {}, content: {}".format(r.status_code, r.text))
                logging.error("Pubmed failure data submission: {}".format(data))
                raise Exception("Fetch query failed; please reformat query or try again later")
        return self.content

    def _parse_article(self, article):
        pmid = str(PubMedFetch._try_single_find(article, "MedlineCitation/PMID"))
        logging.debug("Parsing results for PMID: {pmid}".format(pmid=pmid))
        d = {
            "xml": ET.tostring(article, encoding="unicode"),
            "PMID": pmid,
            "title": PubMedFetch._try_single_find(article, "MedlineCitation/Article/ArticleTitle"),
            "abstract": self._get_abstract(article, self.ABSTRACT_ARTICLE_SEARCH_STRING),
            "citation": self._journal_info(article),
            "year": self._get_year(article, dtype=self.ARTICLE),
            "doi": self._get_doi(article, self.DOI_ARTICLE_SEARCH_STRING),
        }
        d.update(self._authors_info(article, self.ARTICLE))
        return d

    def _parse_book(self, book):
        pmid = str(PubMedFetch._try_single_find(book, "BookDocument/PMID"))
        logging.debug("Parsing results for PMID: {pmid}".format(pmid=pmid))
        book_title = PubMedFetch._try_single_find(book, "BookDocument/Book/BookTitle")
        article_title = self._try_single_find(book, "BookDocument/ArticleTitle")
        abstract = self._get_abstract(book, self.ABSTRACT_BOOK_SEARCH_STRING)
        year = self._get_year(book, dtype=self.BOOK)
        doi = self._get_doi(book, self.DOI_BOOK_SEARCH_STRING)

        d = {
            "xml": ET.tostring(book, encoding="unicode"),
            "PMID": pmid,
            "abstract": abstract,
            "year": year,
            "doi": doi,
        }
        d.update(self._authors_info(book, self.BOOK))

        if article_title:
            d["title"] = article_title
            d["citation"] = self._get_book_citation(book, title=book_title)
        else:
            d["title"] = book_title
            d["citation"] = self._get_book_citation(book)

        return d

    def _get_abstract(self, article, search_string):
        txt = ""

        abstracts = article.findall(search_string)

        # standard abstract
        if len(abstracts) == 1:
            txt = "".join([txt for txt in abstracts[0].itertext()])

        # structured abstract
        if len(abstracts) > 1:
            txts = []
            for abstract in abstracts:
                tmp = "".join([txt for txt in abstract.itertext()])
                lbl = abstract.attrib.get("Label")
                if lbl:
                    tmp = '<span class="abstract_label">{v}: </span>'.format(v=lbl) + tmp
                txts.append(tmp)
            txt = "<br>".join(txts)
        return txt

    @classmethod
    def _try_single_find(cls, xml, search):
        try:
            match = xml.find(search)
            return "".join([txt for txt in match.itertext()])
        except Exception:
            return ""

    def _authors_info(self, et, dtype):
        names = []

        if dtype == self.ARTICLE:
            auths = et.findall("MedlineCitation/Article/AuthorList/Author")
        elif dtype == self.BOOK:
            auths = chain(
                et.findall('BookDocument/Book/AuthorList[@Type="authors"]/Author'),
                et.findall('BookDocument/AuthorList[@Type="authors"]/Author'),
            )

        for auth in auths:
            try:
                names.append(
                    "{0} {1}".format(auth.find("LastName").text, auth.find("Initials").text)
                )
            except Exception:
                pass

            try:
                names.append(auth.find("CollectiveName").text)
            except Exception:
                pass

        return {"authors_list": names, "authors_short": utils.get_author_short_text(names)}

    def _journal_info(self, article):
        return "{journal} {year}; {volume} ({issue}):{pages}".format(
            journal=PubMedFetch._try_single_find(
                article, "MedlineCitation/Article/Journal/ISOAbbreviation"
            ),
            year=PubMedFetch._try_single_find(
                article, "MedlineCitation/Article/Journal/JournalIssue/PubDate/Year"
            ),
            volume=PubMedFetch._try_single_find(
                article, "MedlineCitation/Article/Journal/JournalIssue/Volume"
            ),
            issue=PubMedFetch._try_single_find(
                article, "MedlineCitation/Article/Journal/JournalIssue/Issue"
            ),
            pages=PubMedFetch._try_single_find(
                article, "MedlineCitation/Article/Pagination/MedlinePgn"
            ),
        )

    def _get_book_citation(self, et, title=None):
        if title:
            title += " "
        else:
            title = ""

        return "{title}({year}). {location}: {publisher}.".format(
            title=title,
            year=PubMedFetch._try_single_find(et, "BookDocument/Book/PubDate/Year"),
            location=PubMedFetch._try_single_find(
                et, "BookDocument/Book/Publisher/PublisherLocation"
            ),
            publisher=PubMedFetch._try_single_find(et, "BookDocument/Book/Publisher/PublisherName"),
        )

    def _get_year(self, et, dtype):
        if dtype == self.ARTICLE:
            year = et.find("MedlineCitation/Article/Journal/JournalIssue/PubDate/Year")
            if year is not None:
                return int(year.text)

            medline_date = et.find(
                "MedlineCitation/Article/Journal/JournalIssue/PubDate/MedlineDate"
            )  # noqa
            if medline_date is not None:
                year = re.search(r"(\d+){4}", medline_date.text)
                if year is not None:
                    return int(year.group(0))
        elif dtype == self.BOOK:
            year = et.find("BookDocument/Book/PubDate/Year")
            if year is not None:
                return int(year.text)

    def _get_doi(self, et, search_string):
        doi = et.find(search_string)
        if doi is not None:
            return doi.text
