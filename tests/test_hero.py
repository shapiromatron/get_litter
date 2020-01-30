#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase

from litter_getter.hero import HEROFetch


class HEROFetchTests(TestCase):
    def test_success_query(self):
        # ensure that we get the correct query returned
        ids = ("1201",)
        hero_getter = HEROFetch(id_list=ids)
        hero_getter.get_content()
        self.assertListEqual(hero_getter.failures, [])
        self.assertEqual(len(hero_getter.content), 1)

        val = hero_getter.content[0]

        # test individual components
        self.assertEqual(val["HEROID"], "1201")
        self.assertEqual(val["PMID"], "9922222")
        self.assertListEqual(
            val["authors_list"],
            ["Farman CA", "Watkins K", "Van Hoozen B", "Last JA", "Witschi H", "Pinkerton KE"],
        )
        self.assertEqual(val["authors_short"], "Farman CA et al.")
        self.assertEqual(
            val["title"],
            "Centriacinar remodeling and sustained procollagen gene expression after exposure to ozone and nitrogen dioxide",
        )  # noqa
        self.assertEqual(val["year"], 1999)
        self.assertEqual(
            val["abstract"],
            "Sprague-Dawley rats were exposed to 0.8 ppm ozone (O3), to 14.4 ppm nitrogen dioxide (NO2), or to both gases simultaneously for 6 h per day for up to 90 d. The extent of histopathologic changes within the central acinus of the lungs was compared after 7 or 78 to 90 d of exposure using morphometric analysis by placement of concentric arcs radiating outward from a single reference point at the level of the bronchiole- alveolar duct junction. Lesions in the lungs of rats exposed to the mixture of gases extended approximately twice as far into the acinus as in those exposed to each individual gas. The extent of tissue involvement was the same at 78 to 90 d as noted at 7 d in all exposure groups. At the end of exposure, in situ hybridization for procollagen types I and III demonstrated high levels of messenger RNA within central acini in the lungs of animals exposed to the combination of O3 and NO2. In contrast, animals exposed to each individual gas had a similar pattern of message expression compared with that seen in control animals, although centriacinar histologic changes were still significantly different from control animals. We conclude that the progressive pulmonary fibrosis that occurs in rats exposed to the combination of O3 and NO2 is due to sustained, elevated expression of the genes for procollagen types I and III. This effect at the gene level is correlated with the more severe histologic lesions seen in animals exposed to both O3 and NO2 compared with those exposed to each individual gas. In contrast, the sustained expression of the procollagen genes is not associated with a shift in the distribution of the lesions because the area of change in each group after 7 d of exposure was the same as after 78 to 90 d of exposure.",
        )  # noqa

    def test_bigger_query(self):
        # Ensure that we can get hundreds of results at once, and confirm that
        # we are properly getting processing content and failures
        ids = [str(d) for d in range(1200, 1405)]
        hero_getter = HEROFetch(id_list=ids)
        hero_getter.get_content()
        self.assertEqual(len(hero_getter.content), 200)
        self.assertEqual(len(hero_getter.failures), 5)
        self.assertListEqual(
            sorted(hero_getter.failures), sorted(["1227", "1349", "1224", "1228", "1361"])
        )
