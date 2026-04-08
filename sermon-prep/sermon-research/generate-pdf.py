#!/usr/bin/env python3
"""
Sermon Research PDF Generator
Converts structured sermon research JSON into a formatted PDF document.

Usage: python generate-pdf.py <input.json> [output.pdf]

Required: pip install reportlab
"""

import json
import sys
import os

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.colors import HexColor
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable
    )
except ImportError:
    print("reportlab is required. Install it with: pip install reportlab")
    sys.exit(1)


# --- Colors ---

NAVY = HexColor("#1a365d")
DARK_SLATE = HexColor("#2d3748")
BODY_COLOR = HexColor("#1a202c")
LIGHT_GRAY = HexColor("#f7fafc")
MED_GRAY = HexColor("#cbd5e0")
WHITE = HexColor("#ffffff")
ACCENT = HexColor("#2b6cb0")


# --- Styles ---

def build_styles():
    """Create custom paragraph styles for the document."""
    styles = {}

    styles["title"] = ParagraphStyle(
        "Title",
        fontName="Helvetica-Bold",
        fontSize=26,
        leading=32,
        textColor=NAVY,
        spaceAfter=4,
    )

    styles["subtitle"] = ParagraphStyle(
        "Subtitle",
        fontName="Helvetica",
        fontSize=13,
        leading=18,
        textColor=DARK_SLATE,
        spaceAfter=2,
    )

    styles["meta"] = ParagraphStyle(
        "Meta",
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=DARK_SLATE,
        spaceAfter=16,
    )

    styles["section_header"] = ParagraphStyle(
        "SectionHeader",
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=20,
        textColor=NAVY,
        spaceBefore=20,
        spaceAfter=8,
    )

    styles["body"] = ParagraphStyle(
        "Body",
        fontName="Times-Roman",
        fontSize=11,
        leading=15.5,
        textColor=BODY_COLOR,
        spaceAfter=8,
        alignment=TA_JUSTIFY,
    )

    styles["body_bold"] = ParagraphStyle(
        "BodyBold",
        fontName="Times-Bold",
        fontSize=11,
        leading=15.5,
        textColor=BODY_COLOR,
        spaceAfter=4,
    )

    styles["bullet"] = ParagraphStyle(
        "Bullet",
        fontName="Times-Roman",
        fontSize=11,
        leading=15.5,
        textColor=BODY_COLOR,
        leftIndent=20,
        spaceAfter=6,
        bulletIndent=8,
        bulletFontName="Helvetica",
        bulletFontSize=8,
    )

    styles["prompt"] = ParagraphStyle(
        "Prompt",
        fontName="Times-Italic",
        fontSize=11,
        leading=15.5,
        textColor=DARK_SLATE,
        leftIndent=16,
        spaceAfter=8,
    )

    styles["table_header"] = ParagraphStyle(
        "TableHeader",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=WHITE,
    )

    styles["table_cell"] = ParagraphStyle(
        "TableCell",
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=BODY_COLOR,
    )

    styles["table_cell_bold"] = ParagraphStyle(
        "TableCellBold",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=BODY_COLOR,
    )

    styles["footer_note"] = ParagraphStyle(
        "FooterNote",
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=11,
        textColor=MED_GRAY,
        alignment=TA_CENTER,
    )

    styles["brand_heading"] = ParagraphStyle(
        "BrandHeading",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=NAVY,
        spaceAfter=6,
    )

    styles["brand_body"] = ParagraphStyle(
        "BrandBody",
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=DARK_SLATE,
        spaceAfter=4,
    )

    styles["brand_url"] = ParagraphStyle(
        "BrandURL",
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=13.5,
        textColor=ACCENT,
    )

    return styles


# --- Section Builders ---

def add_header(story, data, styles):
    """Add the title block with passage, date, and church info."""
    story.append(Paragraph("Sermon Research", styles["title"]))
    story.append(Paragraph(data.get("passage", ""), styles["subtitle"]))

    meta_parts = []
    if data.get("date"):
        meta_parts.append(data["date"])
    if data.get("pastor_name"):
        meta_parts.append(data["pastor_name"])
    if data.get("church_name"):
        meta_parts.append(data["church_name"])
    if meta_parts:
        story.append(Paragraph("  |  ".join(meta_parts), styles["meta"]))

    story.append(HRFlowable(
        width="100%", thickness=2, color=NAVY,
        spaceBefore=4, spaceAfter=20
    ))


def add_section(story, title, content, styles):
    """Add a section with header, divider, and body paragraphs."""
    story.append(Paragraph(title, styles["section_header"]))
    story.append(HRFlowable(
        width="100%", thickness=0.5, color=MED_GRAY,
        spaceBefore=0, spaceAfter=10
    ))

    if isinstance(content, str):
        for p in content.split("\n\n"):
            p = p.strip()
            if p:
                story.append(Paragraph(p, styles["body"]))
    elif isinstance(content, list):
        for item in content:
            story.append(Paragraph(item, styles["body"]))


def add_word_studies(story, word_studies, styles):
    """Add the word study table."""
    story.append(Paragraph("Key Word Study", styles["section_header"]))
    story.append(HRFlowable(
        width="100%", thickness=0.5, color=MED_GRAY,
        spaceBefore=0, spaceAfter=10
    ))

    if not word_studies:
        story.append(Paragraph("No word studies provided.", styles["body"]))
        return

    headers = [
        "English", "Transliteration",
        "Literal Meaning", "Range of Meaning", "Translations"
    ]

    header_row = [Paragraph(h, styles["table_header"]) for h in headers]
    table_data = [header_row]

    for ws in word_studies:
        translations = ws.get("translations", {})
        trans_parts = []
        for k, v in translations.items():
            trans_parts.append(f"<b>{k}</b>: {v}")
        trans_text = ", ".join(trans_parts) if trans_parts else ""

        row = [
            Paragraph(ws.get("english", ""), styles["table_cell_bold"]),
            Paragraph(ws.get("transliteration", ""), styles["table_cell"]),
            Paragraph(ws.get("literal_meaning", ""), styles["table_cell"]),
            Paragraph(ws.get("range_of_meaning", ""), styles["table_cell"]),
            Paragraph(trans_text, styles["table_cell"]),
        ]
        table_data.append(row)

    col_widths = [
        0.9 * inch, 0.95 * inch,
        1.0 * inch, 1.8 * inch, 2.35 * inch
    ]

    table = Table(table_data, colWidths=col_widths, repeatRows=1)

    style_commands = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 1), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, MED_GRAY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]

    for i in range(1, len(table_data)):
        if i % 2 == 0:
            style_commands.append(
                ("BACKGROUND", (0, i), (-1, i), LIGHT_GRAY)
            )

    table.setStyle(TableStyle(style_commands))
    story.append(table)
    story.append(Spacer(1, 12))


def add_cross_references(story, cross_refs, styles):
    """Add cross-references as a formatted bullet list."""
    story.append(
        Paragraph("Cross-References and Parallel Passages", styles["section_header"])
    )
    story.append(HRFlowable(
        width="100%", thickness=0.5, color=MED_GRAY,
        spaceBefore=0, spaceAfter=10
    ))

    if not cross_refs:
        story.append(Paragraph("No cross-references provided.", styles["body"]))
        return

    for ref in cross_refs:
        reference = ref.get("reference", "")
        connection = ref.get("connection", "")
        conn_type = ref.get("type", "")

        type_label = f" [{conn_type}]" if conn_type else ""
        text = f"<b>{reference}</b>{type_label}: {connection}"
        story.append(Paragraph(text, styles["bullet"], bulletText="\u2022"))


def add_theological_themes(story, themes, styles):
    """Add theological themes with structured sub-sections."""
    story.append(Paragraph("Theological Themes", styles["section_header"]))
    story.append(HRFlowable(
        width="100%", thickness=0.5, color=MED_GRAY,
        spaceBefore=0, spaceAfter=10
    ))

    if not themes:
        story.append(Paragraph("No themes provided.", styles["body"]))
        return

    for theme in themes:
        name = theme.get("name", "")
        in_text = theme.get("in_text", "")
        implication = theme.get("implication", "")

        story.append(Paragraph(name, styles["body_bold"]))
        if in_text:
            story.append(Paragraph(f"In the text: {in_text}", styles["body"]))
        if implication:
            story.append(
                Paragraph(f"For your congregation: {implication}", styles["body"])
            )
        story.append(Spacer(1, 4))


def add_thinking_prompts(story, prompts, styles):
    """Add numbered thinking prompts."""
    story.append(Paragraph("Thinking Prompts", styles["section_header"]))
    story.append(HRFlowable(
        width="100%", thickness=0.5, color=MED_GRAY,
        spaceBefore=0, spaceAfter=10
    ))

    if not prompts:
        story.append(Paragraph("No prompts provided.", styles["body"]))
        return

    for i, prompt in enumerate(prompts, 1):
        story.append(Paragraph(f"{i}. {prompt}", styles["prompt"]))


def add_reachright_footer(story, styles):
    """Add the REACHRIGHT branding section at the end of the document."""
    story.append(Spacer(1, 30))
    story.append(HRFlowable(
        width="100%", thickness=1, color=NAVY,
        spaceBefore=8, spaceAfter=12
    ))

    story.append(Paragraph("About REACHRIGHT", styles["brand_heading"]))

    story.append(Paragraph(
        "Built by REACHRIGHT. We help churches get found online: custom websites, "
        "Google Ad Grants, local SEO, and social media done for you. "
        "If this tool saved you time this week, we can save you a lot more.",
        styles["brand_body"]
    ))

    story.append(Paragraph("reachrightstudios.com", styles["brand_url"]))


# --- Page Footer ---

def add_page_footer(canvas_obj, doc):
    """Draw page number and REACHRIGHT branding on every page."""
    canvas_obj.saveState()

    # "Powered by REACHRIGHT" on the left
    canvas_obj.setFont("Helvetica", 7)
    canvas_obj.setFillColor(MED_GRAY)
    canvas_obj.drawString(0.75 * inch, 0.45 * inch, "Powered by REACHRIGHT")

    # Page number on the right
    page_num = canvas_obj.getPageNumber()
    canvas_obj.drawRightString(
        letter[0] - 0.75 * inch, 0.45 * inch, f"Page {page_num}"
    )

    canvas_obj.restoreState()


# --- Main Generator ---

def generate_pdf(json_path, output_path=None):
    """Generate a formatted PDF from sermon research JSON data."""

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not output_path:
        passage = data.get("passage", "research")
        safe_name = passage.replace(":", "-").replace(" ", "-")
        output_path = f"Sermon-Research-{safe_name}.pdf"

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title=f"Sermon Research: {data.get('passage', '')}",
        author=data.get("pastor_name", ""),
    )

    styles = build_styles()
    story = []

    # Title block
    add_header(story, data, styles)

    # Section 1: Passage Context
    if data.get("passage_context"):
        add_section(story, "Passage Context", data["passage_context"], styles)

    # Section 2: Historical and Cultural Background
    if data.get("historical_background"):
        add_section(
            story, "Historical and Cultural Background",
            data["historical_background"], styles
        )

    # Section 3: Word Studies
    if data.get("word_studies"):
        add_word_studies(story, data["word_studies"], styles)

    # Section 4: Commentary Insights
    if data.get("commentary_insights"):
        add_section(
            story, "Commentary Insights",
            data["commentary_insights"], styles
        )

    # Section 5: Cross-References
    if data.get("cross_references"):
        add_cross_references(story, data["cross_references"], styles)

    # Section 6: Theological Themes
    if data.get("theological_themes"):
        add_theological_themes(story, data["theological_themes"], styles)

    # Section 7: Thinking Prompts
    if data.get("thinking_prompts"):
        add_thinking_prompts(story, data["thinking_prompts"], styles)

    # REACHRIGHT branding footer
    add_reachright_footer(story, styles)

    doc.build(story, onFirstPage=add_page_footer, onLaterPages=add_page_footer)

    return os.path.abspath(output_path)


# --- CLI Entry ---

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate-pdf.py <input.json> [output.pdf]")
        sys.exit(1)

    json_input = sys.argv[1]
    pdf_output = sys.argv[2] if len(sys.argv) > 2 else None

    result_path = generate_pdf(json_input, pdf_output)
    print(f"PDF generated: {result_path}")
