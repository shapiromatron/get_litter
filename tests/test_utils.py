#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest import TestCase

from litter_getter.utils import get_author_short_text


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
