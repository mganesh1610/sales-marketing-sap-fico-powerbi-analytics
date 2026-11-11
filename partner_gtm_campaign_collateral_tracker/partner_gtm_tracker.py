#!/usr/bin/env python3
"""
Partner GTM Campaign Tracking, Competitive Market-Response & Asset Documentation Governance Module.

Executes against 109,211 SHA-256-verified public campaign records:
1. Kevin Hillstrom Multi-Channel Campaign Attribution Dataset (64,000 rows)
2. UCI Direct Commercial Campaign Execution Dataset (45,211 rows)
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import sqlite3
import urllib.request
import zipfile
from pathlib import Path
from typing import Dict, List

MODULE_DIR = Path(__file__).resolve().parent
CACHE_DIR = MODULE_DIR / ".data_cache"
SQL_PATH = MODULE_DIR / "sql" / "partner_campaign_funnel_ctes.sql"
OUTPUT_DIR = MODULE_DIR / "outputs"

HILLSTROM_URL = (
    "http://www.minethatdata.com/"
    "Kevin_Hillstrom_MineThatData_E-MailAnalytics_DataMiningChallenge_2008.03.20.csv"
)
HILLSTROM_SHA256 = "0e5893329d8b93cefecc571777672028290ab69865718020c78c7284f291aece"

UCI_BANK_ZIP_URL = "https://archive.ics.uci.edu/static/public/222/bank+marketing.zip"
UCI_BANK_ZIP_SHA256 = "e0bf5f5de5b846e2f18e9d90606637267d46dfa260e0f17bb12e605db5efbeb4"


def fetch_verified(url: str, sha256_hex: str, filename: str) -> bytes:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    target = CACHE_DIR / filename
    if target.exists():
        data = target.read_bytes()
        if hashlib.sha256(data).hexdigest() == sha256_hex:
            return data
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Partner-GTM-Tracker)"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
    actual = hashlib.sha256(data).hexdigest()
    if actual != sha256_hex:
        raise ValueError(f"Checksum mismatch on {filename}: {actual} != {sha256_hex}")
    target.write_bytes(data)
    return data


def extract_uci_bank_full(zip_bytes: bytes) -> List[Dict[str, str]]:
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as outer:
        inner_bytes = outer.read("bank.zip")
    with zipfile.ZipFile(io.BytesIO(inner_bytes)) as inner:
        csv_text = inner.read("bank-full.csv").decode("utf-8")
    return list(csv.DictReader(io.StringIO(csv_text), delimiter=";"))


def run_partner_gtm_tracker() -> Dict[str, object]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    hill_bytes = fetch_verified(HILLSTROM_URL, HILLSTROM_SHA256, "hillstrom_64k.csv")
    uci_zip_bytes = fetch_verified(UCI_BANK_ZIP_URL, UCI_BANK_ZIP_SHA256, "bank_marketing.zip")

    hill_rows = list(csv.DictReader(io.StringIO(hill_bytes.decode("utf-8"))))
    uci_rows = extract_uci_bank_full(uci_zip_bytes)

    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE raw_hillstrom_campaigns (
            recency INTEGER,
            history_segment TEXT,
            history REAL,
            mens INTEGER,
            womens INTEGER,
            zip_code TEXT,
            newbie INTEGER,
            channel TEXT,
            segment TEXT,
            visit INTEGER,
            conversion INTEGER,
            spend REAL
        );
        """
    )
    cur.executemany(
        "INSERT INTO raw_hillstrom_campaigns VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        [
            (
                int(r["recency"]),
                r["history_segment"],
                float(r["history"]),
                int(r["mens"]),
                int(r["womens"]),
                r["zip_code"],
                int(r["newbie"]),
                r["channel"],
                r["segment"],
                int(r["visit"]),
                int(r["conversion"]),
                float(r["spend"]),
            )
            for r in hill_rows
        ],
    )
    conn.commit()

    mart_rows = cur.execute(SQL_PATH.read_text(encoding="utf-8")).fetchall()
    mart_cols = [d[0] for d in cur.description]

    mart_csv = OUTPUT_DIR / "partner_channel_kpi_mart.csv"
    with mart_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(mart_cols)
        writer.writerows(mart_rows)

    low_freq = [r for r in uci_rows if int(r["campaign"]) <= 3]
    high_freq = [r for r in uci_rows if int(r["campaign"]) > 4]
    low_cvr = sum(1 for r in low_freq if r["y"] == "yes") / len(low_freq)
    high_cvr = sum(1 for r in high_freq if r["y"] == "yes") / len(high_freq)
    fatigue_decay_pct = ((low_cvr - high_cvr) / low_cvr) * 100.0

    warm_partner = [r for r in uci_rows if r["poutcome"] == "success"]
    cold_outreach = [r for r in uci_rows if r["poutcome"] != "success"]
    warm_cvr = sum(1 for r in warm_partner if r["y"] == "yes") / len(warm_partner)
    cold_cvr = sum(1 for r in cold_outreach if r["y"] == "yes") / len(cold_outreach)
    warm_cosell_lift_x = warm_cvr / cold_cvr

    gates = {
        "gate_01_hillstrom_row_parity": len(hill_rows) == 64000,
        "gate_02_uci_campaign_row_parity": len(uci_rows) == 45211,
        "gate_03_sql_funnel_revenue_conservation": abs(
            sum(row[8] for row in mart_rows) - sum(float(r["spend"]) for r in hill_rows)
        ) < 0.05,
        "gate_04_sql_funnel_account_conservation": sum(row[3] for row in mart_rows) == 64000,
        "gate_05_non_negative_funnel_rates": all(row[6] >= 0.0 and row[7] >= 0.0 for row in mart_rows),
        "gate_06_fatigue_decay_verified": fatigue_decay_pct > 40.0,
        "gate_07_warm_partner_lift_verified": warm_cosell_lift_x > 5.0,
        "gate_08_multichannel_cohort_coverage": len(mart_rows) == 18,
        "gate_09_asset_taxonomy_completeness": all(bool(r["contact"]) and bool(r["month"]) for r in uci_rows),
        "gate_10_zero_null_conversion_labels": all(r["y"] in ("yes", "no") for r in uci_rows),
    }
    passed_gates = sum(1 for v in gates.values() if v)

    summary = {
        "combined_campaign_records": len(hill_rows) + len(uci_rows),
        "hillstrom_multichannel_rows": len(hill_rows),
        "uci_commercial_campaign_rows": len(uci_rows),
        "partner_kpi_mart_cohorts": len(mart_rows),
        "low_frequency_cvr_pct": round(low_cvr * 100.0, 2),
        "high_frequency_fatigue_cvr_pct": round(high_cvr * 100.0, 2),
        "frequency_fatigue_cvr_decay_pct": round(fatigue_decay_pct, 2),
        "warm_partner_reactivation_cvr_pct": round(warm_cvr * 100.0, 2),
        "cold_outreach_cvr_pct": round(cold_cvr * 100.0, 2),
        "warm_partner_cosell_lift_x": round(warm_cosell_lift_x, 2),
        "governance_gates_passed": f"{passed_gates}/{len(gates)}",
        "all_gates_green": passed_gates == len(gates),
    }

    (OUTPUT_DIR / "partner_gtm_campaign_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    conn.close()
    return summary


if __name__ == "__main__":
    print(json.dumps(run_partner_gtm_tracker(), indent=2))
