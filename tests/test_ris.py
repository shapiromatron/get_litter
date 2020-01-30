#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os

from litter_getter.ris import RisImporter

from .utils import ExtendedTestCase


class RISParsingTests(ExtendedTestCase):
    def test_parsing(self):
        # make sure file exists
        fn = os.path.join(os.path.dirname(__file__), "data/sample_ris.txt")
        self.assertTrue(os.path.exists(fn))

        # assert successful import of all references
        importer = RisImporter(fn)
        refs = importer.references
        self.assertEqual(len(refs), 10)

        # test journal-style import
        test = """{
            "accession_number": "2003114678",
            "abstract": "When chlorine is introduced into public drinking water for disinfection, it can react with organic compounds in surface waters to form toxic by-products such as 3-chloro-4-(dichloromethyl)-5-hydroxy-2[5H]-furanone (MX). We investigated the effect of exposure to MX on cytochrome P450 2E1 (CYP2E1)-like activity and total glutathione (GSH) in the liver of the small fish model, medaka (Oryzias latipes). The multi-site carcinogen methylazoxymethanol acetate (MAMAc) was the positive control compound. Both medaka liver microsome preparations and S-9 fractions catalyzed the hydroxylation of p-nitrophenol (PNP), suggesting CYP2E1-like activity in the medaka. Male medaka exposed for 96 h to the CYP2E1 inducers ethanol and acetone under fasted conditions showed significant increases in PNP-hydroxylation activity. Furthermore, total reduced hepatic GSH was reduced in fish fasted for 96 h, indicating that normal feeding is a factor in maintaining xenobiotic defenses. Exposure to MX and MAMAc induced significant increases in hepatic CYP2E1-like activity, however MX exposure did not alter hepatic GSH levels. These data strengthen the role of the medaka as a suitable species for examining cytochrome P450 and GSH detoxification processes and the role these systems play in chemical carcinogenesis. \u00a9 2003 Elsevier Science Inc. All rights reserved.",
            "citation": "Comparative Biochemistry and Physiology - C Toxicology and Pharmacology 2003; 134 (3):353-364",
            "authors_short": "Geter DR et al.",
            "year": "2003",
            "id": 288,
            "doi": "10.1016/S1532-0456(03)00003-6",
            "title": "p-Nitrophenol and glutathione response in medaka (Oryzias latipes) exposed to MX, a drinking water carcinogen",
            "reference_type": "JOUR",
            "accession_db": "Embase",
            "PMID": "12643982"
        }"""
        ref = refs[0]
        ref.pop("json")
        self.assertJSONEqual(json.dumps(ref), test)

        # test chapter-style import
        test = """{
            "accession_number": null,
            "abstract": "",
            "citation": "Applications of Toxicogenomics in Safety Evaluation and Risk Assessment. 2011. Pages 41-64. 9780470449820 (ISBN)",
            "authors_short": "Boverhof DR et al.",
            "year": "2011",
            "id": 11,
            "doi": "10.1002/9781118001042.ch3",
            "title": "Practical Considerations for the Application of Toxicogenomics to Risk Assessment: Early Experience, Current Drivers, and a Path Forward",
            "reference_type": "CHAP",
            "accession_db": "Scopus",
            "PMID": null
        }"""
        ref = refs[5]
        ref.pop("json")
        self.assertJSONEqual(json.dumps(ref), test)

        # test conference-style import
        test = """{
            "accession_number": null,
            "citation": "2013 International Conference on Human Health and Medical Engineering, HHME 2013",
            "authors_short": "",
            "year": "2014",
            "id": 823,
            "doi": null,
            "title": "2013 International Conference on Human Health and Medical Engineering, HHME 2013",
            "reference_type": "CONF",
            "accession_db": "Scopus",
            "PMID": null
        }"""
        ref = refs[9]
        ref.pop("json")
        ref.pop("abstract")
        self.assertJSONEqual(json.dumps(ref), test)

        # test unicode-authors
        test = "Radomska-Leśniewska DM and Skopiński P"
        self.assertEqual(test, refs[8]["authors_short"])

    def test_parsing_unknown_tags(self):
        # make sure file exists
        fn = os.path.join(os.path.dirname(__file__), "data/sample_ris.txt")

        importer = RisImporter(fn)
        refs = importer.references

        # test import with unknown tags
        test = """{
            "JP": ["CRISPR"],
            "DC": ["Direct Current"]
        }"""
        ref = refs[4]
        ref_json = json.loads(ref.pop("json"))
        self.assertJSONEqual(json.dumps(ref_json["unknown_tag"]), test)
