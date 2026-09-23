from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.units import mm
import re

SOURCE = Path("docs/analyst_guide.md")
OUTPUT = Path("docs/analyst_guide.pdf")

styles = getSampleStyleSheet()
styles["Title"].alignment = TA_CENTER

doc = SimpleDocTemplate(
    str(OUTPUT),
    pagesize=A4,
    rightMargin=20 * mm,
    leftMargin=20 * mm,
    topMargin=20 * mm,
    bottomMargin=20 * mm,
)

story = [
    Paragraph("N100 Financial Intelligence Platform", styles["Title"]),
    Spacer(1, 8),
    Paragraph("Analyst Guide", styles["Heading1"]),
    PageBreak(),
]

text = SOURCE.read_text(encoding="utf-8")

for line in text.splitlines():
    line = line.strip()

    if not line:
        story.append(Spacer(1, 6))
        continue

    # Remove basic Markdown formatting
    clean = re.sub(r"\*\*(.*?)\*\*", r"\1", line)
    clean = re.sub(r"`(.*?)`", r"\1", clean)
    clean = clean.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    if clean.startswith("### "):
        story.append(Paragraph(clean[4:], styles["Heading3"]))
    elif clean.startswith("## "):
        story.append(Paragraph(clean[3:], styles["Heading2"]))
    elif clean.startswith("# "):
        story.append(Paragraph(clean[2:], styles["Heading1"]))
    elif clean.startswith("- "):
        story.append(Paragraph("• " + clean[2:], styles["BodyText"]))
    else:
        story.append(Paragraph(clean, styles["BodyText"]))

    story.append(Spacer(1, 4))

doc.build(story)

print(f"Created: {OUTPUT}")