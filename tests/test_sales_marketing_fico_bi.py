#!/usr/bin/env python3
import json
import unittest
from pathlib import Path
from src.sap_fico_pbp_prp_pipeline import run_pipeline, OUTPUTS_DIR


class TestSalesMarketingFicoBI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = run_pipeline()

    def test_01_total_record_scale(self):
        self.assertEqual(self.summary["total_records_processed"], 109211)
        self.assertEqual(self.summary["hillstrom_marketing_records"], 64000)
        self.assertEqual(self.summary["uci_sales_campaign_records"], 45211)

    def test_02_sap_pbp_and_prp_plan_coverage(self):
        self.assertEqual(self.summary["sap_pbp_promotional_plans"], 12)
        self.assertEqual(self.summary["sap_prp_rebate_agreements"], 4)

    def test_03_zero_gl_subledger_variance(self):
        self.assertEqual(self.summary["gl_to_subledger_variance_usd"], 0.0)

    def test_04_gross_to_net_conservation_equation(self):
        gross = round(self.summary["gross_sales_revenue_usd"], 2)
        parts = round(
            self.summary["actual_pbp_promo_spend_usd"]
            + self.summary["prp_partner_rebate_accrual_usd"]
            + self.summary["net_settled_revenue_usd"],
            2,
        )
        self.assertAlmostEqual(gross, parts, places=2)

    def test_05_pbp_variance_reduction_and_roas(self):
        self.assertAlmostEqual(self.summary["pbp_promo_spend_variance_reduction_pct"], 34.8, places=1)
        self.assertGreater(self.summary["blended_gross_roas"], 3.0)

    def test_06_workspace_audit_checks_100_percent(self):
        self.assertEqual(self.summary["workspace_and_audit_checks_passed"], "12/12 (100.0%)")

    def test_07_output_artifacts_exist(self):
        self.assertTrue((OUTPUTS_DIR / "sap_pbp_prp_channel_reconciliation.csv").exists())
        self.assertTrue((OUTPUTS_DIR / "powerbi_workspace_health_audit.csv").exists())
        self.assertTrue((OUTPUTS_DIR / "sales_marketing_fico_summary.json").exists())


if __name__ == "__main__":
    unittest.main()
