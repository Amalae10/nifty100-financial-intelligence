from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import mm

SRC = Path("docs/acceptance_checklist.md")
OUT = Path("docs/acceptance_checklist.pdf")

styles = getSampleStyleSheet()
styles["Title"].alignment = TA_CENTER

doc = SimpleDocTemplate(
    str(OUT),
    pagesize=A4,
    rightMargin=18*mm,
    leftMargin=18*mm,
    topMargin=18*mm,
    bottomMargin=18*mm,
)

story = []

for line in SRC.read_text(encoding="utf-8-sig").splitlines():
    line = line.strip()

    if not line:
        story.append(Spacer(1, 6))
        continue

    # Skip markdown table separator
    if line.startswith("|---"):
        continue

    if line.startswith("# "):
        story.append(Paragraph(line[2:], styles["Title"]))

    elif line.startswith("## "):
        story.append(Paragraph(line[3:], styles["Heading2"]))

    elif line.startswith("### "):
        story.append(Paragraph(line[4:], styles["Heading3"]))

    elif line.startswith("|"):
        cells = [x.strip() for x in line.strip("|").split("|")]
        story.append(
            Paragraph(" | ".join(cells), styles["BodyText"])
        )

    elif line.startswith("- "):
        story.append(
            Paragraph("• " + line[2:], styles["BodyText"])
        )

    else:
        story.append(Paragraph(line, styles["BodyText"]))

    story.append(Spacer(1, 4))

doc.build(story)

print(f"Created: {OUT}")