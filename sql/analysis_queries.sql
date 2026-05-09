-- CRM Sales Pipeline & Lead Follow-Up Automation System
-- SQL queries used to analyze cleaned CRM lead data.

-- KPI summary
SELECT
  COUNT(*) AS total_leads,
  ROUND(SUM(CASE WHEN stage NOT IN ('Won','Lost') THEN CAST(deal_value AS REAL) ELSE 0 END), 2) AS active_pipeline,
  ROUND(SUM(CASE WHEN stage NOT IN ('Won','Lost') THEN CAST(expected_value AS REAL) ELSE 0 END), 2) AS expected_pipeline,
  ROUND(SUM(CASE WHEN stage = 'Won' THEN CAST(deal_value AS REAL) ELSE 0 END), 2) AS won_revenue,
  SUM(CASE WHEN followup_status = 'Overdue' THEN 1 ELSE 0 END) AS overdue_followups,
  SUM(CASE WHEN priority = 'High' AND stage NOT IN ('Won','Lost') THEN 1 ELSE 0 END) AS high_priority_active_leads
FROM crm_leads;

-- Follow-up queue
SELECT lead_id, company_name, contact_name, sales_rep, stage, lead_source,
       deal_value, expected_value, lead_score, priority, followup_status,
       next_followup_date, recommended_action
FROM crm_leads
WHERE stage NOT IN ('Won','Lost')
  AND followup_status IN ('Overdue', 'Due Today', 'Due This Week', 'Missing Follow-Up')
ORDER BY
  CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END,
  CASE followup_status WHEN 'Overdue' THEN 1 WHEN 'Due Today' THEN 2 WHEN 'Missing Follow-Up' THEN 3 ELSE 4 END,
  CAST(expected_value AS REAL) DESC;

-- Sales rep performance
SELECT sales_rep,
       COUNT(*) AS total_leads,
       ROUND(SUM(CASE WHEN stage NOT IN ('Won','Lost') THEN CAST(deal_value AS REAL) ELSE 0 END), 2) AS active_pipeline,
       ROUND(SUM(CASE WHEN stage NOT IN ('Won','Lost') THEN CAST(expected_value AS REAL) ELSE 0 END), 2) AS expected_pipeline,
       ROUND(SUM(CASE WHEN stage = 'Won' THEN CAST(deal_value AS REAL) ELSE 0 END), 2) AS won_revenue,
       SUM(CASE WHEN followup_status = 'Overdue' THEN 1 ELSE 0 END) AS overdue_followups,
       SUM(CASE WHEN priority = 'High' AND stage NOT IN ('Won','Lost') THEN 1 ELSE 0 END) AS high_priority_leads,
       ROUND(AVG(CAST(lead_score AS REAL)), 1) AS avg_lead_score
FROM crm_leads
GROUP BY sales_rep
ORDER BY expected_pipeline DESC;

-- Lead source performance
SELECT lead_source,
       COUNT(*) AS total_leads,
       SUM(CASE WHEN stage IN ('Qualified','Demo Scheduled','Proposal','Negotiation','Won') THEN 1 ELSE 0 END) AS qualified_or_better,
       ROUND(100.0 * SUM(CASE WHEN stage = 'Won' THEN 1 ELSE 0 END) / COUNT(*), 1) AS win_rate_pct,
       ROUND(AVG(CAST(deal_value AS REAL)), 2) AS avg_deal_value,
       ROUND(SUM(CASE WHEN stage NOT IN ('Won','Lost') THEN CAST(expected_value AS REAL) ELSE 0 END), 2) AS expected_pipeline,
       SUM(CASE WHEN followup_status = 'Overdue' THEN 1 ELSE 0 END) AS overdue_followups
FROM crm_leads
GROUP BY lead_source
ORDER BY expected_pipeline DESC;
