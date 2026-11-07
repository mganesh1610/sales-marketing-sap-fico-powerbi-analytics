-- ============================================================================
-- Microsoft Access & SQL Relational Schema, Parameter Queries & CTEs
-- Covers: SAP FICO (PBP & PRP), Sales & Marketing Operations, Power BI Views
-- ============================================================================

-- 1. Microsoft Access Compatible Table Creation & Calculated Formula Query
SELECT
    f.pbp_plan_id AS [PBP Plan ID],
    f.prp_agreement_id AS [PRP Rebate ID],
    f.channel_group AS [Sales & Marketing Channel],
    f.segment_tier AS [Customer Segment Tier],
    COUNT(f.record_id) AS [Total Campaign Records],
    SUM(f.engaged) AS [Engaged Prospects],
    SUM(f.converted) AS [Converted Orders],
    ROUND(SUM(f.gross_sales_cents) / 100.0, 2) AS [Gross Sales USD],
    ROUND(SUM(f.promo_cost_cents) / 100.0, 2) AS [Actual PBP Promo Spend USD],
    IIF(SUM(f.converted) >= r.volume_threshold_orders,
        r.rebate_rate_bps + r.bonus_rebate_bps,
        r.rebate_rate_bps) AS [Effective PRP Rebate BPS]
FROM (tbl_sales_marketing_fact AS f
INNER JOIN tbl_sap_pbp_promotions AS p ON f.pbp_plan_id = p.pbp_plan_id)
INNER JOIN tbl_sap_prp_rebates AS r ON f.prp_agreement_id = r.prp_agreement_id
GROUP BY
    f.pbp_plan_id,
    f.prp_agreement_id,
    f.channel_group,
    f.segment_tier,
    r.volume_threshold_orders,
    r.rebate_rate_bps,
    r.bonus_rebate_bps;

-- 2. Analytical SQL Joins & CTEs for Power BI, Tableau & Looker Semantic Layer
WITH channel_performance_cte AS (
    SELECT
        f.channel_group,
        f.segment_tier,
        f.pbp_plan_id,
        p.planned_promo_budget_cents / 100.0 AS planned_budget_usd,
        COUNT(*) AS total_touchpoints,
        SUM(f.converted) AS total_orders,
        SUM(f.gross_sales_cents) / 100.0 AS gross_revenue_usd,
        SUM(f.promo_cost_cents) / 100.0 AS promo_spend_usd
    FROM tbl_sales_marketing_fact f
    INNER JOIN tbl_sap_pbp_promotions p
        ON f.pbp_plan_id = p.pbp_plan_id
    GROUP BY f.channel_group, f.segment_tier, f.pbp_plan_id, p.planned_promo_budget_cents
)
SELECT
    channel_group,
    segment_tier,
    pbp_plan_id,
    total_touchpoints,
    total_orders,
    gross_revenue_usd,
    promo_spend_usd,
    ROUND(gross_revenue_usd / NULLIF(promo_spend_usd, 0), 2) AS channel_roas,
    ROUND(promo_spend_usd / NULLIF(total_orders, 0), 2) AS effective_cpa_usd
FROM channel_performance_cte
ORDER BY gross_revenue_usd DESC;
