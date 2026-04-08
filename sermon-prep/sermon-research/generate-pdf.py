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
        HRFlowable, KeepTogether
    )
except ImportError:
    print("reportlab is required. Install it with: pip install reportlab")
    sys.exit(1)


# --- Color Palette ---
# Editorial study-bible aesthetic: deep navy + warm gold accent

NAVY = HexColor("#1B2A4A")
GOLD = HexColor("#B8860B")
GOLD_LIGHT = HexColor("#D4A843")
BODY_COLOR = HexColor("#2D3436")
SLATE = HexColor("#4A5568")
MED_GRAY = HexColor("#A0AEC0")
LIGHT_BG = HexColor("#F8F6F1")
RULE_GRAY = HexColor("#D1CDC4")
WHITE = HexColor("#FFFFFF")

# Content width: letter (8.5") minus 1" margins each side = 6.5"
CONTENT_WIDTH = 6.5 * inch
NO_BORDER = {"style": None}


# --- Styles ---

def build_styles():
    """Create custom paragraph styles for the document."""
    s = {}

    # --- Title banner styles (white on navy) ---
    s["title"] = ParagraphStyle(
        "Title", fontName="Helvetica-Bold", fontSize=28, leading=34,
        textColor=WHITE, spaceAfter=2,
    )
    s["passage"] = ParagraphStyle(
        "Passage", fontName="Helvetica", fontSize=16, leading=22,
        textColor=HexColor("#C8D6E5"), spaceAfter=6,
    )
    s["meta"] = ParagraphStyle(
        "Meta", fontName="Helvetica", fontSize=9, leading=13,
        textColor=HexColor("#8899AA"),
    )

    # --- Section headers ---
    s["section_header"] = ParagraphStyle(
        "SectionHeader", fontName="Helvetica-Bold", fontSize=14, leading=18,
        textColor=NAVY, spaceBefore=24, spaceAfter=2,
    )

    # --- Body ---
    s["body"] = ParagraphStyle(
        "Body", fontName="Times-Roman", fontSize=11, leading=16,
        textColor=BODY_COLOR, spaceAfter=10, alignment=TA_JUSTIFY,
    )
    s["body_bold"] = ParagraphStyle(
        "BodyBold", fontName="Helvetica-Bold", fontSize=11, leading=16,
        textColor=NAVY, spaceAfter=4,
    )
    s["body_label"] = ParagraphStyle(
        "BodyLabel", fontName="Helvetica-Bold", fontSize=9.5, leading=14,
        textColor=GOLD, spaceAfter=2,
    )
    s["body_content"] = ParagraphStyle(
        "BodyContent", fontName="Times-Roman", fontSize=11, leading=16,
        textColor=BODY_COLOR, spaceAfter=8, leftIndent=0,
        alignment=TA_JUSTIFY,
    )

    # --- Bullets ---
    s["bullet"] = ParagraphStyle(
        "Bullet", fontName="Times-Roman", fontSize=11, leading=16,
        textColor=BODY_COLOR, leftIndent=18, spaceAfter=8,
        bulletIndent=4, bulletFontName="Helvetica-Bold",
        bulletFontSize=9, bulletColor=GOLD,
    )

    # --- Thinking prompts (inside shaded box) ---
    s["prompt"] = ParagraphStyle(
        "Prompt", fontName="Times-Italic", fontSize=10.5, leading=15,
        textColor=SLATE, spaceAfter=6, leftIndent=0,
    )

    # --- Table styles ---
    s["table_header"] = ParagraphStyle(
        "TableHeader", fontName="Helvetica-Bold", fontSize=8.5,
        leading=11, textColor=WHITE,
    )
    s["table_cell"] = ParagraphStyle(
        "TableCell", fontName="Helvetica", fontSize=8.5,
        leading=12, textColor=BODY_COLOR,
    )
    s["table_cell_bold"] = ParagraphStyle(
        "TableCellBold", fontName="Helvetica-Bold", fontSize=8.5,
        leading=12, textColor=NAVY,
    )

    # --- REACHRIGHT banner styles (white on navy) ---
    s["brand_body"] = ParagraphStyle(
        "BrandBody", fontName="Helvetica", fontSize=9, leading=13,
        textColor=HexColor("#C8D6E5"),
    )
    s["brand_url"] = ParagraphStyle(
        "BrandURL", fontName="Helvetica-Bold", fontSize=10, leading=14,
        textColor=GOLD_LIGHT, spaceBefore=4,
    )

    return s


# --- Helper: Section header with gold accent ---

def section_header(story, title, styles):
    """Add a section header with gold accent underline."""
    story.append(Paragraph(title, styles["section_header"]))
    story.append(HRFlowable(
        width="100%", thickness=2, color=GOLD,
        spaceBefore=2, spaceAfter=14
    ))


# --- Title Banner ---

def add_title_banner(story, data, styles):
    """Full-width navy banner with passage info."""
    meta_parts = []
    if data.get("date"):
        meta_parts.append(data["date"])
    if data.get("pastor_name"):
        meta_parts.append(data["pastor_name"])
    if data.get("church_name"):
        meta_parts.append(data["church_name"])

    banner_content = []
    banner_content.append(Paragraph("SERMON RESEARCH", styles["title"]))
    banner_content.append(Paragraph(data.get("passage", ""), styles["passage"]))
    if meta_parts:
        banner_content.append(Spacer(1, 4))
        banner_content.append(
            Paragraph("  |  ".join(meta_parts), styles["meta"])
        )

    # Wrap in a table cell for navy background
    banner = Table(
        [[banner_content]],
        colWidths=[CONTENT_WIDTH],
    )
    banner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("LEFTPADDING", (0, 0), (-1, -1), 24),
        ("RIGHTPADDING", (0, 0), (-1, -1), 24),
        ("TOPPADDING", (0, 0), (-1, -1), 24),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 20),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(banner)

    # Gold accent line below banner
    story.append(HRFlowable(
        width="100%", thickness=3, color=GOLD,
        spaceBefore=0, spaceAfter=24
    ))


# --- Text Section ---

def add_section(story, title, content, styles):
    """Add a text section with header and body paragraphs."""
    section_header(story, title, styles)

    if isinstance(content, str):
        for p in content.split("\n\n"):
            p = p.strip()
            if p:
                story.append(Paragraph(p, styles["body"]))
    elif isinstance(content, list):
        for item in content:
            story.append(Paragraph(item, styles["body"]))


# --- Word Study Table ---

def add_word_studies(story, word_studies, styles):
    """Add the word study table with refined styling."""
    section_header(story, "Key Word Study", styles)

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

    col_widths = [0.9 * inch, 0.95 * inch, 1.0 * inch, 1.8 * inch, 1.85 * inch]

    table = Table(table_data, colWidths=col_widths, repeatRows=1)

    style_commands = [
        # Header row
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("TOPPADDING", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        # Gold line below header
        ("LINEBELOW", (0, 0), (-1, 0), 2, GOLD),
        # All cells
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 1), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        # Subtle grid
        ("GRID", (0, 0), (-1, 0), 0, WHITE),
        ("LINEBELOW", (0, 1), (-1, -1), 0.5, RULE_GRAY),
        ("LINEBEFORE", (1, 1), (-1, -1), 0.5, RULE_GRAY),
    ]

    # Alternating row backgrounds
    for i in range(1, len(table_data)):
        if i % 2 == 0:
            style_commands.append(("BACKGROUND", (0, i), (-1, i), LIGHT_BG))

    table.setStyle(TableStyle(style_commands))
    story.append(table)
    story.append(Spacer(1, 16))


# --- Cross-References ---

def add_cross_references(story, cross_refs, styles):
    """Add cross-references as a formatted bullet list."""
    section_header(story, "Cross-References and Parallel Passages", styles)

    if not cross_refs:
        story.append(Paragraph("No cross-references provided.", styles["body"]))
        return

    for ref in cross_refs:
        reference = ref.get("reference", "")
        connection = ref.get("connection", "")
        conn_type = ref.get("type", "")

        type_label = f'  <font color="#{SLATE.hexval()[2:]}">[{conn_type}]</font>' if conn_type else ""
        text = f"<b>{reference}</b>{type_label}:  {connection}"
        story.append(Paragraph(text, styles["bullet"], bulletText="\u2022"))


# --- Theological Themes ---

def add_theological_themes(story, themes, styles):
    """Add theological themes with structured sub-sections."""
    section_header(story, "Theological Themes", styles)

    if not themes:
        story.append(Paragraph("No themes provided.", styles["body"]))
        return

    for theme in themes:
        name = theme.get("name", "")
        in_text = theme.get("in_text", "")
        implication = theme.get("implication", "")

        # Theme name with gold underline
        story.append(Paragraph(name, styles["body_bold"]))
        story.append(HRFlowable(
            width="30%", thickness=1.5, color=GOLD,
            spaceBefore=0, spaceAfter=8
        ))

        if in_text:
            story.append(Paragraph("IN THE TEXT", styles["body_label"]))
            story.append(Paragraph(in_text, styles["body_content"]))

        if implication:
            story.append(Paragraph("FOR YOUR CONGREGATION", styles["body_label"]))
            story.append(Paragraph(implication, styles["body_content"]))

        story.append(Spacer(1, 8))


# --- Thinking Prompts (shaded box) ---

def add_thinking_prompts(story, prompts, styles):
    """Add thinking prompts inside a shaded container with gold left border."""
    section_header(story, "Thinking Prompts", styles)

    if not prompts:
        story.append(Paragraph("No prompts provided.", styles["body"]))
        return

    # Build prompt paragraphs
    prompt_elements = []
    for i, prompt in enumerate(prompts, 1):
        prompt_elements.append(
            Paragraph(f"<b>{i}.</b>  {prompt}", styles["prompt"])
        )

    # Wrap in a table for gold-left-border + cream background
    # Two columns: thin gold bar | prompt content
    gold_bar_width = 4
    content_col_width = CONTENT_WIDTH - gold_bar_width - 2

    box = Table(
        [[None, prompt_elements]],
        colWidths=[gold_bar_width, content_col_width],
    )
    box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), GOLD),
        ("BACKGROUND", (1, 0), (1, -1), LIGHT_BG),
        ("LEFTPADDING", (0, 0), (0, -1), 0),
        ("RIGHTPADDING", (0, 0), (0, -1), 0),
        ("TOPPADDING", (0, 0), (0, -1), 0),
        ("BOTTOMPADDING", (0, 0), (0, -1), 0),
        ("LEFTPADDING", (1, 0), (1, -1), 16),
        ("RIGHTPADDING", (1, 0), (1, -1), 16),
        ("TOPPADDING", (1, 0), (1, -1), 14),
        ("BOTTOMPADDING", (1, 0), (1, -1), 14),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(box)


# --- REACHRIGHT Branding Banner ---

def add_reachright_footer(story, styles):
    """Add REACHRIGHT branding as a navy banner at the end."""
    story.append(Spacer(1, 30))

    brand_content = []
    brand_content.append(Paragraph(
        "Built by REACHRIGHT. We help churches get found online: custom websites, "
        "Google Ad Grants, local SEO, and social media done for you. "
        "If this tool saved you time this week, we can save you a lot more.",
        styles["brand_body"]
    ))
    brand_content.append(Paragraph("reachrightstudios.com", styles["brand_url"]))

    banner = Table(
        [[brand_content]],
        colWidths=[CONTENT_WIDTH],
    )
    banner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("LEFTPADDING", (0, 0), (-1, -1), 20),
        ("RIGHTPADDING", (0, 0), (-1, -1), 20),
        ("TOPPADDING", (0, 0), (-1, -1), 16),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 16),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        # Gold top accent
        ("LINEABOVE", (0, 0), (-1, 0), 3, GOLD),
    ]))
    story.append(banner)


# --- Page Footer (canvas callback) ---

def add_page_footer(canvas_obj, doc):
    """Draw footer with thin gold rule, branding, and page number."""
    canvas_obj.saveState()
    page_width = letter[0]
    margin = 1.0 * inch

    # Thin gold rule
    canvas_obj.setStrokeColor(GOLD)
    canvas_obj.setLineWidth(0.5)
    canvas_obj.line(margin, 0.6 * inch, page_width - margin, 0.6 * inch)

    # "Powered by REACHRIGHT" left
    canvas_obj.setFont("Helvetica", 7)
    canvas_obj.setFillColor(MED_GRAY)
    canvas_obj.drawString(margin, 0.42 * inch, "Powered by REACHRIGHT")

    # Page number right
    page_num = canvas_obj.getPageNumber()
    canvas_obj.drawRightString(
        page_width - margin, 0.42 * inch, f"Page {page_num}"
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
        leftMargin=1.0 * inch,
        rightMargin=1.0 * inch,
        topMargin=0.85 * inch,
        bottomMargin=0.85 * inch,
        title=f"Sermon Research: {data.get('passage', '')}",
        author=data.get("pastor_name", ""),
    )

    styles = build_styles()
    story = []

    # Title banner
    add_title_banner(story, data, styles)

    # Sections
    if data.get("passage_context"):
        add_section(story, "Passage Context", data["passage_context"], styles)

    if data.get("historical_background"):
        add_section(
            story, "Historical and Cultural Background",
            data["historical_background"], styles
        )

    if data.get("word_studies"):
        add_word_studies(story, data["word_studies"], styles)

    if data.get("commentary_insights"):
        add_section(
            story, "Commentary Insights",
            data["commentary_insights"], styles
        )

    if data.get("cross_references"):
        add_cross_references(story, data["cross_references"], styles)

    if data.get("theological_themes"):
        add_theological_themes(story, data["theological_themes"], styles)

    if data.get("thinking_prompts"):
        add_thinking_prompts(story, data["thinking_prompts"], styles)

    # REACHRIGHT branding
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
