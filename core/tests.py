"""SDI hisoblash yadrosi testlari (TZ 12-bo'lim, 9-mezon)."""

from django.test import SimpleTestCase

from core.enums import DEFAULT_WEIGHTS, compute_sdi, level_for, normalize_weights


class WeightsTests(SimpleTestCase):
    def test_default_weights_sum_to_one(self):
        self.assertAlmostEqual(sum(DEFAULT_WEIGHTS.values()), 1.0, places=6)

    def test_normalize_scales_arbitrary_weights(self):
        weights = normalize_weights({"MOT": 2, "COG": 2, "ACT": 2, "REF": 2, "CRE": 2})
        self.assertAlmostEqual(sum(weights.values()), 1.0, places=6)
        self.assertAlmostEqual(weights["MOT"], 0.2, places=6)

    def test_normalize_falls_back_when_all_zero(self):
        self.assertEqual(
            normalize_weights({"MOT": 0, "COG": 0, "ACT": 0, "REF": 0, "CRE": 0}),
            DEFAULT_WEIGHTS,
        )

    def test_negative_weight_is_clamped(self):
        weights = normalize_weights({"MOT": -5, "COG": 1, "ACT": 1, "REF": 1, "CRE": 1})
        self.assertEqual(weights["MOT"], 0.0)


class SdiTests(SimpleTestCase):
    def test_all_hundred_gives_hundred(self):
        scores = {key: 100 for key in DEFAULT_WEIGHTS}
        self.assertEqual(compute_sdi(scores), 100.0)

    def test_all_zero_gives_zero(self):
        scores = {key: 0 for key in DEFAULT_WEIGHTS}
        self.assertEqual(compute_sdi(scores), 0.0)

    def test_weighted_formula_matches_manual_calculation(self):
        scores = {"MOT": 60, "COG": 80, "ACT": 40, "REF": 50, "CRE": 70}
        expected = 60 * 0.15 + 80 * 0.25 + 40 * 0.25 + 50 * 0.20 + 70 * 0.15
        self.assertAlmostEqual(compute_sdi(scores), round(expected, 2), places=2)

    def test_missing_component_counts_as_zero(self):
        self.assertAlmostEqual(compute_sdi({"COG": 100}), 25.0, places=2)

    def test_custom_weights_are_respected(self):
        scores = {"MOT": 100, "COG": 0, "ACT": 0, "REF": 0, "CRE": 0}
        weights = {"MOT": 1, "COG": 0, "ACT": 0, "REF": 0, "CRE": 0}
        self.assertEqual(compute_sdi(scores, weights), 100.0)


class LevelScaleTests(SimpleTestCase):
    def test_boundaries(self):
        self.assertEqual(level_for(0)[0], "INITIAL")
        self.assertEqual(level_for(39.9)[0], "INITIAL")
        self.assertEqual(level_for(40)[0], "LOW_MEDIUM")
        self.assertEqual(level_for(59.9)[0], "LOW_MEDIUM")
        self.assertEqual(level_for(60)[0], "MEDIUM")
        self.assertEqual(level_for(74.9)[0], "MEDIUM")
        self.assertEqual(level_for(75)[0], "HIGH")
        self.assertEqual(level_for(89.9)[0], "HIGH")
        self.assertEqual(level_for(90)[0], "CREATIVE")
        self.assertEqual(level_for(100)[0], "CREATIVE")

    def test_out_of_range_values_are_clamped(self):
        self.assertEqual(level_for(-10)[0], "INITIAL")
        self.assertEqual(level_for(150)[0], "CREATIVE")

    def test_none_is_treated_as_zero(self):
        self.assertEqual(level_for(None)[0], "INITIAL")
