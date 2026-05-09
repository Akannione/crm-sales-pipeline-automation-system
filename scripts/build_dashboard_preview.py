from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "assets" / "screenshots" / "crm_dashboard_preview.png"


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_card(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], label: str, value: str) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=16, fill="#ffffff", outline="#d9e2ec", width=2)
    draw.text((x1 + 24, y1 + 24), label, fill="#667085", font=font(22))
    draw.text((x1 + 24, y1 + 62), value, fill="#1f2933", font=font(38, bold=True))


def draw_table(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    width: int,
    title: str,
    headers: list[str],
    rows: list[dict[str, str]],
) -> None:
    draw.rounded_rectangle((x, y, x + width, y + 360), radius=16, fill="#ffffff", outline="#d9e2ec", width=2)
    draw.text((x + 22, y + 20), title, fill="#1f2933", font=font(28, bold=True))
    top = y + 70
    col_width = width // len(headers)
    draw.rectangle((x + 16, top, x + width - 16, top + 42), fill="#f6f8fb")
    for index, header in enumerate(headers):
        draw.text((x + 24 + index * col_width, top + 10), header, fill="#475467", font=font(16, bold=True))
    row_y = top + 50
    for row in rows[:6]:
        draw.line((x + 16, row_y + 34, x + width - 16, row_y + 34), fill="#e5eaf0", width=1)
        for index, header in enumerate(headers):
            value = str(row.get(header, ""))
            if len(value) > 22:
                value = value[:20] + ".."
            draw.text((x + 24 + index * col_width, row_y), value, fill="#344054", font=font(15))
        row_y += 40


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    kpi_rows = load_csv(ROOT / "data" / "processed" / "pipeline_kpi_summary.csv")
    source_rows = load_csv(ROOT / "data" / "processed" / "source_performance.csv")
    queue_rows = load_csv(ROOT / "data" / "processed" / "followup_queue.csv")
    kpis = {row["metric"]: row["value"] for row in kpi_rows}

    image = Image.new("RGB", (1600, 1000), "#f6f8fb")
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, 1600, 150), fill="#ffffff")
    draw.text((70, 42), "CRM Sales Pipeline & Lead Follow-Up Dashboard", fill="#1f2933", font=font(42, bold=True))
    draw.text((72, 100), "Clean CRM data, lead scoring, follow-up priority, and sales pipeline visibility.", fill="#667085", font=font(22))

    cards = [
        ("Total Leads Cleaned", kpis["Total leads cleaned"]),
        ("Active Pipeline", kpis["Active pipeline value"]),
        ("Expected Pipeline", kpis["Expected pipeline value"]),
        ("Won Revenue", kpis["Won revenue"]),
        ("Overdue Follow-Ups", kpis["Overdue follow-ups"]),
        ("High-Priority Leads", kpis["High-priority active leads"]),
    ]
    x_positions = [70, 560, 1050]
    y_positions = [190, 360]
    card_index = 0
    for y in y_positions:
        for x in x_positions:
            label, value = cards[card_index]
            draw_card(draw, (x, y, x + 430, y + 130), label, value)
            card_index += 1

    draw_table(
        draw,
        70,
        550,
        930,
        "Priority Follow-Up Queue",
        ["company_name", "sales_rep", "stage", "expected_value", "priority", "followup_status"],
        queue_rows,
    )
    draw_table(
        draw,
        1040,
        550,
        490,
        "Lead Sources",
        ["lead_source", "total_leads", "win_rate_pct", "expected_pipeline"],
        source_rows,
    )

    draw.text((70, 940), "Recommendation: prioritize overdue high-score leads, fix missing follow-up dates, and review sources by expected value.", fill="#475467", font=font(20))
    image.save(OUT_PATH)
    print(OUT_PATH)


if __name__ == "__main__":
    main()
