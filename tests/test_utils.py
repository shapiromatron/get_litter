#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest import TestCase

from litter_getter.utils import get_author_short_text, normalize_author


class TestNormalizeAuthors:
    def test_expected(self):
        # test no initials
        assert normalize_author("Smith") == "Smith"
        assert normalize_author("Smith") == "Smith"
        assert normalize_author("Smith, Kevin") == "Smith Kevin"
        assert normalize_author("Smith, Kevin James") == "Smith Kevin James"
        assert normalize_author("Smith, Kevin J.") == "Smith Kevin J"

        # test no periods
        assert normalize_author("Smith K") == "Smith K"
        assert normalize_author("Smith, K") == "Smith K"
        assert normalize_author("Smith KJ") == "Smith KJ"
        assert normalize_author("Smith, KJ") == "Smith KJ"
        assert normalize_author("Smith K J") == "Smith KJ"
        assert normalize_author("Smith, K J") == "Smith KJ"

        # test w/ periods
        assert normalize_author("Smith K.") == "Smith K"
        assert normalize_author("Smith, K.") == "Smith K"
        assert normalize_author("Smith K.J.") == "Smith KJ"
        assert normalize_author("Smith, K.J.") == "Smith KJ"
        assert normalize_author("Smith K. J.") == "Smith KJ"
        assert normalize_author("Smith, K. J.") == "Smith KJ"

        # hyphenated
        assert normalize_author("Smith-Hyphenated, Kevin") == "Smith-Hyphenated Kevin"

        # unicode
        assert normalize_author("Langkjær, Svend") == "Langkjær Svend"
        assert normalize_author("Åmith K.") == "Åmith K"
        assert normalize_author("Åmith Å. Å.") == "Åmith ÅÅ"
        assert normalize_author("Åmith K.") == "Åmith K"

        # not an author-like name
        assert (
            normalize_author("The National Academies of Sciences, Engineering, and Medicine")
            == "The National Academies of Sciences, Engineering, and Medicine"
        )

    def test_edges(self):
        assert normalize_author("") == ""
        assert normalize_author("SKJ") == "SKJ"


class TestAuthor(TestCase):
    def test_parsing(self):
        # 0 test
        self.assertEqual("", get_author_short_text([]))

        # 1 test
        self.assertEqual("Smith J", get_author_short_text(["Smith J"]))

        # 2 test
        self.assertEqual("Smith J and Smith J", get_author_short_text(["Smith J"] * 2))

        # 3 test
        self.assertEqual("Smith J, Smith J, and Smith J", get_author_short_text(["Smith J"] * 3))

        # 4 test
        self.assertEqual("Smith J et al.", get_author_short_text(["Smith J"] * 4))
