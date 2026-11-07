# Power BI Workspace Administration, DAX Troubleshooting & Access/SAP FICO Schema Guide

## 1. Power BI Workspace Administration & Troubleshooting Runbook
- **Workspace Governance:** Separates `Dev`, `UAT`, and `Prod` workspaces with role-based access control (`Admin`, `Member`, `Contributor`, `Viewer`) and scheduled gateway refreshes.
- **DAX & Relationship Debugging:**
  - Resolves silent relationship join failures caused by leading/trailing whitespace via Power Query `Text.Trim` / `Text.Clean` and Excel `_` visual boundary markers.
  - Uses `EXCEPT(VALUES(...), VALUES(...))` to detect orphan foreign keys prior to semantic model refresh.
  - Applies `UNION` + `TREATAS` unified calendar tables so a single date slicer filters promotional plans (`SAP PBP`), rebate accruals (`SAP PRP`), and campaign conversions simultaneously.

## 2. SAP FICO (`PBP` & `PRP`) Formulations
- **Effective Partner Rebate Basis Points (`PRP`):**
  $$\text{BPS}_{\text{eff}} = \text{BPS}_{\text{base}} + \mathbb{I}(\text{Orders} \ge \tau_{\text{vol}}) \cdot \text{BPS}_{\text{bonus}}$$
- **Gross-to-Net Ledger Conservation (`PBP` + `PRP`):**
  $$\text{Revenue}_{\text{Net}} = \text{Sales}_{\text{Gross}} - \text{Spend}_{\text{PBP}} - \text{Rebate}_{\text{PRP}}, \quad \Delta_{\text{GL, Subledger}} = \$0.00$$
