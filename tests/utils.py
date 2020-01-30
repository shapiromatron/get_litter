#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from unittest import TestCase

import six


class ExtendedTestCase(TestCase):
    """Extra assertions borrowed Django."""

    def assertJSONEqual(self, raw, expected_data, msg=None):
        """
        Asserts that the JSON fragments raw and expected_data are equal.
        Usual JSON non-significant whitespace rules apply as the heavyweight
        is delegated to the json library.
        """
        try:
            data = json.loads(raw)
        except ValueError:
            self.fail("First argument is not valid JSON: %r" % raw)
        if isinstance(expected_data, six.string_types):
            try:
                expected_data = json.loads(expected_data)
            except ValueError:
                self.fail("Second argument is not valid JSON: %r" % expected_data)
        self.assertEqual(data, expected_data, msg=msg)
