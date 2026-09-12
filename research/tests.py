"""Tadqiqot moduli: eksport anonimligi, ustunlar va statistika testlari."""

import csv
import io

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.enums import Cut, Role, StudyArm
from diagnostics.models import Measurement

from .services import (
    EXPORT_COLUMNS,
    comparison_table,
    describe,
    independent_t,
    measurement_rows,
    stats_table,
    to_csv,
    to_xlsx,
)

User = get_user_model()


class ExportDataTests(TestCase):
    def setUp(self):

        for index in range(4):
            arm = StudyArm.EXPERIMENTAL if index % 2 == 0 else StudyArm.CONTROL
            user = User.objects.create_user(f"resp{index}@test.uz", "parol12345")
            user.first_name, user.last_name = "Ism", "Familiya"
            user.save()
            user.profile.study_arm = arm
            user.profile.save()

            gain = 20 if arm == StudyArm.EXPERIMENTAL else 5
            Measurement.objects.create(user=user, cut=Cut.INITIAL,
                                       mot=50, cog=50, act=50, ref=50, cre=50)
            Measurement.objects.create(user=user, cut=Cut.FINAL,
                                       mot=50 + gain, cog=50 + gain, act=50 + gain,
                                       ref=50 + gain, cre=50 + gain)

    def test_rows_have_exact_columns(self):
        """FR-59 — ustunlar tarkibi TZ'ga aynan mos."""
        rows = measurement_rows()
        self.assertTrue(rows)
        self.assertEqual(list(rows[0].keys()), EXPORT_COLUMNS)

    def test_export_contains_no_personal_data(self):
        """FR-60 / NFR-17 — ism, familiya, email eksportda bo'lmasligi shart."""
        payload = to_csv(measurement_rows()).decode("utf-8-sig")
        self.assertNotIn("Ism", payload)
        self.assertNotIn("Familiya", payload)
        self.assertNotIn("@test.uz", payload)

    def test_respondent_id_is_stable_across_cuts(self):
        rows = measurement_rows()
        by_id = {}
        for row in rows:
            by_id.setdefault(row["respondent_id"], set()).add(row["cut"])
        # Har bir respondent ikkala kesimda ham bir xil kod bilan chiqadi.
        self.assertTrue(all(len(cuts) == 2 for cuts in by_id.values()))

    def test_csv_is_parseable(self):
        payload = to_csv(measurement_rows()).decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(payload), delimiter=";")
        parsed = list(reader)
        self.assertEqual(len(parsed), 8)
        self.assertEqual(reader.fieldnames, EXPORT_COLUMNS)

    def test_xlsx_is_generated(self):
        payload = to_xlsx(measurement_rows())
        if payload is None:
            self.skipTest("openpyxl o'rnatilmagan")
        self.assertTrue(payload.startswith(b"PK"))  # xlsx — zip arxiv

    def test_cut_filter(self):
        rows = measurement_rows(cuts=[Cut.FINAL])
        self.assertTrue(all(row["cut"] == Cut.FINAL for row in rows))

    def test_arm_filter(self):
        rows = measurement_rows(arms=[StudyArm.EXPERIMENTAL])
        self.assertTrue(all(row["group"] == StudyArm.EXPERIMENTAL for row in rows))


class StatisticsTests(TestCase):
    def test_describe_basic(self):
        stats = describe([10, 20, 30, 40])
        self.assertEqual(stats["n"], 4)
        self.assertEqual(stats["mean"], 25.0)
        self.assertEqual(stats["min"], 10.0)
        self.assertEqual(stats["max"], 40.0)
        self.assertAlmostEqual(stats["sd"], 12.91, places=1)  # tanlanma SD

    def test_describe_empty(self):
        self.assertEqual(describe([])["n"], 0)

    def test_describe_single_value_has_zero_sd(self):
        self.assertEqual(describe([42])["sd"], 0.0)

    def test_independent_t_returns_none_for_small_samples(self):
        self.assertIsNone(independent_t([1], [2]))

    def test_independent_t_computes(self):
        result = independent_t([70, 72, 74, 76], [50, 52, 54, 56])
        self.assertIsNotNone(result)
        self.assertGreater(result["t"], 0)


class ExperimentComparisonTests(ExportDataTests):
    def test_experimental_growth_exceeds_control(self):
        comparison = comparison_table()
        sdi_row = next(row for row in comparison if row["component"] == "SDI")
        self.assertGreater(sdi_row["E"]["delta"], sdi_row["C"]["delta"])
        self.assertGreater(sdi_row["delta_diff"], 0)

    def test_stats_table_covers_both_arms(self):
        table = stats_table()
        arms = {row["arm"] for row in table}
        self.assertIn(StudyArm.EXPERIMENTAL, arms)
        self.assertIn(StudyArm.CONTROL, arms)


class ResearchAccessTests(TestCase):
    """NFR-12 — tadqiqot paneli faqat admin uchun."""

    def setUp(self):
        self.student = User.objects.create_user("oqituvchi-r@test.uz", "parol12345")
        self.student.profile.onboarding_done = True
        self.student.profile.save()

        self.researcher = User.objects.create_user("admin-r@test.uz", "parol12345")
        self.researcher.profile.role = Role.ADMIN
        self.researcher.profile.onboarding_done = True
        self.researcher.profile.save()

    def test_student_cannot_open_research_dashboard(self):
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(reverse("research:dashboard")).status_code, 403)

    def test_student_cannot_export(self):
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(reverse("research:export")).status_code, 403)

    def test_researcher_can_open_dashboard(self):
        self.client.force_login(self.researcher)
        self.assertEqual(self.client.get(reverse("research:dashboard")).status_code, 200)

    def test_researcher_can_download_csv(self):
        self.client.force_login(self.researcher)
        response = self.client.post(reverse("research:export"), {"fmt": "CSV"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/csv", response["Content-Type"])
        self.assertIn("attachment", response["Content-Disposition"])
