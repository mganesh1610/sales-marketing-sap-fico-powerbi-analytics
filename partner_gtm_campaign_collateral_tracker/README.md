# Partner GTM Campaign Tracking, Competitive Response & Asset Governance (`partner_gtm_campaign_collateral_tracker`)

An in-place `P1` product marketing & partner GTM analytics module auditing **109,211 SHA-256-verified public campaign & customer insight records** (`64,000` Kevin Hillstrom multi-channel customer records + `45,211` UCI direct commercial campaign execution records).

## Verified Capabilities & Outputs

- **Multi-Channel Partner Campaign Tracking (`sql/partner_campaign_funnel_ctes.sql`):** Aggregates `64,000` customer journeys into **`18` cross-vendor bundle vs. single-solution channel cohorts** (`Web`, `Phone`, `Multichannel`) with exact `$0.00` revenue conservation.
- **Customer-Insight Cadence & Warm Co-Sell Reactivation (`partner_gtm_tracker.py`):** Quantifies **`50.25%` conversion decay** from high-frequency campaign fatigue (`12.88%` vs. `6.41%` CVR) and **`6.56x` conversion lift** on warm partner-engaged customer segments (`64.73%` vs. `9.86%` CVR).
- **Automated Asset & Taxonomy Hygiene Gates:** Passes **`10/10` (`100.0%`)** campaign taxonomy completeness, SQL account/revenue conservation, and BI reporting parity gates (`outputs/partner_gtm_campaign_summary.json`, `outputs/partner_channel_kpi_mart.csv`).
- **Automated Test Suite (`tests/test_partner_gtm_tracker.py`):** `3/3` unit tests passing.

## Quickstart

```bash
PYTHONPATH=. python3 -m unittest discover -s partner_gtm_campaign_collateral_tracker/tests -p "test_*.py" -v
```
