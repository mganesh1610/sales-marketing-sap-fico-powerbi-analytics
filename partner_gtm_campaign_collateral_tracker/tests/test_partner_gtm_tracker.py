#!/usr/bin/env python3
"""Unit and SQL conservation tests for Partner GTM Campaign & Collateral Tracker."""
import unittest

from partner_gtm_campaign_collateral_tracker.partner_gtm_tracker import (
    OUTPUT_DIR,
    run_partner_gtm_tracker,
)


class TestPartnerGTMTracker(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.summary = run_partner_gtm_tracker()

    def test_combined_campaign_scale(self) -> None:
        self.assertEqual(self.summary["combined_campaign_records"], 109211)
        self.assertEqual(self.summary["partner_kpi_mart_cohorts"], 18)

    def test_governance_and_conservation_gates(self) -> None:
        self.assertEqual(self.summary["governance_gates_passed"], "10/10")
        self.assertTrue(self.summary["all_gates_green"])

    def test_partner_insights_and_exports(self) -> None:
        self.assertGreater(self.summary["frequency_fatigue_cvr_decay_pct"], 45.0)
        self.assertGreater(self.summary["warm_partner_cosell_lift_x"], 5.5)
        self.assertTrue((OUTPUT_DIR / "partner_gtm_campaign_summary.json").is_file())
        self.assertTrue((OUTPUT_DIR / "partner_channel_kpi_mart.csv").is_file())


if __name__ == "__main__":
    unittest.main()
