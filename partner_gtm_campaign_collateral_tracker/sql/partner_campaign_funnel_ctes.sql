-- Partner GTM Multi-Channel Campaign Funnel & Competitive Response CTEs
WITH channel_campaign_rollup AS (
    SELECT
        channel,
        segment AS gtm_motion,
        CASE
            WHEN mens = 1 AND womens = 1 THEN 'Cross_Vendor_Bundle_Cohort'
            ELSE 'Single_Solution_Cohort'
        END AS customer_insight_cohort,
        COUNT(*) AS accounts_reached,
        SUM(visit) AS landing_page_visits,
        SUM(conversion) AS closed_conversions,
        ROUND(AVG(visit) * 100.0, 4) AS ctr_visit_pct,
        ROUND(AVG(conversion) * 100.0, 4) AS conversion_pct,
        ROUND(SUM(spend), 2) AS attributed_revenue
    FROM raw_hillstrom_campaigns
    GROUP BY channel, segment, customer_insight_cohort
)
SELECT
    channel,
    gtm_motion,
    customer_insight_cohort,
    accounts_reached,
    landing_page_visits,
    closed_conversions,
    ctr_visit_pct,
    conversion_pct,
    attributed_revenue
FROM channel_campaign_rollup
ORDER BY customer_insight_cohort, channel, gtm_motion;
