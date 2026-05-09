from __future__ import annotations

import csv
import random
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "crm_leads_raw.csv"
CLEAN_PATH = ROOT / "data" / "processed" / "clean_crm_leads.csv"
DB_PATH = ROOT / "data" / "processed" / "sales_pipeline.sqlite"
REPORT_DIR = ROOT / "reports"
SQL_PATH = ROOT / "sql" / "analysis_queries.sql"
REPORT_DATE = date(2026, 5, 9)


LEAD_SOURCES = ["Website", "Referral", "LinkedIn", "Webinar", "Cold Email", "Event", "Partner", "Paid Search"]
INDUSTRIES = ["Healthcare", "Professional Services", "Fitness", "Education", "Real Estate", "Retail", "Nonprofit", "SaaS"]
REGIONS = ["Atlanta", "Columbus", "Charlotte", "Nashville", "Remote", "Dallas", "Tampa", "Chicago"]
COMPANY_SIZES = ["1-10", "11-50", "51-200", "201-500", "500+"]
SALES_REPS = ["Avery Brooks", "Jordan Lee", "Morgan Smith", "Riley Carter", "Tobi Oniyide"]
STAGES = ["New", "Contacted", "Qualified", "Demo Scheduled", "Proposal", "Negotiation", "Won", "Lost", "Nurture"]
EMAIL_STATUSES = ["No Response", "Opened", "Replied", "Bounced", "Unsubscribed"]
LOST_REASONS = ["No Budget", "No Decision", "Bad Fit", "Chose Competitor", "Timing", ""]

STAGE_PROBABILITY = {
    "New": 0.08,
    "Contacted": 0.15,
    "Qualified": 0.32,
    "Demo Scheduled": 0.48,
    "Proposal": 0.64,
    "Negotiation": 0.78,
    "Won": 1.0,
    "Lost": 0.0,
    "Nurture": 0.18,
}

STAGE_RANK = {
    "New": 1,
    "Contacted": 2,
    "Nurture": 3,
    "Qualified": 4,
    "Demo Scheduled": 5,
    "Proposal": 6,
    "Negotiation": 7,
    "Lost": 8,
    "Won": 9,
}

TEXT_VARIANTS = {
    "Website": ["Website", "web site", "WEB", "Inbound Web"],
    "Referral": ["Referral", "referral", "Referred"],
    "LinkedIn": ["LinkedIn", "linkedin", "Linked In"],
    "Webinar": ["Webinar", "webinar", "Online Event"],
    "Cold Email": ["Cold Email", "cold email", "Outbound Email"],
    "Paid Search": ["Paid Search", "paid search", "Google Ads"],
    "Professional Services": ["Professional Services", "prof services", "Professional Svcs"],
    "SaaS": ["SaaS", "saas", "Software"],
    "New": ["New", "new", "Fresh Lead"],
    "Contacted": ["Contacted", "contacted", "Reached Out"],
    "Qualified": ["Qualified", "qualified", "Good Fit"],
    "Demo Scheduled": ["Demo Scheduled", "demo scheduled", "Demo Booked"],
    "Proposal": ["Proposal", "proposal", "Proposal Sent"],
    "Negotiation": ["Negotiation", "negotiation", "Decision Stage"],
    "Won": ["Won", "won", "Closed Won"],
    "Lost": ["Lost", "lost", "Closed Lost"],
    "Nurture": ["Nurture", "nurture", "Long Term"],
    "No Response": ["No Response", "no response", "No Reply"],
    "Opened": ["Opened", "opened", "Email Opened"],
    "Replied": ["Replied", "replied", "Response"],
    "Bounced": ["Bounced", "bounced", "Invalid Email"],
}


def ensure_dirs() -> None:
    for path in [RAW_PATH.parent, CLEAN_PATH.parent, DB_PATH.parent, REPORT_DIR, SQL_PATH.parent]:
        path.mkdir(parents=True, exist_ok=True)


def messy_text(value: str, chance: float = 0.16) -> str:
    if random.random() < 0.025:
        return ""
    if random.random() < chance and value in TEXT_VARIANTS:
        return random.choice(TEXT_VARIANTS[value])
    return value


def messy_date(value: date | None) -> str:
    if value is None:
        return ""
    if random.random() < 0.025:
        return ""
    return value.strftime(random.choice(["%Y-%m-%d", "%m/%d/%Y", "%b %d %Y"]))


def messy_money(value: float) -> str:
    if random.random() < 0.035:
        return ""
    if random.random() < 0.02:
        return f"-{value:.2f}"
    if random.random() < 0.12:
        return f"$ {value:,.2f}"
    return f"{value:.2f}"


def messy_int(value: int) -> str:
    if random.random() < 0.03:
        return ""
    if random.random() < 0.02:
        return str(value * -1)
    return str(value)


def messy_bool(value: bool) -> str:
    if value:
        return random.choice(["yes", "Y", "true", "1", "Booked"])
    return random.choice(["no", "N", "false", "0", ""])


def base_deal_value(company_size: str, industry: str) -> float:
    size_multiplier = {
        "1-10": 0.65,
        "11-50": 1.0,
        "51-200": 1.55,
        "201-500": 2.2,
        "500+": 3.1,
    }[company_size]
    industry_multiplier = {
        "Healthcare": 1.35,
        "Professional Services": 1.15,
        "Fitness": 0.75,
        "Education": 0.9,
        "Real Estate": 1.1,
        "Retail": 0.8,
        "Nonprofit": 0.62,
        "SaaS": 1.7,
    }[industry]
    return random.uniform(1400, 7200) * size_multiplier * industry_multiplier


def generate_raw_dataset(record_count: int = 760) -> list[dict[str, str]]:
    random.seed(41)
    rows: list[dict[str, str]] = []
    first_names = ["Maya", "Chris", "Andre", "Taylor", "Sam", "Jasmine", "Alex", "Nia", "Daniel", "Priya"]
    last_names = ["Walker", "Patel", "Johnson", "Garcia", "Brown", "Nguyen", "Miller", "Davis", "Wilson", "Thomas"]
    company_words = ["Northstar", "Summit", "Blue Ridge", "Metro", "BrightPath", "Crescent", "Anchor", "Evergreen"]
    company_types = ["Group", "Systems", "Partners", "Clinic", "Studio", "Services", "Labs", "Collective"]
    start_date = date(2026, 1, 2)

    for index in range(record_count):
        source = random.choices(LEAD_SOURCES, weights=[21, 17, 16, 13, 11, 8, 7, 7], k=1)[0]
        industry = random.choices(INDUSTRIES, weights=[14, 18, 9, 10, 14, 12, 7, 16], k=1)[0]
        region = random.choice(REGIONS)
        company_size = random.choices(COMPANY_SIZES, weights=[20, 32, 25, 14, 9], k=1)[0]
        stage = random.choices(STAGES, weights=[12, 17, 19, 12, 11, 7, 9, 7, 6], k=1)[0]
        rep = random.choice(SALES_REPS)
        created_date = start_date + timedelta(days=random.randint(0, 118))

        stage_rank = STAGE_RANK[stage]
        last_contact_date = None if stage == "New" and random.random() < 0.5 else created_date + timedelta(days=random.randint(0, 38))
        if last_contact_date and last_contact_date > REPORT_DATE:
            last_contact_date = REPORT_DATE - timedelta(days=random.randint(0, 4))

        next_followup_date = None
        if stage not in {"Won", "Lost"}:
            if random.random() < 0.14:
                next_followup_date = None
            else:
                anchor = last_contact_date or created_date
                next_followup_date = anchor + timedelta(days=random.randint(2, 21))
                if random.random() < 0.32:
                    next_followup_date = REPORT_DATE - timedelta(days=random.randint(1, 18))

        deal_value = base_deal_value(company_size, industry) * random.uniform(0.78, 1.35)
        probability = STAGE_PROBABILITY[stage] + random.uniform(-0.04, 0.04)
        probability = min(1.0, max(0.0, probability))
        meeting_count = max(0, stage_rank - 2 + random.randint(-1, 2))
        if stage in {"New", "Contacted"}:
            meeting_count = random.choice([0, 0, 1])
        demo_booked = stage_rank >= STAGE_RANK["Demo Scheduled"] and stage not in {"Lost"}
        proposal_sent = stage_rank >= STAGE_RANK["Proposal"] and stage not in {"Lost"}
        email_status = random.choices(EMAIL_STATUSES, weights=[38, 26, 24, 7, 5], k=1)[0]
        lost_reason = random.choice(LOST_REASONS[:-1]) if stage == "Lost" else ""
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        company = f"{random.choice(company_words)} {random.choice(company_types)}"

        rows.append(
            {
                "lead_id": f"CRM-{20000 + index}",
                "created_date": messy_date(created_date),
                "lead_source": messy_text(source),
                "industry": messy_text(industry, 0.1),
                "region": messy_text(region, 0.06),
                "company_size": company_size if random.random() > 0.03 else "",
                "company_name": company,
                "contact_name": name,
                "sales_rep": rep if random.random() > 0.03 else "",
                "stage": messy_text(stage),
                "deal_value": messy_money(deal_value),
                "probability": f"{probability:.2f}" if random.random() > 0.04 else "",
                "last_contact_date": messy_date(last_contact_date),
                "next_followup_date": messy_date(next_followup_date),
                "email_status": messy_text(email_status),
                "demo_booked": messy_bool(demo_booked),
                "proposal_sent": messy_bool(proposal_sent),
                "meeting_count": messy_int(meeting_count),
                "lost_reason": messy_text(lost_reason, 0.08),
            }
        )

    for row in random.sample(rows, 24):
        duplicate = row.copy()
        duplicate["stage"] = messy_text(random.choice(["Qualified", "Proposal", "Negotiation", "Won"]))
        duplicate["last_contact_date"] = messy_date(REPORT_DATE - timedelta(days=random.randint(0, 15)))
        duplicate["next_followup_date"] = messy_date(REPORT_DATE + timedelta(days=random.randint(1, 8)))
        rows.append(duplicate)

    random.shuffle(rows)
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def normalize_text(value: str, default: str = "Unknown") -> str:
    cleaned = " ".join((value or "").strip().replace("-", " ").split()).title()
    if not cleaned:
        return default
    aliases = {
        "Web Site": "Website",
        "Web": "Website",
        "Inbound Web": "Website",
        "Referred": "Referral",
        "Linkedin": "LinkedIn",
        "Linked In": "LinkedIn",
        "Online Event": "Webinar",
        "Outbound Email": "Cold Email",
        "Google Ads": "Paid Search",
        "Prof Services": "Professional Services",
        "Professional Svcs": "Professional Services",
        "Software": "SaaS",
        "Saas": "SaaS",
        "Fresh Lead": "New",
        "Reached Out": "Contacted",
        "Good Fit": "Qualified",
        "Demo Booked": "Demo Scheduled",
        "Proposal Sent": "Proposal",
        "Decision Stage": "Negotiation",
        "Closed Won": "Won",
        "Closed Lost": "Lost",
        "Long Term": "Nurture",
        "No Reply": "No Response",
        "Email Opened": "Opened",
        "Response": "Replied",
        "Invalid Email": "Bounced",
    }
    return aliases.get(cleaned, cleaned)


def parse_date(value: str) -> date | None:
    value = (value or "").strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%b %d %Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def parse_float(value: str) -> float | None:
    try:
        parsed = float((value or "").strip().replace("$", "").replace(",", ""))
    except ValueError:
        return None
    return parsed if parsed >= 0 else None


def parse_int(value: str) -> int:
    try:
        parsed = int(float((value or "").strip()))
    except ValueError:
        return 0
    return parsed if parsed >= 0 else 0


def parse_bool(value: str) -> bool:
    return (value or "").strip().lower() in {"yes", "y", "true", "1", "booked"}


def score_lead(row: dict) -> int:
    stage = row["stage"]
    stage_score = {
        "New": 12,
        "Contacted": 22,
        "Qualified": 45,
        "Demo Scheduled": 61,
        "Proposal": 73,
        "Negotiation": 86,
        "Won": 100,
        "Lost": 0,
        "Nurture": 28,
    }.get(stage, 10)
    source_bonus = {"Referral": 9, "LinkedIn": 6, "Webinar": 5, "Website": 4, "Partner": 4}.get(row["lead_source"], 0)
    email_bonus = {"Replied": 8, "Opened": 4, "No Response": 0, "Bounced": -8, "Unsubscribed": -10}.get(row["email_status"], 0)
    meeting_bonus = min(10, row["meeting_count"] * 2)
    value_bonus = 10 if row["deal_value"] >= 12000 else 6 if row["deal_value"] >= 7000 else 2
    recency_bonus = 0
    if isinstance(row["days_since_contact"], int):
        if row["days_since_contact"] <= 7:
            recency_bonus = 7
        elif row["days_since_contact"] <= 14:
            recency_bonus = 3
        elif row["days_since_contact"] > 30:
            recency_bonus = -8
    score = stage_score + source_bonus + email_bonus + meeting_bonus + value_bonus + recency_bonus
    if row["followup_status"] == "Overdue":
        score += 5
    return max(0, min(100, round(score)))


def recommended_action(row: dict) -> str:
    stage = row["stage"]
    status = row["followup_status"]
    if stage in {"Won", "Lost"}:
        return "Closed - review for learning"
    if status == "Overdue":
        return "Follow up today"
    if status == "Missing Follow-Up":
        return "Set next follow-up date"
    if status == "Due Today":
        return "Call or email today"
    if stage in {"Proposal", "Negotiation"}:
        return "Confirm decision timeline"
    if stage == "New":
        return "Qualify lead"
    if stage == "Nurture":
        return "Send nurture sequence"
    return "Continue scheduled follow-up"


def clean_dataset(rows: list[dict[str, str]]) -> list[dict]:
    deduped: dict[str, dict] = {}
    for raw in rows:
        created = parse_date(raw["created_date"]) or REPORT_DATE
        last_contact = parse_date(raw["last_contact_date"])
        next_followup = parse_date(raw["next_followup_date"])
        stage = normalize_text(raw["stage"], "New")
        if stage not in STAGE_RANK:
            stage = "New"
        probability = parse_float(raw["probability"])
        if probability is None:
            probability = STAGE_PROBABILITY[stage]
        probability = max(0.0, min(1.0, probability))
        deal_value = parse_float(raw["deal_value"]) or 0.0
        days_since_contact = (REPORT_DATE - last_contact).days if last_contact else None
        days_to_followup = (next_followup - REPORT_DATE).days if next_followup else None

        if stage in {"Won", "Lost"}:
            followup_status = "Closed"
        elif next_followup is None:
            followup_status = "Missing Follow-Up"
        elif days_to_followup < 0:
            followup_status = "Overdue"
        elif days_to_followup == 0:
            followup_status = "Due Today"
        elif days_to_followup <= 7:
            followup_status = "Due This Week"
        else:
            followup_status = "Scheduled"

        clean = {
            "lead_id": raw["lead_id"].strip(),
            "created_date": created.isoformat(),
            "lead_source": normalize_text(raw["lead_source"], "Unknown"),
            "industry": normalize_text(raw["industry"], "Unknown"),
            "region": normalize_text(raw["region"], "Unknown"),
            "company_size": raw["company_size"].strip() or "Unknown",
            "company_name": raw["company_name"].strip() or "Unknown Company",
            "contact_name": raw["contact_name"].strip() or "Unknown Contact",
            "sales_rep": raw["sales_rep"].strip() or "Unassigned",
            "stage": stage,
            "deal_value": round(deal_value, 2),
            "probability": round(probability, 2),
            "expected_value": round(deal_value * probability, 2),
            "last_contact_date": last_contact.isoformat() if last_contact else "",
            "next_followup_date": next_followup.isoformat() if next_followup else "",
            "days_since_contact": days_since_contact if days_since_contact is not None else "",
            "days_to_followup": days_to_followup if days_to_followup is not None else "",
            "followup_status": followup_status,
            "email_status": normalize_text(raw["email_status"], "Unknown"),
            "demo_booked": parse_bool(raw["demo_booked"]),
            "proposal_sent": parse_bool(raw["proposal_sent"]),
            "meeting_count": parse_int(raw["meeting_count"]),
            "lost_reason": normalize_text(raw["lost_reason"], "") if stage == "Lost" else "",
        }
        clean["lead_score"] = score_lead(clean)
        clean["priority"] = (
            "Closed"
            if stage in {"Won", "Lost"}
            else "High"
            if clean["lead_score"] >= 75
            else "Medium"
            if clean["lead_score"] >= 55
            else "Low"
        )
        clean["recommended_action"] = recommended_action(clean)
        current = deduped.get(clean["lead_id"])
        if current is None:
            deduped[clean["lead_id"]] = clean
            continue
        current_rank = STAGE_RANK[current["stage"]]
        new_rank = STAGE_RANK[clean["stage"]]
        current_contact = current["last_contact_date"] or "0000-00-00"
        new_contact = clean["last_contact_date"] or "0000-00-00"
        if (new_rank, new_contact) >= (current_rank, current_contact):
            deduped[clean["lead_id"]] = clean
    return sorted(deduped.values(), key=lambda item: item["lead_id"])


def load_sqlite(rows: list[dict]) -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    columns = list(rows[0])
    column_sql = ", ".join(f"{column} TEXT" for column in columns)
    connection.execute(f"CREATE TABLE crm_leads ({column_sql})")
    placeholders = ", ".join("?" for _ in columns)
    connection.executemany(
        f"INSERT INTO crm_leads ({', '.join(columns)}) VALUES ({placeholders})",
        [[str(row[column]) for column in columns] for row in rows],
    )
    connection.commit()
    connection.close()


def query_rows(sql: str) -> list[dict]:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    rows = [dict(row) for row in connection.execute(sql)]
    connection.close()
    return rows


def export_analysis_tables() -> dict[str, list[dict]]:
    def scalar(sql: str):
        return query_rows(sql)[0]["value"]

    total_leads = scalar("SELECT COUNT(*) AS value FROM crm_leads")
    active_pipeline = scalar("SELECT ROUND(SUM(CAST(deal_value AS REAL)), 2) AS value FROM crm_leads WHERE stage NOT IN ('Won','Lost')")
    expected_pipeline = scalar("SELECT ROUND(SUM(CAST(expected_value AS REAL)), 2) AS value FROM crm_leads WHERE stage NOT IN ('Won','Lost')")
    won_revenue = scalar("SELECT ROUND(SUM(CAST(deal_value AS REAL)), 2) AS value FROM crm_leads WHERE stage = 'Won'")
    overdue_followups = scalar("SELECT COUNT(*) AS value FROM crm_leads WHERE followup_status = 'Overdue'")
    high_priority_leads = scalar("SELECT COUNT(*) AS value FROM crm_leads WHERE priority = 'High' AND stage NOT IN ('Won','Lost')")

    tables = {
        "pipeline_kpi_summary": [
            {
                "metric": "Total leads cleaned",
                "value": total_leads,
            },
            {
                "metric": "Active pipeline value",
                "value": f"${active_pipeline:,.2f}",
            },
            {
                "metric": "Expected pipeline value",
                "value": f"${expected_pipeline:,.2f}",
            },
            {
                "metric": "Won revenue",
                "value": f"${won_revenue:,.2f}",
            },
            {
                "metric": "Overdue follow-ups",
                "value": overdue_followups,
            },
            {
                "metric": "High-priority active leads",
                "value": high_priority_leads,
            },
        ],
        "followup_queue": query_rows(
            """
            SELECT lead_id, company_name, contact_name, sales_rep, stage, lead_source,
                   deal_value, expected_value, lead_score, priority, followup_status,
                   next_followup_date, recommended_action
            FROM crm_leads
            WHERE stage NOT IN ('Won','Lost')
              AND followup_status IN ('Overdue', 'Due Today', 'Due This Week', 'Missing Follow-Up')
            ORDER BY
              CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END,
              CASE followup_status WHEN 'Overdue' THEN 1 WHEN 'Due Today' THEN 2 WHEN 'Missing Follow-Up' THEN 3 ELSE 4 END,
              CAST(expected_value AS REAL) DESC
            LIMIT 80
            """
        ),
        "rep_performance": query_rows(
            """
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
            ORDER BY expected_pipeline DESC
            """
        ),
        "source_performance": query_rows(
            """
            SELECT lead_source,
                   COUNT(*) AS total_leads,
                   SUM(CASE WHEN stage IN ('Qualified','Demo Scheduled','Proposal','Negotiation','Won') THEN 1 ELSE 0 END) AS qualified_or_better,
                   ROUND(100.0 * SUM(CASE WHEN stage = 'Won' THEN 1 ELSE 0 END) / COUNT(*), 1) AS win_rate_pct,
                   ROUND(AVG(CAST(deal_value AS REAL)), 2) AS avg_deal_value,
                   ROUND(SUM(CASE WHEN stage NOT IN ('Won','Lost') THEN CAST(expected_value AS REAL) ELSE 0 END), 2) AS expected_pipeline,
                   SUM(CASE WHEN followup_status = 'Overdue' THEN 1 ELSE 0 END) AS overdue_followups
            FROM crm_leads
            GROUP BY lead_source
            ORDER BY expected_pipeline DESC
            """
        ),
        "stage_conversion": query_rows(
            """
            SELECT stage,
                   COUNT(*) AS lead_count,
                   ROUND(SUM(CAST(deal_value AS REAL)), 2) AS total_deal_value,
                   ROUND(SUM(CAST(expected_value AS REAL)), 2) AS expected_value,
                   ROUND(AVG(CAST(lead_score AS REAL)), 1) AS avg_lead_score
            FROM crm_leads
            GROUP BY stage
            ORDER BY
              CASE stage
                WHEN 'New' THEN 1
                WHEN 'Contacted' THEN 2
                WHEN 'Nurture' THEN 3
                WHEN 'Qualified' THEN 4
                WHEN 'Demo Scheduled' THEN 5
                WHEN 'Proposal' THEN 6
                WHEN 'Negotiation' THEN 7
                WHEN 'Won' THEN 8
                WHEN 'Lost' THEN 9
                ELSE 10
              END
            """
        ),
        "industry_pipeline": query_rows(
            """
            SELECT industry,
                   COUNT(*) AS total_leads,
                   ROUND(SUM(CASE WHEN stage NOT IN ('Won','Lost') THEN CAST(deal_value AS REAL) ELSE 0 END), 2) AS active_pipeline,
                   ROUND(SUM(CASE WHEN stage NOT IN ('Won','Lost') THEN CAST(expected_value AS REAL) ELSE 0 END), 2) AS expected_pipeline,
                   SUM(CASE WHEN priority = 'High' AND stage NOT IN ('Won','Lost') THEN 1 ELSE 0 END) AS high_priority_leads,
                   ROUND(AVG(CAST(deal_value AS REAL)), 2) AS avg_deal_value
            FROM crm_leads
            GROUP BY industry
            ORDER BY expected_pipeline DESC
            """
        ),
    }
    for name, rows in tables.items():
        write_csv(ROOT / "data" / "processed" / f"{name}.csv", rows)
    return tables


def write_sql_file() -> None:
    SQL_PATH.write_text(
        """-- CRM Sales Pipeline & Lead Follow-Up Automation System
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
""",
        encoding="utf-8",
    )


def money(value: float | int | str | None) -> str:
    if value is None or value == "":
        return "$0"
    return f"${float(value):,.0f}"


def write_dashboard(tables: dict[str, list[dict]]) -> None:
    kpis = {row["metric"]: row["value"] for row in tables["pipeline_kpi_summary"]}
    source_rows = tables["source_performance"][:6]
    queue_rows = tables["followup_queue"][:12]
    rep_rows = tables["rep_performance"]
    stage_rows = tables["stage_conversion"]

    def table(headers: list[str], rows: list[dict]) -> str:
        head = "".join(f"<th>{header}</th>" for header in headers)
        body = ""
        for row in rows:
            body += "<tr>" + "".join(f"<td>{row.get(header, '')}</td>" for header in headers) + "</tr>"
        return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CRM Sales Pipeline Dashboard</title>
  <style>
    :root {{
      --ink: #1f2933;
      --muted: #667085;
      --line: #d9e2ec;
      --blue: #2457a6;
      --green: #138a61;
      --amber: #b7791f;
      --red: #b42318;
      --bg: #f6f8fb;
      --panel: #ffffff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      color: var(--ink);
      background: var(--bg);
      line-height: 1.45;
    }}
    header {{
      background: #ffffff;
      border-bottom: 1px solid var(--line);
      padding: 32px;
    }}
    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 28px;
    }}
    h1, h2, h3 {{ margin: 0; }}
    h1 {{ font-size: 32px; }}
    h2 {{ font-size: 20px; margin-bottom: 14px; }}
    p {{ color: var(--muted); max-width: 900px; }}
    .grid {{
      display: grid;
      gap: 16px;
    }}
    .kpis {{
      grid-template-columns: repeat(3, minmax(0, 1fr));
      margin-bottom: 18px;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
    }}
    .metric-label {{
      color: var(--muted);
      font-size: 13px;
      margin-bottom: 8px;
    }}
    .metric-value {{
      font-size: 28px;
      font-weight: 700;
      color: var(--ink);
    }}
    .two-col {{
      grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr);
      align-items: start;
      margin-top: 16px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}
    th, td {{
      border-bottom: 1px solid var(--line);
      padding: 10px 8px;
      text-align: left;
      vertical-align: top;
    }}
    th {{
      color: #344054;
      font-size: 12px;
      background: #f8fafc;
    }}
    .pill {{
      display: inline-block;
      border-radius: 999px;
      padding: 3px 8px;
      background: #e7f0ff;
      color: var(--blue);
      font-size: 12px;
      font-weight: 700;
    }}
    .note {{
      border-left: 4px solid var(--blue);
      padding: 12px 14px;
      background: #eef5ff;
      color: #344054;
      margin-top: 16px;
    }}
    @media (max-width: 820px) {{
      header {{ padding: 24px; }}
      main {{ padding: 18px; }}
      .kpis, .two-col {{ grid-template-columns: 1fr; }}
      .metric-value {{ font-size: 24px; }}
      table {{ font-size: 12px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>CRM Sales Pipeline & Lead Follow-Up Dashboard</h1>
    <p>Portfolio case study showing how messy CRM lead data can be cleaned, scored, prioritized, and turned into a weekly sales operations dashboard.</p>
  </header>
  <main>
    <section class="grid kpis">
      <div class="card"><div class="metric-label">Total Leads Cleaned</div><div class="metric-value">{kpis["Total leads cleaned"]}</div></div>
      <div class="card"><div class="metric-label">Active Pipeline Value</div><div class="metric-value">{kpis["Active pipeline value"]}</div></div>
      <div class="card"><div class="metric-label">Expected Pipeline Value</div><div class="metric-value">{kpis["Expected pipeline value"]}</div></div>
      <div class="card"><div class="metric-label">Won Revenue</div><div class="metric-value">{kpis["Won revenue"]}</div></div>
      <div class="card"><div class="metric-label">Overdue Follow-Ups</div><div class="metric-value">{kpis["Overdue follow-ups"]}</div></div>
      <div class="card"><div class="metric-label">High-Priority Active Leads</div><div class="metric-value">{kpis["High-priority active leads"]}</div></div>
    </section>

    <section class="grid two-col">
      <div class="card">
        <h2>Priority Follow-Up Queue</h2>
        {table(["lead_id", "company_name", "sales_rep", "stage", "expected_value", "lead_score", "priority", "followup_status", "recommended_action"], queue_rows)}
      </div>
      <div class="card">
        <h2>Lead Source Performance</h2>
        {table(["lead_source", "total_leads", "qualified_or_better", "win_rate_pct", "expected_pipeline", "overdue_followups"], source_rows)}
      </div>
    </section>

    <section class="grid two-col">
      <div class="card">
        <h2>Sales Rep Performance</h2>
        {table(["sales_rep", "total_leads", "expected_pipeline", "won_revenue", "overdue_followups", "high_priority_leads", "avg_lead_score"], rep_rows)}
      </div>
      <div class="card">
        <h2>Pipeline by Stage</h2>
        {table(["stage", "lead_count", "total_deal_value", "expected_value", "avg_lead_score"], stage_rows)}
      </div>
    </section>

    <div class="note">
      <span class="pill">Business recommendation</span>
      Prioritize overdue high-score leads, fix missing follow-up dates, and compare sources by expected pipeline instead of raw lead volume.
    </div>
  </main>
</body>
</html>
"""
    (REPORT_DIR / "crm_sales_pipeline_dashboard.html").write_text(html, encoding="utf-8")


def write_executive_summary(tables: dict[str, list[dict]]) -> None:
    kpis = {row["metric"]: row["value"] for row in tables["pipeline_kpi_summary"]}
    top_source = tables["source_performance"][0]
    top_rep = tables["rep_performance"][0]
    top_industry = tables["industry_pipeline"][0]
    text = f"""# Executive Summary

## Project
CRM Sales Pipeline & Lead Follow-Up Automation System

## Business Problem
A small business or startup sales team was tracking leads across messy CRM exports and spreadsheets. Leadership needed a clearer view of pipeline value, lead source quality, sales rep workload, overdue follow-ups, and which leads should be contacted first.

## What I Built
- Generated and cleaned a messy CRM lead dataset with duplicate records, inconsistent stages, missing follow-up dates, invalid deal values, and uneven source labels.
- Built a repeatable Python cleaning workflow.
- Designed a lead scoring model using stage, source quality, email engagement, meeting count, deal value, and contact recency.
- Loaded the clean dataset into SQLite and used SQL to create sales operations reports.
- Created a priority follow-up queue for overdue, due-this-week, and missing-follow-up leads.
- Generated dashboard-ready CSV files and a static HTML dashboard for management review.

## Key Findings
- Total leads cleaned: {kpis["Total leads cleaned"]}
- Active pipeline value: {kpis["Active pipeline value"]}
- Expected pipeline value: {kpis["Expected pipeline value"]}
- Won revenue: {kpis["Won revenue"]}
- Overdue follow-ups: {kpis["Overdue follow-ups"]}
- High-priority active leads: {kpis["High-priority active leads"]}
- Highest expected pipeline source: {top_source["lead_source"]} at {money(top_source["expected_pipeline"])}
- Top rep by expected pipeline: {top_rep["sales_rep"]} at {money(top_rep["expected_pipeline"])}
- Highest expected pipeline industry: {top_industry["industry"]} at {money(top_industry["expected_pipeline"])}

## Recommendation
Use the follow-up queue as a weekly sales operations workflow. The biggest improvement opportunity is not only getting more leads. It is protecting the existing pipeline by fixing missing follow-up dates, prioritizing high-score leads, and reviewing lead sources by expected value instead of raw volume.

## Skills Demonstrated
Python, SQL, SQLite, CRM data cleanup, lead scoring, sales pipeline analysis, dashboard creation, KPI reporting, business operations analysis, and automation-oriented CIST thinking.
"""
    (REPORT_DIR / "executive_summary.md").write_text(text, encoding="utf-8")


def write_portfolio_showcase() -> None:
    html = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CRM Sales Pipeline Case Study</title>
  <style>
    body { margin: 0; font-family: Arial, Helvetica, sans-serif; color: #1f2933; background: #ffffff; line-height: 1.55; }
    main { max-width: 940px; margin: 0 auto; padding: 40px 24px; }
    h1 { font-size: 36px; margin: 0 0 12px; }
    h2 { margin-top: 32px; }
    p, li { color: #475467; }
    a { color: #2457a6; font-weight: 700; }
    .intro { font-size: 18px; color: #344054; }
    .band { background: #f6f8fb; border: 1px solid #d9e2ec; border-radius: 8px; padding: 18px; margin: 22px 0; }
  </style>
</head>
<body>
<main>
  <h1>CRM Sales Pipeline & Lead Follow-Up Automation System</h1>
  <p class="intro">A Business Administration + CIST portfolio case study that turns messy CRM lead data into a cleaned pipeline, lead scoring model, follow-up queue, SQL reports, and management dashboard.</p>
  <div class="band">
    <p><strong>Core idea:</strong> Many small teams do not lose revenue only because they lack leads. They lose revenue because follow-ups are late, CRM data is messy, pipeline value is unclear, and managers cannot quickly see which opportunities deserve attention.</p>
  </div>
  <h2>What I Built</h2>
  <ul>
    <li>Messy CRM lead dataset with duplicates, inconsistent labels, missing follow-up dates, and invalid values.</li>
    <li>Python cleaning pipeline that standardizes data and deduplicates leads.</li>
    <li>Lead scoring model based on stage, source, engagement, value, meetings, and recency.</li>
    <li>SQLite reporting database and SQL analysis queries.</li>
    <li>Follow-up queue for overdue, due, and missing follow-up leads.</li>
    <li>HTML dashboard and executive summary for business users.</li>
  </ul>
  <h2>Business Value</h2>
  <p>This project shows how I can translate messy sales operations data into a practical workflow: clean the data, define the right KPIs, prioritize the next actions, and present the result in a way a business owner, sales manager, or operator can use weekly.</p>
  <h2>Open the Dashboard</h2>
  <p><a href="crm_sales_pipeline_dashboard.html">View CRM Sales Pipeline Dashboard</a></p>
</main>
</body>
</html>
"""
    (REPORT_DIR / "portfolio_showcase.html").write_text(html, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    raw_rows = generate_raw_dataset()
    write_csv(RAW_PATH, raw_rows)
    clean_rows = clean_dataset(raw_rows)
    write_csv(CLEAN_PATH, clean_rows)
    load_sqlite(clean_rows)
    write_sql_file()
    tables = export_analysis_tables()
    write_dashboard(tables)
    write_executive_summary(tables)
    write_portfolio_showcase()
    print(f"Generated {len(raw_rows)} raw CRM rows")
    print(f"Cleaned to {len(clean_rows)} deduplicated leads")
    print(f"Dashboard: {REPORT_DIR / 'crm_sales_pipeline_dashboard.html'}")
    print(f"Executive summary: {REPORT_DIR / 'executive_summary.md'}")


if __name__ == "__main__":
    main()
