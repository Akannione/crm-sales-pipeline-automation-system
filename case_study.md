# Case Study: CRM Sales Pipeline & Lead Follow-Up Automation System

## One-Line Summary

I built a Python and SQL workflow that cleans messy CRM lead data, scores opportunities, prioritizes follow-ups, and creates a sales pipeline dashboard for weekly business review.

## My Positioning

This project is built from a Business Administration + CIST perspective. The goal is not just to create charts. The goal is to show that I can translate a business operations problem into a technical workflow that improves clarity, follow-up discipline, and revenue visibility.

## Business Problem

Many small businesses, agencies, startups, and service teams track leads in a CRM, spreadsheet, or mixed set of tools. The team may have demand, but the data is often messy:

- Leads are duplicated.
- Lead sources are inconsistent.
- Sales stages are not standardized.
- Follow-up dates are missing or overdue.
- Deal values are incomplete or invalid.
- Managers cannot quickly see pipeline risk.
- Sales reps do not have a clear next-action queue.

The result is lost momentum. Leads go cold, managers overvalue raw lead count, and high-value opportunities do not always get contacted on time.

## Solution Built

I created a repeatable CRM sales operations workflow.

1. **Raw data generation:** Built a realistic messy CRM dataset with duplicate leads, inconsistent labels, missing fields, and invalid values.
2. **Python cleaning pipeline:** Standardized sources, industries, stages, email statuses, dates, values, and boolean fields.
3. **Deduplication:** Reduced raw CRM exports into one clean record per lead.
4. **Lead scoring:** Created a score using stage, source quality, email engagement, meeting count, deal value, follow-up status, and contact recency.
5. **Follow-up logic:** Classified leads as overdue, due today, due this week, missing follow-up, scheduled, or closed.
6. **SQLite reporting database:** Loaded the cleaned data into SQLite for reusable analysis.
7. **SQL analysis:** Created KPI summary, follow-up queue, rep performance, source performance, stage conversion, and industry pipeline outputs.
8. **Dashboard and summary:** Generated a static HTML dashboard and executive summary for sales operations review.

## Tools Used

- Python
- SQL
- SQLite
- CSV
- HTML/CSS
- CRM-style reporting logic
- KPI design
- Sales operations analysis

## Business Questions Answered

- How much active pipeline does the team have?
- Which leads should be followed up first?
- Which reps have the most expected pipeline and overdue follow-ups?
- Which lead sources produce the strongest opportunities?
- Which stages hold the most pipeline value?
- Which industries represent the strongest current opportunity?
- Where is revenue at risk because follow-up dates are missing or overdue?

## Why This Project Matters

This project is highly relevant to freelance and entry-level analytics work because many companies do not need complex machine learning first. They need their CRM exports cleaned, their pipeline organized, their overdue follow-ups visible, and their weekly reporting made repeatable.

That is a practical, sellable business systems problem.

## What This Demonstrates

This case study shows that I can:

- Clean messy CRM and spreadsheet data.
- Build repeatable reporting workflows.
- Use SQL to analyze pipeline performance.
- Design business-friendly KPI logic.
- Create lead scoring and follow-up prioritization rules.
- Build dashboards that support action, not just visuals.
- Communicate recommendations in plain business language.

## Freelance Relevance

This project supports freelance offers such as:

- CRM cleanup
- Excel/CSV lead list cleanup
- Sales pipeline dashboard creation
- Lead scoring setup
- Follow-up tracking systems
- Weekly sales reporting
- Small business reporting automation
- Sales operations process documentation

## Next Iteration

The next version should include a Google Sheets version, a Power BI version, and an optional AI-generated weekly sales summary.

