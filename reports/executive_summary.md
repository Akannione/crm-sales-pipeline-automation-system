# Executive Summary

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
- Total leads cleaned: 760
- Active pipeline value: $4,462,179.61
- Expected pipeline value: $1,481,020.91
- Won revenue: $588,553.23
- Overdue follow-ups: 442
- High-priority active leads: 188
- Highest expected pipeline source: Website at $350,336
- Top rep by expected pipeline: Riley Carter at $369,530
- Highest expected pipeline industry: SaaS at $432,720

## Recommendation
Use the follow-up queue as a weekly sales operations workflow. The biggest improvement opportunity is not only getting more leads. It is protecting the existing pipeline by fixing missing follow-up dates, prioritizing high-score leads, and reviewing lead sources by expected value instead of raw volume.

## Skills Demonstrated
Python, SQL, SQLite, CRM data cleanup, lead scoring, sales pipeline analysis, dashboard creation, KPI reporting, business operations analysis, and automation-oriented CIST thinking.
