# Skill PDF Upgrades Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add formatted PDF output to 8 pastor skills using a shared Python library with two branding modes (REACHRIGHT and church-clean).

**Architecture:** Extract shared styling, layout components, and branding logic from the existing sermon-research generator into `shared/pdf_utils.py`. Each skill gets its own `generate-pdf.py` that imports shared utilities and adds skill-specific layout. Each skill's SKILL.md gets an Output Format section with JSON schema and generation instructions.

**Tech Stack:** Python 3, reportlab

**Spec:** `docs/superpowers/specs/2026-04-08-skill-pdf-upgrades-design.md`

---

## File Map

### New files
- `shared/pdf_utils.py` - Shared PDF library (colors, styles, layout components, branding)
- `sermon-prep/sermon-series/generate-pdf.py` - Sermon series PDF generator
- `sermon-prep/sermon-brainstorm/generate-pdf.py` - Sermon brief PDF generator
- `sermon-repurposing/small-group-questions/generate-pdf.py` - Small group guide PDF generator
- `pastoral-rhythm/meeting-agenda/generate-pdf.py` - Meeting agenda PDF generator
- `written-communication/church-letter/generate-pdf.py` - Church letter PDF generator
- `pastoral-rhythm/midweek-devotional/generate-pdf.py` - Midweek devotional PDF generator
- `written-communication/announcement-script/generate-pdf.py` - Announcement script PDF generator

### Modified files
- `sermon-prep/sermon-research/generate-pdf.py` - Refactor to import from shared library
- `sermon-prep/sermon-series/SKILL.md` - Add Output Format section
- `sermon-prep/sermon-brainstorm/SKILL.md` - Add Output Format section
- `sermon-repurposing/small-group-questions/SKILL.md` - Add Output Format section
- `pastoral-rhythm/meeting-agenda/SKILL.md` - Add Output Format section
- `written-communication/church-letter/SKILL.md` - Add Output Format section
- `pastoral-rhythm/midweek-devotional/SKILL.md` - Add Output Format section
- `written-communication/announcement-script/SKILL.md` - Add Output Format section

---

## Task 1: Build shared/pdf_utils.py

**Files:**
- Create: `shared/pdf_utils.py`

- [ ] **Step 1: Create the shared PDF utility module**

Extract all reusable components from `sermon-prep/sermon-research/generate-pdf.py` into `shared/pdf_utils.py`. The module must contain:

**Color palette constants** (copied exactly from sermon-research):
```python
NAVY = HexColor("#1B2A4A")
GOLD = HexColor("#B8860B")
GOLD_LIGHT = HexColor("#D4A843")
BODY_COLOR = HexColor("#2D3436")
SLATE = HexColor("#4A5568")
MED_GRAY = HexColor("#A0AEC0")
LIGHT_BG = HexColor("#F8F6F1")
RULE_GRAY = HexColor("#D1CDC4")
WHITE = HexColor("#FFFFFF")
CONTENT_WIDTH = 6.5 * inch
```

**`build_styles()`** - Returns a dict of all ParagraphStyle objects. Copied exactly from sermon-research's `build_styles()` function. Keys: title, passage, meta, section_header, body, body_bold, body_label, body_content, bullet, prompt, table_header, table_cell, table_cell_bold, brand_body, brand_url.

**`section_header(story, title, styles)`** - Adds H2 header with gold accent underline. Copied from sermon-research.

**`add_section(story, title, content, styles)`** - Adds text section. If content is a string, splits on `\n\n`. If content is a list, iterates. Copied from sermon-research.

**`add_bullet_list(story, items, styles)`** - New function. Takes a list of strings, renders each as a gold-bulleted paragraph using styles["bullet"]. Uses bullet character `\u2022`.
```python
def add_bullet_list(story, items, styles):
    for item in items:
        story.append(Paragraph(item, styles["bullet"], bulletText="\u2022"))
```

**`add_table(story, headers, rows, col_widths, styles)`** - New generic function. Builds a table with navy header row, gold line below header, alternating cream row backgrounds, subtle grid. Parameters:
- `headers`: list of strings
- `rows`: list of lists of strings (plain text, not Paragraph objects)
- `col_widths`: list of floats (in inches, will be multiplied by `inch`)
- `styles`: the styles dict

```python
def add_table(story, headers, rows, col_widths, styles):
    header_row = [Paragraph(h, styles["table_header"]) for h in headers]
    table_data = [header_row]
    for row in rows:
        table_data.append([Paragraph(str(cell), styles["table_cell"]) for cell in row])

    widths = [w * inch for w in col_widths]
    table = Table(table_data, colWidths=widths, repeatRows=1)

    style_commands = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("TOPPADDING", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("LINEBELOW", (0, 0), (-1, 0), 2, GOLD),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 1), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, 0), 0, WHITE),
        ("LINEBELOW", (0, 1), (-1, -1), 0.5, RULE_GRAY),
        ("LINEBEFORE", (1, 1), (-1, -1), 0.5, RULE_GRAY),
    ]
    for i in range(1, len(table_data)):
        if i % 2 == 0:
            style_commands.append(("BACKGROUND", (0, i), (-1, i), LIGHT_BG))

    table.setStyle(TableStyle(style_commands))
    story.append(table)
    story.append(Spacer(1, 16))
```

**`add_shaded_box(story, elements, styles)`** - Extracted from sermon-research's `add_thinking_prompts`. Renders a gold-left-border + cream-background container around arbitrary flowable elements.
```python
def add_shaded_box(story, elements, styles):
    gold_bar_width = 4
    content_col_width = CONTENT_WIDTH - gold_bar_width - 2
    box = Table(
        [[None, elements]],
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
```

**`add_title_banner(story, title_text, subtitle_text, meta_parts, styles)`** - Generalized from sermon-research. Parameters:
- `title_text`: e.g. "SERMON RESEARCH" or "STAFF MEETING AGENDA"
- `subtitle_text`: e.g. "Romans 8:1-11" or "Hold Fast"
- `meta_parts`: list of strings joined with " | " (e.g. ["2026-04-08", "Pastor Thomas", "New Hope Hawaii Kai"])

```python
def add_title_banner(story, title_text, subtitle_text, meta_parts, styles):
    banner_content = []
    banner_content.append(Paragraph(title_text, styles["title"]))
    if subtitle_text:
        banner_content.append(Paragraph(subtitle_text, styles["passage"]))
    if meta_parts:
        banner_content.append(Spacer(1, 4))
        banner_content.append(Paragraph("  |  ".join(meta_parts), styles["meta"]))

    banner = Table([[banner_content]], colWidths=[CONTENT_WIDTH])
    banner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("LEFTPADDING", (0, 0), (-1, -1), 24),
        ("RIGHTPADDING", (0, 0), (-1, -1), 24),
        ("TOPPADDING", (0, 0), (-1, -1), 24),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 20),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(banner)
    story.append(HRFlowable(width="100%", thickness=3, color=GOLD, spaceBefore=0, spaceAfter=24))
```

**`add_reachright_footer(story, styles)`** - Copied exactly from sermon-research.

**`make_page_footer(brand="reachright")`** - Returns a canvas callback function. When `brand="reachright"`: gold rule + "Powered by REACHRIGHT" left + page number right. When `brand="church"`: thin gray rule + page number right only.
```python
def make_page_footer(brand="reachright"):
    def _footer(canvas_obj, doc):
        canvas_obj.saveState()
        page_width = letter[0]
        margin = 1.0 * inch

        if brand == "reachright":
            canvas_obj.setStrokeColor(GOLD)
            canvas_obj.setLineWidth(0.5)
            canvas_obj.line(margin, 0.6 * inch, page_width - margin, 0.6 * inch)
            canvas_obj.setFont("Helvetica", 7)
            canvas_obj.setFillColor(MED_GRAY)
            canvas_obj.drawString(margin, 0.42 * inch, "Powered by REACHRIGHT")
        else:
            canvas_obj.setStrokeColor(RULE_GRAY)
            canvas_obj.setLineWidth(0.5)
            canvas_obj.line(margin, 0.6 * inch, page_width - margin, 0.6 * inch)

        canvas_obj.setFont("Helvetica", 7)
        canvas_obj.setFillColor(MED_GRAY)
        page_num = canvas_obj.getPageNumber()
        canvas_obj.drawRightString(page_width - margin, 0.42 * inch, f"Page {page_num}")
        canvas_obj.restoreState()
    return _footer
```

**`create_doc(output_path, title="", author="")`** - Creates and returns a SimpleDocTemplate with standard settings.
```python
def create_doc(output_path, title="", author=""):
    return SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=1.0 * inch,
        rightMargin=1.0 * inch,
        topMargin=0.85 * inch,
        bottomMargin=0.85 * inch,
        title=title,
        author=author,
    )
```

The module's imports at the top:
```python
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
```

- [ ] **Step 2: Verify the module imports cleanly**

Run:
```bash
cd pastor-ai-skills && python -c "import sys; sys.path.insert(0, 'shared'); from pdf_utils import build_styles, create_doc, section_header, add_section, add_bullet_list, add_table, add_shaded_box, add_title_banner, add_reachright_footer, make_page_footer; print('All imports OK')"
```
Expected: `All imports OK`

- [ ] **Step 3: Commit**

```bash
git add shared/pdf_utils.py
git commit -m "feat: add shared PDF utility library for all skill generators"
```

---

## Task 2: Refactor sermon-research to use shared library

**Files:**
- Modify: `sermon-prep/sermon-research/generate-pdf.py`

- [ ] **Step 1: Refactor generate-pdf.py**

Replace all inline color constants, `build_styles()`, `section_header()`, `add_section()`, `add_title_banner()`, `add_reachright_footer()`, `add_page_footer()`, and `create_doc` setup with imports from `shared/pdf_utils.py`.

Keep these functions local (they are sermon-research-specific):
- `add_word_studies(story, word_studies, styles)` - unchanged
- `add_cross_references(story, cross_refs, styles)` - unchanged
- `add_theological_themes(story, themes, styles)` - unchanged
- `add_thinking_prompts(story, prompts, styles)` - refactored to use `add_shaded_box` from shared

The refactored file structure:
```python
#!/usr/bin/env python3
"""Sermon Research PDF Generator"""

import json
import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, "..", "..", "shared"))

from pdf_utils import (
    NAVY, GOLD, GOLD_LIGHT, BODY_COLOR, SLATE, MED_GRAY, LIGHT_BG, RULE_GRAY, WHITE,
    CONTENT_WIDTH, build_styles, section_header, add_section, add_title_banner,
    add_reachright_footer, make_page_footer, create_doc, add_shaded_box,
)
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch

# --- Sermon-specific layout functions ---
# add_word_studies, add_cross_references, add_theological_themes, add_thinking_prompts
# (keep existing implementations, but add_thinking_prompts uses add_shaded_box)

def generate_pdf(json_path, output_path=None):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not output_path:
        passage = data.get("passage", "research")
        safe_name = passage.replace(":", "-").replace(" ", "-")
        output_path = f"Sermon-Research-{safe_name}.pdf"

    doc = create_doc(output_path, title=f"Sermon Research: {data.get('passage', '')}", author=data.get("pastor_name", ""))
    styles = build_styles()
    story = []

    # Title banner
    meta_parts = [p for p in [data.get("date"), data.get("pastor_name"), data.get("church_name")] if p]
    add_title_banner(story, "SERMON RESEARCH", data.get("passage", ""), meta_parts, styles)

    # Sections (same logic as before)
    if data.get("passage_context"):
        add_section(story, "Passage Context", data["passage_context"], styles)
    if data.get("historical_background"):
        add_section(story, "Historical and Cultural Background", data["historical_background"], styles)
    if data.get("word_studies"):
        add_word_studies(story, data["word_studies"], styles)
    if data.get("commentary_insights"):
        add_section(story, "Commentary Insights", data["commentary_insights"], styles)
    if data.get("cross_references"):
        add_cross_references(story, data["cross_references"], styles)
    if data.get("theological_themes"):
        add_theological_themes(story, data["theological_themes"], styles)
    if data.get("thinking_prompts"):
        add_thinking_prompts(story, data["thinking_prompts"], styles)

    add_reachright_footer(story, styles)
    page_footer = make_page_footer("reachright")
    doc.build(story, onFirstPage=page_footer, onLaterPages=page_footer)
    return os.path.abspath(output_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate-pdf.py <input.json> [output.pdf]")
        sys.exit(1)
    json_input = sys.argv[1]
    pdf_output = sys.argv[2] if len(sys.argv) > 2 else None
    result_path = generate_pdf(json_input, pdf_output)
    print(f"PDF generated: {result_path}")
```

- [ ] **Step 2: Verify with a test JSON file**

Create a minimal test JSON file, run the generator, verify PDF output is produced, then delete both files.

```bash
cd pastor-ai-skills
python -c "
import json
data = {
    'passage': 'Test-Verification',
    'date': '2026-04-08',
    'pastor_name': 'Test Pastor',
    'church_name': 'Test Church',
    'passage_context': 'This is a test paragraph.\n\nThis is a second paragraph.',
    'word_studies': [{'english': 'grace', 'transliteration': 'charis', 'literal_meaning': 'gift', 'range_of_meaning': 'Wide usage', 'translations': {'NIV': 'grace', 'ESV': 'grace'}}],
    'thinking_prompts': ['Test prompt one?', 'Test prompt two?']
}
with open('_test.json', 'w') as f:
    json.dump(data, f)
"
python sermon-prep/sermon-research/generate-pdf.py _test.json _test_output.pdf
ls -la _test_output.pdf
rm _test.json _test_output.pdf
```

Expected: PDF file created successfully, then cleaned up.

- [ ] **Step 3: Commit**

```bash
git add sermon-prep/sermon-research/generate-pdf.py
git commit -m "refactor: sermon-research generator imports from shared pdf_utils"
```

---

## Task 3: Build sermon-series generator and update SKILL.md

**Files:**
- Create: `sermon-prep/sermon-series/generate-pdf.py`
- Modify: `sermon-prep/sermon-series/SKILL.md`

- [ ] **Step 1: Create generate-pdf.py for sermon-series**

The generator reads a JSON file and produces a PDF with these sections:
1. Title banner: "SERMON SERIES" with series title as subtitle, meta line with date/pastor/church
2. Scope Assessment: text section
3. Series Title Options: table with Title and Tagline columns (3 rows)
4. Weekly Breakdown: table with Week, Sermon Title, Scripture, Big Idea, Connective Thread columns
5. Series Arc: text section
6. Practical Notes: three subsections using body_label + body_content pattern (Duration Check, Special Attention, Launch Recommendation)
7. REACHRIGHT footer

```python
#!/usr/bin/env python3
"""Sermon Series PDF Generator"""

import json
import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, "..", "..", "shared"))

from pdf_utils import (
    NAVY, GOLD, BODY_COLOR, CONTENT_WIDTH,
    build_styles, section_header, add_section, add_title_banner,
    add_reachright_footer, make_page_footer, create_doc, add_table,
)
from reportlab.platypus import Paragraph, Spacer, HRFlowable
from reportlab.lib.units import inch


def add_practical_notes(story, notes, styles):
    section_header(story, "Practical Notes", styles)

    if notes.get("duration_check"):
        story.append(Paragraph("DURATION CHECK", styles["body_label"]))
        story.append(Paragraph(notes["duration_check"], styles["body_content"]))

    if notes.get("special_attention"):
        story.append(Paragraph("WEEKS NEEDING SPECIAL ATTENTION", styles["body_label"]))
        story.append(Paragraph(notes["special_attention"], styles["body_content"]))

    if notes.get("launch_recommendation"):
        story.append(Paragraph("SERIES LAUNCH RECOMMENDATION", styles["body_label"]))
        story.append(Paragraph(notes["launch_recommendation"], styles["body_content"]))


def generate_pdf(json_path, output_path=None):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not output_path:
        title = data.get("series_title", "series")
        safe_name = title.replace(" ", "-").replace(":", "-")
        output_path = f"Sermon-Series-{safe_name}.pdf"

    doc = create_doc(
        output_path,
        title=f"Sermon Series: {data.get('series_title', '')}",
        author=data.get("pastor_name", ""),
    )
    styles = build_styles()
    story = []

    # Title banner
    meta_parts = [p for p in [data.get("date"), data.get("pastor_name"), data.get("church_name")] if p]
    subtitle = data.get("series_title", "")
    if data.get("series_tagline"):
        subtitle += f" -- {data['series_tagline']}"
    add_title_banner(story, "SERMON SERIES", subtitle, meta_parts, styles)

    # Scope assessment
    if data.get("scope_assessment"):
        add_section(story, "Scope Assessment", data["scope_assessment"], styles)

    # Title options table
    if data.get("title_options"):
        section_header(story, "Series Title Options", styles)
        headers = ["Title", "Tagline"]
        rows = [[opt.get("title", ""), opt.get("tagline", "")] for opt in data["title_options"]]
        add_table(story, headers, rows, [2.0, 4.5], styles)

    # Weekly breakdown table
    if data.get("weekly_breakdown"):
        section_header(story, "Weekly Breakdown", styles)
        headers = ["Week", "Sermon Title", "Scripture", "Big Idea", "Connective Thread"]
        rows = []
        for week in data["weekly_breakdown"]:
            rows.append([
                str(week.get("week", "")),
                week.get("sermon_title", ""),
                week.get("passage", ""),
                week.get("big_idea", ""),
                week.get("connective_thread", ""),
            ])
        add_table(story, headers, rows, [0.5, 1.2, 1.0, 1.8, 2.0], styles)

    # Series arc
    if data.get("series_arc"):
        add_section(story, "Series Arc", data["series_arc"], styles)

    # Practical notes
    if data.get("practical_notes"):
        add_practical_notes(story, data["practical_notes"], styles)

    add_reachright_footer(story, styles)
    page_footer = make_page_footer("reachright")
    doc.build(story, onFirstPage=page_footer, onLaterPages=page_footer)
    return os.path.abspath(output_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate-pdf.py <input.json> [output.pdf]")
        sys.exit(1)
    json_input = sys.argv[1]
    pdf_output = sys.argv[2] if len(sys.argv) > 2 else None
    result_path = generate_pdf(json_input, pdf_output)
    print(f"PDF generated: {result_path}")
```

- [ ] **Step 2: Verify with test JSON**

```bash
cd pastor-ai-skills
python -c "
import json
data = {
    'series_title': 'Hold Fast',
    'series_tagline': 'Staying grounded when everything shifts',
    'date': '2026-04-08',
    'pastor_name': 'Test Pastor',
    'church_name': 'Test Church',
    'scope_assessment': 'Four weeks through Hebrews 10-12. Good fit for the length.',
    'title_options': [
        {'title': 'Hold Fast', 'tagline': 'Staying grounded when everything shifts'},
        {'title': 'Unshaken', 'tagline': 'Faith that holds when life does not'},
        {'title': 'Anchor Down', 'tagline': 'Finding your footing in uncertain times'}
    ],
    'weekly_breakdown': [
        {'week': 1, 'sermon_title': 'The Confidence You Already Have', 'passage': 'Hebrews 10:19-25', 'big_idea': 'You have access to God that nothing can revoke.', 'connective_thread': 'Establishes the premise: we hold fast because of what Christ already did.'},
        {'week': 2, 'sermon_title': 'When Endurance Gets Heavy', 'passage': 'Hebrews 10:32-39', 'big_idea': 'The hardest part of faith is the middle.', 'connective_thread': 'Moves from confidence to the cost of maintaining it.'}
    ],
    'series_arc': 'The series opens with assurance and moves into the cost of endurance, then lands on the heroes who went before us as proof that holding fast is possible.',
    'practical_notes': {
        'duration_check': 'Four weeks is the right length for this material.',
        'special_attention': 'Week 2 deals with suffering. May need pastoral sensitivity.',
        'launch_recommendation': 'Cold open. The title and topic are strong enough to hook without a teaser week.'
    }
}
with open('_test.json', 'w') as f:
    json.dump(data, f)
"
python sermon-prep/sermon-series/generate-pdf.py _test.json _test_output.pdf
ls -la _test_output.pdf
rm _test.json _test_output.pdf
```

Expected: PDF generated successfully.

- [ ] **Step 3: Update SKILL.md with Output Format section**

Replace the current ending of `sermon-prep/sermon-series/SKILL.md` (after the "How to Use This" section) by appending an Output Format section. The section follows the same pattern as sermon-research: states output is PDF, lists the reportlab requirement, gives the 5-step generation process, and includes the full JSON schema.

JSON schema for sermon-series:
```json
{
  "series_title": "Hold Fast",
  "series_tagline": "Staying grounded when everything shifts",
  "passage_or_theme": "Hebrews 10-12",
  "num_weeks": 4,
  "date": "2026-04-08",
  "pastor_name": "PASTOR_NAME from foundation",
  "church_name": "CHURCH_NAME from foundation",
  "scope_assessment": "Full text of the scope assessment paragraph.",
  "title_options": [
    {
      "title": "Hold Fast",
      "tagline": "Staying grounded when everything shifts"
    }
  ],
  "weekly_breakdown": [
    {
      "week": 1,
      "sermon_title": "The Confidence You Already Have",
      "passage": "Hebrews 10:19-25",
      "big_idea": "You have access to God that nothing can revoke.",
      "connective_thread": "Establishes the premise: we hold fast because of what Christ already did."
    }
  ],
  "series_arc": "Full text of the series arc summary.",
  "practical_notes": {
    "duration_check": "Full text of the duration check.",
    "special_attention": "Full text of the special attention notes.",
    "launch_recommendation": "Full text of the launch recommendation."
  }
}
```

Important notes to include in SKILL.md:
- `title_options` is an array of exactly 3 objects.
- `weekly_breakdown` is an array with one object per week.
- `practical_notes` is an object with three string fields.
- Use the pastor's real name and church name from foundation variables, not placeholders.
- Do not use em dashes anywhere in the content.

- [ ] **Step 4: Commit**

```bash
git add sermon-prep/sermon-series/generate-pdf.py sermon-prep/sermon-series/SKILL.md
git commit -m "feat: sermon-series outputs formatted PDF with REACHRIGHT branding"
```

---

## Task 4: Build sermon-brainstorm generator and update SKILL.md

**Files:**
- Create: `sermon-prep/sermon-brainstorm/generate-pdf.py`
- Modify: `sermon-prep/sermon-brainstorm/SKILL.md`

- [ ] **Step 1: Create generate-pdf.py for sermon-brainstorm**

The generator produces a short (1-2 page) PDF of the sermon brief. Layout:
1. Title banner: "SERMON BRIEF" with passage as subtitle
2. Each brief field rendered as a gold label + body content pair (using body_label and body_content styles): Big Idea, Key Tension, Audience Need, Desired Response, The Turn
3. Supporting Passages as a bullet list
4. Illustration Idea as a labeled section
5. Closing italic line in a shaded box
6. REACHRIGHT footer

```python
#!/usr/bin/env python3
"""Sermon Brief PDF Generator"""

import json
import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, "..", "..", "shared"))

from pdf_utils import (
    build_styles, section_header, add_title_banner,
    add_reachright_footer, make_page_footer, create_doc,
    add_bullet_list, add_shaded_box,
)
from reportlab.platypus import Paragraph, Spacer


def add_brief_field(story, label, content, styles):
    if not content:
        return
    story.append(Paragraph(label.upper(), styles["body_label"]))
    story.append(Paragraph(content, styles["body_content"]))


def generate_pdf(json_path, output_path=None):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not output_path:
        passage = data.get("passage", "brief")
        safe_name = passage.replace(":", "-").replace(" ", "-")
        output_path = f"Sermon-Brief-{safe_name}.pdf"

    doc = create_doc(
        output_path,
        title=f"Sermon Brief: {data.get('passage', '')}",
        author=data.get("pastor_name", ""),
    )
    styles = build_styles()
    story = []

    # Title banner
    meta_parts = []
    if data.get("series"):
        meta_parts.append(data["series"])
    if data.get("date"):
        meta_parts.append(data["date"])
    if data.get("pastor_name"):
        meta_parts.append(data["pastor_name"])
    if data.get("church_name"):
        meta_parts.append(data["church_name"])
    add_title_banner(story, "SERMON BRIEF", data.get("passage", ""), meta_parts, styles)

    # Brief fields
    add_brief_field(story, "Big Idea", data.get("big_idea"), styles)
    add_brief_field(story, "Key Tension", data.get("key_tension"), styles)
    add_brief_field(story, "Audience Need", data.get("audience_need"), styles)
    add_brief_field(story, "Desired Response", data.get("desired_response"), styles)
    add_brief_field(story, "The Turn", data.get("the_turn"), styles)

    # Supporting passages
    if data.get("supporting_passages"):
        section_header(story, "Supporting Passages", styles)
        items = []
        for sp in data["supporting_passages"]:
            ref = sp.get("reference", "")
            note = sp.get("note", "")
            items.append(f"<b>{ref}</b>: {note}" if note else f"<b>{ref}</b>")
        add_bullet_list(story, items, styles)

    # Illustration idea
    add_brief_field(story, "One Image or Illustration Idea", data.get("illustration_idea"), styles)

    # Closing line in shaded box
    story.append(Spacer(1, 16))
    closing = [Paragraph(
        "<i>This brief is a launchpad, not a script. Take it to prayer and make it yours.</i>",
        styles["prompt"]
    )]
    add_shaded_box(story, closing, styles)

    add_reachright_footer(story, styles)
    page_footer = make_page_footer("reachright")
    doc.build(story, onFirstPage=page_footer, onLaterPages=page_footer)
    return os.path.abspath(output_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate-pdf.py <input.json> [output.pdf]")
        sys.exit(1)
    json_input = sys.argv[1]
    pdf_output = sys.argv[2] if len(sys.argv) > 2 else None
    result_path = generate_pdf(json_input, pdf_output)
    print(f"PDF generated: {result_path}")
```

- [ ] **Step 2: Verify with test JSON**

```bash
cd pastor-ai-skills
python -c "
import json
data = {
    'passage': 'John 11:1-44',
    'series': 'Life and Death',
    'date': '2026-04-13',
    'pastor_name': 'Test Pastor',
    'church_name': 'Test Church',
    'big_idea': 'Jesus delays not because he is indifferent, but because he is after something bigger than comfort.',
    'key_tension': 'The God who could have prevented suffering chose not to, and that choice was love.',
    'audience_need': 'People in the room are carrying grief and wondering where God is in it.',
    'desired_response': 'Trust that God is present in the delay, not absent from it.',
    'the_turn': 'The moment shifts from Mary and Martha questioning Jesus to Jesus weeping with them.',
    'supporting_passages': [
        {'reference': 'Psalm 13:1-2', 'note': 'The cry of how long, a parallel to Martha and Mary.'},
        {'reference': 'Romans 8:28', 'note': 'God working all things, even delay, for good.'}
    ],
    'illustration_idea': 'A surgeon who makes you wait for a surgery date because the timing matters more than speed.'
}
with open('_test.json', 'w') as f:
    json.dump(data, f)
"
python sermon-prep/sermon-brainstorm/generate-pdf.py _test.json _test_output.pdf
ls -la _test_output.pdf
rm _test.json _test_output.pdf
```

Expected: PDF generated successfully.

- [ ] **Step 3: Update SKILL.md with Output Format section**

Append an Output Format section after the "Why This Works" section at the end of `sermon-prep/sermon-brainstorm/SKILL.md`. The section explains that the brief is output as a PDF after the brainstorm conversation concludes. Include the JSON schema:

```json
{
  "passage": "John 11:1-44",
  "series": "Life and Death",
  "date": "2026-04-13",
  "pastor_name": "PASTOR_NAME from foundation",
  "church_name": "CHURCH_NAME from foundation",
  "big_idea": "Jesus delays not because he is indifferent, but because he is after something bigger than comfort.",
  "key_tension": "The God who could have prevented suffering chose not to, and that choice was love.",
  "audience_need": "People in the room are carrying grief and wondering where God is in it.",
  "desired_response": "Trust that God is present in the delay, not absent from it.",
  "the_turn": "The moment shifts from Mary and Martha questioning Jesus to Jesus weeping with them.",
  "supporting_passages": [
    {
      "reference": "Psalm 13:1-2",
      "note": "The cry of how long, a parallel to Martha and Mary."
    }
  ],
  "illustration_idea": "A surgeon who makes you wait because timing matters more than speed."
}
```

Important notes:
- This skill is interactive. The PDF is generated only after the brainstorm conversation produces the brief.
- `series` is optional (only if part of a series).
- `supporting_passages` is an array of 2-3 objects.
- All other fields are single strings.
- Do not use em dashes.

- [ ] **Step 4: Commit**

```bash
git add sermon-prep/sermon-brainstorm/generate-pdf.py sermon-prep/sermon-brainstorm/SKILL.md
git commit -m "feat: sermon-brainstorm outputs brief as formatted PDF"
```

---

## Task 5: Build small-group-questions generator and update SKILL.md

**Files:**
- Create: `sermon-repurposing/small-group-questions/generate-pdf.py`
- Modify: `sermon-repurposing/small-group-questions/SKILL.md`

- [ ] **Step 1: Create generate-pdf.py for small-group-questions**

Layout:
1. Title banner: "SMALL GROUP DISCUSSION GUIDE" with passage as subtitle, date/pastor/church as meta
2. Big Idea in a shaded box
3. Icebreaker section with two bullet options
4. "Read the Passage Together" note
5. Observation Questions: numbered
6. Interpretation Questions: numbered, continuing count
7. Application Questions: numbered, continuing count
8. Going Deeper: numbered, continuing count
9. Closing: prayer prompt in shaded box, optional challenge as body text
10. REACHRIGHT footer

```python
#!/usr/bin/env python3
"""Small Group Discussion Guide PDF Generator"""

import json
import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, "..", "..", "shared"))

from pdf_utils import (
    NAVY, GOLD, SLATE,
    build_styles, section_header, add_title_banner,
    add_reachright_footer, make_page_footer, create_doc,
    add_shaded_box, add_bullet_list,
)
from reportlab.platypus import Paragraph, Spacer


def add_numbered_questions(story, questions, styles, start_num=1):
    for i, q in enumerate(questions, start_num):
        story.append(Paragraph(f"<b>{i}.</b>  {q}", styles["body"]))
    return start_num + len(questions)


def generate_pdf(json_path, output_path=None):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not output_path:
        passage = data.get("passage", "guide")
        safe_name = passage.replace(":", "-").replace(" ", "-")
        output_path = f"Small-Group-Guide-{safe_name}.pdf"

    doc = create_doc(
        output_path,
        title=f"Small Group Guide: {data.get('passage', '')}",
        author=data.get("pastor_name", ""),
    )
    styles = build_styles()
    story = []

    # Title banner
    meta_parts = [p for p in [data.get("date"), data.get("pastor_name"), data.get("church_name")] if p]
    add_title_banner(story, "SMALL GROUP DISCUSSION GUIDE", data.get("passage", ""), meta_parts, styles)

    # Big Idea callout
    if data.get("big_idea"):
        section_header(story, "Big Idea", styles)
        big_idea_elements = [Paragraph(f"<b>{data['big_idea']}</b>", styles["body_content"])]
        add_shaded_box(story, big_idea_elements, styles)
        story.append(Spacer(1, 12))

    # Icebreaker
    if data.get("icebreakers"):
        section_header(story, "Icebreaker (leader picks one)", styles)
        add_bullet_list(story, data["icebreakers"], styles)

    # Read the Passage
    translation = data.get("translation", "NIV")
    section_header(story, "Read the Passage Together", styles)
    story.append(Paragraph(f"{data.get('passage', '')} ({translation})", styles["body"]))

    # Questions with continuous numbering
    num = 1

    if data.get("observation_questions"):
        section_header(story, "Observation Questions", styles)
        num = add_numbered_questions(story, data["observation_questions"], styles, num)

    if data.get("interpretation_questions"):
        section_header(story, "Interpretation Questions", styles)
        num = add_numbered_questions(story, data["interpretation_questions"], styles, num)

    if data.get("application_questions"):
        section_header(story, "Application Questions", styles)
        num = add_numbered_questions(story, data["application_questions"], styles, num)

    if data.get("going_deeper_questions"):
        section_header(story, "Going Deeper", styles)
        num = add_numbered_questions(story, data["going_deeper_questions"], styles, num)

    # Closing
    section_header(story, "Closing", styles)
    if data.get("prayer_prompt"):
        story.append(Paragraph("PRAYER PROMPT", styles["body_label"]))
        prayer_elements = [Paragraph(data["prayer_prompt"], styles["prompt"])]
        add_shaded_box(story, prayer_elements, styles)
        story.append(Spacer(1, 8))

    if data.get("optional_challenge"):
        story.append(Paragraph("OPTIONAL CHALLENGE", styles["body_label"]))
        story.append(Paragraph(data["optional_challenge"], styles["body_content"]))

    add_reachright_footer(story, styles)
    page_footer = make_page_footer("reachright")
    doc.build(story, onFirstPage=page_footer, onLaterPages=page_footer)
    return os.path.abspath(output_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate-pdf.py <input.json> [output.pdf]")
        sys.exit(1)
    json_input = sys.argv[1]
    pdf_output = sys.argv[2] if len(sys.argv) > 2 else None
    result_path = generate_pdf(json_input, pdf_output)
    print(f"PDF generated: {result_path}")
```

- [ ] **Step 2: Verify with test JSON**

```bash
cd pastor-ai-skills
python -c "
import json
data = {
    'passage': 'Romans 8:1-11',
    'date': 'April 13, 2026',
    'translation': 'ESV',
    'pastor_name': 'Test Pastor',
    'church_name': 'Test Church',
    'big_idea': 'There is no condemnation for those in Christ because the Spirit has set us free from the law of sin and death.',
    'icebreakers': ['What is one thing you do to reset when life feels overwhelming?', 'When was the last time you felt completely free from guilt about something?'],
    'observation_questions': ['What does Paul say has happened to those who are in Christ Jesus?', 'What two laws does Paul contrast in verses 2-4?'],
    'interpretation_questions': ['Why does Paul distinguish between the flesh and the Spirit?', 'What does it mean to have the mind set on the Spirit?', 'How does verse 11 connect to the resurrection?'],
    'application_questions': ['Where in your daily life do you still live as though you are condemned?', 'What would change if you truly believed verse 1 applied to your worst moment?', 'How does this passage speak to a relationship where you are withholding forgiveness?'],
    'going_deeper_questions': ['How does Galatians 5:16-25 expand on the flesh versus Spirit contrast here?', 'What does this passage reveal about how God initiates freedom rather than waiting for us to earn it?'],
    'prayer_prompt': 'Spend a few minutes praying about the specific area where you still carry condemnation. Ask God to replace that weight with the truth of Romans 8:1.',
    'optional_challenge': 'This week, identify one moment each day where guilt shows up. When it does, read Romans 8:1 out loud. Not as a mantra, but as a reminder of what is already true.'
}
with open('_test.json', 'w') as f:
    json.dump(data, f)
"
python sermon-repurposing/small-group-questions/generate-pdf.py _test.json _test_output.pdf
ls -la _test_output.pdf
rm _test.json _test_output.pdf
```

Expected: PDF generated successfully.

- [ ] **Step 3: Update SKILL.md with Output Format section**

Append the Output Format section after the "Output Quality Check" section at the end of `sermon-repurposing/small-group-questions/SKILL.md`. Include the JSON schema:

```json
{
  "passage": "Romans 8:1-11",
  "date": "April 13, 2026",
  "translation": "ESV",
  "pastor_name": "PASTOR_NAME from foundation",
  "church_name": "CHURCH_NAME from foundation",
  "big_idea": "One sentence distilled from the sermon.",
  "icebreakers": [
    "Icebreaker option A",
    "Icebreaker option B"
  ],
  "observation_questions": [
    "Question 1",
    "Question 2"
  ],
  "interpretation_questions": [
    "Question 3",
    "Question 4",
    "Question 5"
  ],
  "application_questions": [
    "Question 6",
    "Question 7",
    "Question 8"
  ],
  "going_deeper_questions": [
    "Question 9",
    "Question 10"
  ],
  "prayer_prompt": "Specific prayer direction tied to the sermon theme.",
  "optional_challenge": "One concrete action step for the week."
}
```

Important notes:
- `icebreakers` always has exactly 2 entries.
- Question arrays match the counts in the skill's design rules: 2 observation, 3 interpretation, 3 application, 2 going deeper.
- Total question count should be 10 or fewer.
- Do not use em dashes.

- [ ] **Step 4: Commit**

```bash
git add sermon-repurposing/small-group-questions/generate-pdf.py sermon-repurposing/small-group-questions/SKILL.md
git commit -m "feat: small-group-questions outputs formatted PDF with REACHRIGHT branding"
```

---

## Task 6: Build meeting-agenda generator and update SKILL.md

**Files:**
- Create: `pastoral-rhythm/meeting-agenda/generate-pdf.py`
- Modify: `pastoral-rhythm/meeting-agenda/SKILL.md`

- [ ] **Step 1: Create generate-pdf.py for meeting-agenda**

Layout:
1. Title banner: "[MEETING TYPE] AGENDA" with date/time/location as meta
2. Time check bar: "X minutes allocated / Y minutes available"
3. Opening section
4. Each agenda item as a structured block with time, purpose tag, lead, context, discussion question, decision info
5. Action Items section as bullet list
6. Closing section
7. Parking lot section
8. REACHRIGHT footer

```python
#!/usr/bin/env python3
"""Meeting Agenda PDF Generator"""

import json
import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, "..", "..", "shared"))

from pdf_utils import (
    NAVY, GOLD, GOLD_LIGHT, SLATE, LIGHT_BG, CONTENT_WIDTH,
    build_styles, section_header, add_title_banner,
    add_reachright_footer, make_page_footer, create_doc,
    add_bullet_list, add_shaded_box,
)
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor


def add_time_check(story, time_check, styles):
    allocated = time_check.get("allocated", "")
    available = time_check.get("available", "")
    text = f"<b>{allocated} minutes allocated</b>  /  {available} minutes available"
    elements = [Paragraph(text, styles["body_content"])]
    add_shaded_box(story, elements, styles)
    story.append(Spacer(1, 16))


def add_agenda_item(story, item, styles):
    # Item header: title with time and purpose tag
    title = item.get("title", "")
    minutes = item.get("minutes", "")
    purpose = item.get("purpose", "")
    lead = item.get("lead", "")

    header_text = f"{title}  <font color=\"#{SLATE.hexval()[2:]}\">[{purpose}]</font>"
    story.append(Paragraph(header_text, styles["body_bold"]))

    meta_line = f"{minutes} min"
    if lead:
        meta_line += f"  |  Lead: {lead}"
    story.append(Paragraph(meta_line, styles["body_label"]))

    story.append(Spacer(1, 4))

    if item.get("context"):
        story.append(Paragraph(item["context"], styles["body_content"]))

    if item.get("discussion_question"):
        story.append(Paragraph("DISCUSSION QUESTION", styles["body_label"]))
        story.append(Paragraph(item["discussion_question"], styles["body_content"]))

    if item.get("decision_needed") and item["decision_needed"].lower() != "no":
        story.append(Paragraph("DECISION NEEDED", styles["body_label"]))
        detail = item.get("decision_detail", "Yes")
        story.append(Paragraph(detail, styles["body_content"]))

    story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#D1CDC4"), spaceBefore=8, spaceAfter=12))


def generate_pdf(json_path, output_path=None):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not output_path:
        date = data.get("date", "agenda")
        safe_name = date.replace("/", "-").replace(" ", "-")
        output_path = f"Meeting-Agenda-{safe_name}.pdf"

    meeting_type = data.get("meeting_type", "Meeting")
    doc = create_doc(
        output_path,
        title=f"{meeting_type} Agenda: {data.get('date', '')}",
        author=data.get("pastor_name", ""),
    )
    styles = build_styles()
    story = []

    # Title banner
    meta_parts = []
    if data.get("date"):
        meta_parts.append(data["date"])
    time_str = ""
    if data.get("start_time"):
        time_str = data["start_time"]
        if data.get("end_time"):
            time_str += f" - {data['end_time']}"
        if data.get("total_minutes"):
            time_str += f" ({data['total_minutes']} min)"
        meta_parts.append(time_str)
    if data.get("location"):
        meta_parts.append(data["location"])

    add_title_banner(story, f"{meeting_type.upper()} AGENDA", "", meta_parts, styles)

    # Time check
    if data.get("time_check"):
        add_time_check(story, data["time_check"], styles)

    # Opening
    if data.get("opening"):
        opening = data["opening"]
        section_header(story, f"Opening ({opening.get('minutes', 5)} min)", styles)
        if opening.get("prayer_note"):
            story.append(Paragraph(opening["prayer_note"], styles["body"]))
        if opening.get("checkin_question"):
            story.append(Paragraph(f"<b>Check-in:</b> {opening['checkin_question']}", styles["body"]))

    # Agenda items
    if data.get("agenda_items"):
        for item in data["agenda_items"]:
            add_agenda_item(story, item, styles)

    # Action items
    if data.get("action_items"):
        section_header(story, "Action Items and Next Steps", styles)
        items = []
        for ai in data["action_items"]:
            action = ai.get("action", "")
            owner = ai.get("owner", "")
            deadline = ai.get("deadline", "")
            parts = [f"<b>{action}</b>"]
            if owner:
                parts.append(f"Owner: {owner}")
            if deadline:
                parts.append(f"By: {deadline}")
            items.append("  |  ".join(parts))
        add_bullet_list(story, items, styles)

    # Closing
    if data.get("closing"):
        closing = data["closing"]
        section_header(story, f"Closing ({closing.get('minutes', 2)} min)", styles)
        if closing.get("note"):
            story.append(Paragraph(closing["note"], styles["body"]))

    # Parking lot
    if data.get("parking_lot"):
        section_header(story, "Parking Lot", styles)
        add_bullet_list(story, data["parking_lot"], styles)

    add_reachright_footer(story, styles)
    page_footer = make_page_footer("reachright")
    doc.build(story, onFirstPage=page_footer, onLaterPages=page_footer)
    return os.path.abspath(output_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate-pdf.py <input.json> [output.pdf]")
        sys.exit(1)
    json_input = sys.argv[1]
    pdf_output = sys.argv[2] if len(sys.argv) > 2 else None
    result_path = generate_pdf(json_input, pdf_output)
    print(f"PDF generated: {result_path}")
```

- [ ] **Step 2: Verify with test JSON**

```bash
cd pastor-ai-skills
python -c "
import json
data = {
    'meeting_type': 'Staff Meeting',
    'date': 'April 14, 2026',
    'start_time': '9:00 AM',
    'end_time': '10:00 AM',
    'total_minutes': 60,
    'location': 'Conference Room B',
    'pastor_name': 'Test Pastor',
    'church_name': 'Test Church',
    'time_check': {'allocated': 60, 'available': 60},
    'opening': {'minutes': 5, 'prayer_note': 'Opening prayer (1-2 minutes)', 'checkin_question': 'What is one win from the past week?'},
    'agenda_items': [
        {'title': 'Easter Debrief', 'minutes': 15, 'purpose': 'Discussion', 'lead': 'Lead Pastor', 'context': 'We had 47 first-time guests and four salvations.', 'discussion_question': 'What worked better than expected, and what would we do differently?', 'decision_needed': 'No'},
        {'title': 'Summer Series Planning', 'minutes': 15, 'purpose': 'Decision', 'lead': 'Teaching Pastor', 'context': 'Need to lock in summer series topic and dates.', 'discussion_question': 'Which proposed concept better fits our congregation right now?', 'decision_needed': 'Yes', 'decision_detail': 'Choose series topic and confirm start date.'}
    ],
    'action_items': [
        {'action': 'Send Q1 budget summary', 'owner': 'Executive Pastor', 'deadline': 'Friday'},
        {'action': 'Return with 3 recruitment ideas', 'owner': 'Children\\'s Director', 'deadline': 'Next meeting'}
    ],
    'closing': {'minutes': 2, 'note': 'Closing prayer'},
    'parking_lot': ['Building project update (deferred to April 21)']
}
with open('_test.json', 'w') as f:
    json.dump(data, f)
"
python pastoral-rhythm/meeting-agenda/generate-pdf.py _test.json _test_output.pdf
ls -la _test_output.pdf
rm _test.json _test_output.pdf
```

Expected: PDF generated successfully.

- [ ] **Step 3: Update SKILL.md with Output Format section**

Append the Output Format section after the "How to Use This Skill" section at the end of `pastoral-rhythm/meeting-agenda/SKILL.md`. Include the JSON schema:

```json
{
  "meeting_type": "Staff Meeting",
  "date": "April 14, 2026",
  "start_time": "9:00 AM",
  "end_time": "10:00 AM",
  "total_minutes": 60,
  "location": "Conference Room B",
  "pastor_name": "PASTOR_NAME from foundation",
  "church_name": "CHURCH_NAME from foundation",
  "time_check": {
    "allocated": 60,
    "available": 60
  },
  "opening": {
    "minutes": 5,
    "prayer_note": "Opening prayer (1-2 minutes)",
    "checkin_question": "What is one win from the past week?"
  },
  "agenda_items": [
    {
      "title": "Easter Debrief",
      "minutes": 15,
      "purpose": "Discussion",
      "lead": "Lead Pastor",
      "context": "We had 47 first-time guests and four salvations.",
      "discussion_question": "What worked better than expected?",
      "decision_needed": "No",
      "decision_detail": ""
    }
  ],
  "action_items": [
    {
      "action": "Send Q1 budget summary",
      "owner": "Executive Pastor",
      "deadline": "Friday"
    }
  ],
  "closing": {
    "minutes": 2,
    "note": "Closing prayer"
  },
  "parking_lot": [
    "Building project update (deferred to April 21)"
  ]
}
```

Important notes:
- `agenda_items` is an array with one object per item. `purpose` is one of: "Update", "Discussion", "Decision".
- `decision_needed` is "Yes" or "No". If "Yes", `decision_detail` states what needs deciding.
- `parking_lot` is an array of strings for items deferred to a future meeting.
- Do not use em dashes.

- [ ] **Step 4: Commit**

```bash
git add pastoral-rhythm/meeting-agenda/generate-pdf.py pastoral-rhythm/meeting-agenda/SKILL.md
git commit -m "feat: meeting-agenda outputs formatted PDF with REACHRIGHT branding"
```

---

## Task 7: Build church-letter generator and update SKILL.md

**Files:**
- Create: `written-communication/church-letter/generate-pdf.py`
- Modify: `written-communication/church-letter/SKILL.md`

- [ ] **Step 1: Create generate-pdf.py for church-letter**

This is a church-branded document. No REACHRIGHT mentions anywhere. Clean, formal letter layout.

Layout:
1. Church name as letterhead (navy, centered, Helvetica-Bold 18pt)
2. Date line (right-aligned)
3. Addressee line
4. Letter body as justified paragraphs
5. Pastor signature block (name, title, church name)
6. Page footer: thin gray rule + page number only (no REACHRIGHT)

The letter should NOT use the navy title banner. It should feel like a formal letter on church stationery, not a product report.

```python
#!/usr/bin/env python3
"""Church Letter PDF Generator"""

import json
import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, "..", "..", "shared"))

from pdf_utils import (
    NAVY, GOLD, BODY_COLOR, MED_GRAY, RULE_GRAY, CONTENT_WIDTH,
    build_styles, make_page_footer, create_doc,
)
from reportlab.platypus import Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_JUSTIFY, TA_LEFT
from reportlab.lib.units import inch


def build_letter_styles(base_styles):
    s = dict(base_styles)
    s["letterhead"] = ParagraphStyle(
        "Letterhead", fontName="Helvetica-Bold", fontSize=18, leading=22,
        textColor=NAVY, alignment=TA_CENTER, spaceAfter=4,
    )
    s["letterhead_rule"] = None  # placeholder, we use HRFlowable
    s["date_line"] = ParagraphStyle(
        "DateLine", fontName="Helvetica", fontSize=10, leading=14,
        textColor=BODY_COLOR, alignment=TA_RIGHT, spaceAfter=20,
    )
    s["addressee"] = ParagraphStyle(
        "Addressee", fontName="Helvetica", fontSize=11, leading=16,
        textColor=BODY_COLOR, spaceAfter=16,
    )
    s["letter_body"] = ParagraphStyle(
        "LetterBody", fontName="Times-Roman", fontSize=11, leading=17,
        textColor=BODY_COLOR, spaceAfter=12, alignment=TA_JUSTIFY,
    )
    s["signature_name"] = ParagraphStyle(
        "SignatureName", fontName="Helvetica-Bold", fontSize=11, leading=16,
        textColor=NAVY, spaceBefore=28,
    )
    s["signature_title"] = ParagraphStyle(
        "SignatureTitle", fontName="Helvetica", fontSize=10, leading=14,
        textColor=BODY_COLOR,
    )
    return s


def generate_pdf(json_path, output_path=None):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not output_path:
        date = data.get("date", "letter")
        topic = data.get("topic", "")
        safe_date = date.replace("/", "-").replace(" ", "-").replace(",", "")
        safe_topic = topic.replace(" ", "-")[:30] if topic else "letter"
        output_path = f"Church-Letter-{safe_date}-{safe_topic}.pdf"

    doc = create_doc(
        output_path,
        title=f"Church Letter: {data.get('date', '')}",
        author=data.get("pastor_name", ""),
    )
    base_styles = build_styles()
    styles = build_letter_styles(base_styles)
    story = []

    # Letterhead
    story.append(Paragraph(data.get("church_name", ""), styles["letterhead"]))
    story.append(HRFlowable(width="40%", thickness=2, color=GOLD, spaceBefore=2, spaceAfter=20))

    # Date
    if data.get("date"):
        story.append(Paragraph(data["date"], styles["date_line"]))

    # Addressee
    if data.get("addressee"):
        story.append(Paragraph(data["addressee"], styles["addressee"]))

    # Body
    body = data.get("body", "")
    for p in body.split("\n\n"):
        p = p.strip()
        if p:
            story.append(Paragraph(p, styles["letter_body"]))

    # Signature
    if data.get("pastor_name"):
        story.append(Paragraph(data["pastor_name"], styles["signature_name"]))
    if data.get("pastor_title"):
        story.append(Paragraph(data["pastor_title"], styles["signature_title"]))
    if data.get("church_name"):
        story.append(Paragraph(data["church_name"], styles["signature_title"]))

    page_footer = make_page_footer("church")
    doc.build(story, onFirstPage=page_footer, onLaterPages=page_footer)
    return os.path.abspath(output_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate-pdf.py <input.json> [output.pdf]")
        sys.exit(1)
    json_input = sys.argv[1]
    pdf_output = sys.argv[2] if len(sys.argv) > 2 else None
    result_path = generate_pdf(json_input, pdf_output)
    print(f"PDF generated: {result_path}")
```

- [ ] **Step 2: Verify with test JSON**

```bash
cd pastor-ai-skills
python -c "
import json
data = {
    'church_name': 'New Hope Hawaii Kai',
    'date': 'April 14, 2026',
    'topic': 'Leadership Transition',
    'addressee': 'Dear New Hope Family,',
    'body': 'This church has meant everything to our family, and that is exactly why I want to write to you directly.\n\nAfter much prayer and conversation with our council, Pastor David Kim will be stepping down as Worship Director effective May 1. This was a mutual decision made with care for David, his family, and our church.\n\nI know this raises questions. That is okay. Here is what I can tell you right now: our worship ministry is not in crisis. We have a strong team in place, and we will announce interim leadership by next Sunday.\n\nIf you have questions or need to talk, my door is open. You can also reach out to any of our elders.\n\nGod is not finished with this church. I am more convinced of that today than I was a year ago.',
    'pastor_name': 'Thomas Costello',
    'pastor_title': 'Executive Pastor',
    'framing_note': 'A pastoral letter communicating a staff departure with grace and clarity.',
    'flags': ['Recommend pastoral follow-up with worship team before sending.']
}
with open('_test.json', 'w') as f:
    json.dump(data, f)
"
python written-communication/church-letter/generate-pdf.py _test.json _test_output.pdf
ls -la _test_output.pdf
rm _test.json _test_output.pdf
```

Expected: PDF generated successfully.

- [ ] **Step 3: Update SKILL.md with Output Format section**

Append the Output Format section after the "Why Getting This Right Matters" section at the end of `written-communication/church-letter/SKILL.md`. Note that this is a church-branded PDF with no REACHRIGHT mentions. Include the JSON schema:

```json
{
  "church_name": "CHURCH_NAME from foundation",
  "date": "April 14, 2026",
  "topic": "Leadership Transition",
  "addressee": "Dear New Hope Family,",
  "body": "Full letter text. Separate paragraphs with double newlines.",
  "pastor_name": "PASTOR_NAME from foundation",
  "pastor_title": "PASTOR_TITLE from foundation",
  "framing_note": "One sentence describing the letter for pastor's reference only.",
  "flags": [
    "Any flags for legal review, pastoral follow-up, etc."
  ]
}
```

Important notes:
- `framing_note` and `flags` are for the pastor's reference only and do not appear in the PDF.
- `body` is a plain text string with `\n\n` for paragraph breaks.
- This is a church-branded document. No REACHRIGHT branding appears in the output.
- Do not use em dashes.

- [ ] **Step 4: Commit**

```bash
git add written-communication/church-letter/generate-pdf.py written-communication/church-letter/SKILL.md
git commit -m "feat: church-letter outputs formatted PDF with church letterhead"
```

---

## Task 8: Build midweek-devotional generator and update SKILL.md

**Files:**
- Create: `pastoral-rhythm/midweek-devotional/generate-pdf.py`
- Modify: `pastoral-rhythm/midweek-devotional/SKILL.md`

- [ ] **Step 1: Create generate-pdf.py for midweek-devotional**

Church-branded. Minimal, warm, single-page layout. Feels like a personal note.

Layout:
1. Church name and date at top in understated type (no navy banner)
2. Opening text
3. Scripture in a shaded callout box (gold left border, cream background)
4. Reflection as body text
5. Takeaway highlighted in bold
6. Closing prayer/benediction in italic
7. Pastor name at bottom
8. Page footer: thin gray rule + page number only

```python
#!/usr/bin/env python3
"""Midweek Devotional PDF Generator"""

import json
import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, "..", "..", "shared"))

from pdf_utils import (
    NAVY, GOLD, BODY_COLOR, SLATE, MED_GRAY,
    build_styles, make_page_footer, create_doc, add_shaded_box,
)
from reportlab.platypus import Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY


def build_devotional_styles(base_styles):
    s = dict(base_styles)
    s["devo_header"] = ParagraphStyle(
        "DevoHeader", fontName="Helvetica", fontSize=10, leading=14,
        textColor=MED_GRAY, alignment=TA_CENTER, spaceAfter=2,
    )
    s["devo_date"] = ParagraphStyle(
        "DevoDate", fontName="Helvetica", fontSize=9, leading=13,
        textColor=MED_GRAY, alignment=TA_CENTER, spaceAfter=20,
    )
    s["devo_body"] = ParagraphStyle(
        "DevoBody", fontName="Times-Roman", fontSize=11.5, leading=18,
        textColor=BODY_COLOR, spaceAfter=12, alignment=TA_JUSTIFY,
    )
    s["devo_scripture"] = ParagraphStyle(
        "DevoScripture", fontName="Times-Italic", fontSize=11, leading=17,
        textColor=BODY_COLOR, spaceAfter=4,
    )
    s["devo_reference"] = ParagraphStyle(
        "DevoReference", fontName="Helvetica-Bold", fontSize=9, leading=13,
        textColor=NAVY, spaceAfter=0,
    )
    s["devo_takeaway"] = ParagraphStyle(
        "DevoTakeaway", fontName="Helvetica-Bold", fontSize=11.5, leading=18,
        textColor=NAVY, spaceAfter=16, alignment=TA_CENTER,
    )
    s["devo_closing"] = ParagraphStyle(
        "DevoClosing", fontName="Times-Italic", fontSize=11, leading=17,
        textColor=SLATE, spaceAfter=12, alignment=TA_JUSTIFY,
    )
    s["devo_signoff"] = ParagraphStyle(
        "DevoSignoff", fontName="Helvetica", fontSize=10, leading=14,
        textColor=BODY_COLOR, spaceBefore=20,
    )
    return s


def generate_pdf(json_path, output_path=None):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not output_path:
        date = data.get("date", "devotional")
        safe_name = date.replace("/", "-").replace(" ", "-").replace(",", "")
        output_path = f"Midweek-Devotional-{safe_name}.pdf"

    doc = create_doc(
        output_path,
        title=f"Midweek Devotional: {data.get('date', '')}",
        author=data.get("pastor_name", ""),
    )
    base_styles = build_styles()
    styles = build_devotional_styles(base_styles)
    story = []

    # Header
    story.append(Paragraph(data.get("church_name", ""), styles["devo_header"]))
    story.append(Paragraph(data.get("date", ""), styles["devo_date"]))
    story.append(HRFlowable(width="30%", thickness=1.5, color=GOLD, spaceBefore=0, spaceAfter=24))

    # Opening
    if data.get("opening"):
        story.append(Paragraph(data["opening"], styles["devo_body"]))

    # Scripture callout
    if data.get("scripture_text"):
        scripture_elements = []
        scripture_elements.append(Paragraph(data["scripture_text"], styles["devo_scripture"]))
        ref_line = data.get("passage_reference", "")
        if data.get("translation"):
            ref_line += f" ({data['translation']})"
        scripture_elements.append(Paragraph(ref_line, styles["devo_reference"]))
        add_shaded_box(story, scripture_elements, styles)
        story.append(Spacer(1, 16))

    # Reflection
    if data.get("reflection"):
        for p in data["reflection"].split("\n\n"):
            p = p.strip()
            if p:
                story.append(Paragraph(p, styles["devo_body"]))

    # Takeaway
    if data.get("takeaway"):
        story.append(Spacer(1, 8))
        story.append(Paragraph(data["takeaway"], styles["devo_takeaway"]))

    # Closing
    if data.get("closing"):
        story.append(Paragraph(data["closing"], styles["devo_closing"]))

    # Pastor name
    if data.get("pastor_name"):
        story.append(Paragraph(data["pastor_name"], styles["devo_signoff"]))

    page_footer = make_page_footer("church")
    doc.build(story, onFirstPage=page_footer, onLaterPages=page_footer)
    return os.path.abspath(output_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate-pdf.py <input.json> [output.pdf]")
        sys.exit(1)
    json_input = sys.argv[1]
    pdf_output = sys.argv[2] if len(sys.argv) > 2 else None
    result_path = generate_pdf(json_input, pdf_output)
    print(f"PDF generated: {result_path}")
```

- [ ] **Step 2: Verify with test JSON**

```bash
cd pastor-ai-skills
python -c "
import json
data = {
    'church_name': 'New Hope Hawaii Kai',
    'date': 'April 16, 2026',
    'pastor_name': 'Thomas Costello',
    'passage_reference': 'Psalm 46:10',
    'translation': 'ESV',
    'scripture_text': 'Be still, and know that I am God. I will be exalted among the nations, I will be exalted in the earth!',
    'opening': 'By Wednesday most of us have already forgotten what we committed to on Sunday. That is not failure. That is being human.',
    'reflection': 'Stillness is not the absence of noise. It is the decision to stop performing long enough to remember who is actually in charge.\n\nMost of us do not struggle with believing God is God. We struggle with acting like it. We fill the silence with plans, worries, and backup strategies because stillness feels like inaction. But the psalmist is not calling us to passivity. He is calling us to trust.',
    'takeaway': 'Today, stop solving for five minutes. Just stop. Let God be God without your help.',
    'closing': 'Father, we are tired of carrying things that were never ours to carry. Teach us to be still. Not because the world has stopped, but because you have not. Amen.'
}
with open('_test.json', 'w') as f:
    json.dump(data, f)
"
python pastoral-rhythm/midweek-devotional/generate-pdf.py _test.json _test_output.pdf
ls -la _test_output.pdf
rm _test.json _test_output.pdf
```

Expected: PDF generated successfully.

- [ ] **Step 3: Update SKILL.md with Output Format section**

Append the Output Format section after the current output section at the end of `pastoral-rhythm/midweek-devotional/SKILL.md`. Replace the existing text-based output description with PDF instructions. Include the JSON schema:

```json
{
  "church_name": "CHURCH_NAME from foundation",
  "date": "April 16, 2026",
  "pastor_name": "PASTOR_NAME from foundation",
  "passage_reference": "Psalm 46:10",
  "translation": "ESV",
  "scripture_text": "Be still, and know that I am God.",
  "opening": "Opening text (1-2 sentences).",
  "reflection": "Reflection text. Separate paragraphs with double newlines.",
  "takeaway": "One sentence the reader carries into the rest of the week.",
  "closing": "Prayer or benediction text."
}
```

Important notes:
- No section headers appear in the final PDF (structural labels are for the skill, not the reader).
- `reflection` is a plain text string with `\n\n` for paragraph breaks.
- All other fields are single strings.
- This is a church-branded document. No REACHRIGHT branding.
- Do not use em dashes.

- [ ] **Step 4: Commit**

```bash
git add pastoral-rhythm/midweek-devotional/generate-pdf.py pastoral-rhythm/midweek-devotional/SKILL.md
git commit -m "feat: midweek-devotional outputs formatted PDF with church branding"
```

---

## Task 9: Build announcement-script generator and update SKILL.md

**Files:**
- Create: `written-communication/announcement-script/generate-pdf.py`
- Modify: `written-communication/announcement-script/SKILL.md`

- [ ] **Step 1: Create generate-pdf.py for announcement-script**

Church-branded. Clean single-page layout. Hand-it-to-the-announcer ready.

Layout:
1. Header: "Sunday Announcements" with date, estimated time, items covered / items submitted
2. Tone/deliverer notes (if provided) in a subtle note style
3. Script body in readable type, with delivery cues [pause], [smile] rendered in italic lighter color
4. Divider
5. "For the Bulletin / Slides / Email" section with bumped items
6. Page footer: thin gray rule + page number only

The script body needs special handling: delivery cues in square brackets should be styled differently from spoken text. Parse the script text and render bracketed cues in italic slate color inline with the body.

```python
#!/usr/bin/env python3
"""Announcement Script PDF Generator"""

import json
import re
import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, "..", "..", "shared"))

from pdf_utils import (
    NAVY, GOLD, BODY_COLOR, SLATE, MED_GRAY, CONTENT_WIDTH,
    build_styles, section_header, make_page_footer, create_doc,
    add_bullet_list,
)
from reportlab.platypus import Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.units import inch


def build_script_styles(base_styles):
    s = dict(base_styles)
    s["script_title"] = ParagraphStyle(
        "ScriptTitle", fontName="Helvetica-Bold", fontSize=18, leading=22,
        textColor=NAVY, alignment=TA_CENTER, spaceAfter=4,
    )
    s["script_meta"] = ParagraphStyle(
        "ScriptMeta", fontName="Helvetica", fontSize=9, leading=13,
        textColor=MED_GRAY, alignment=TA_CENTER, spaceAfter=16,
    )
    s["script_body"] = ParagraphStyle(
        "ScriptBody", fontName="Times-Roman", fontSize=12, leading=19,
        textColor=BODY_COLOR, spaceAfter=10,
    )
    s["script_note"] = ParagraphStyle(
        "ScriptNote", fontName="Helvetica-Oblique", fontSize=9.5, leading=14,
        textColor=SLATE, spaceAfter=16,
    )
    s["bumped_header"] = ParagraphStyle(
        "BumpedHeader", fontName="Helvetica-Bold", fontSize=10, leading=14,
        textColor=NAVY, spaceBefore=16, spaceAfter=8,
    )
    return s


def format_script_text(text):
    """Convert [delivery cues] to italic slate-colored inline markup."""
    slate_hex = SLATE.hexval()[2:] if hasattr(SLATE, 'hexval') else "4A5568"
    def replace_cue(match):
        cue = match.group(1)
        return f'<font color="#{slate_hex}"><i>({cue})</i></font>'
    return re.sub(r'\[([^\]]+)\]', replace_cue, text)


def generate_pdf(json_path, output_path=None):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not output_path:
        date = data.get("date", "script")
        safe_name = date.replace("/", "-").replace(" ", "-").replace(",", "")
        output_path = f"Announcement-Script-{safe_name}.pdf"

    doc = create_doc(
        output_path,
        title=f"Announcement Script: {data.get('date', '')}",
        author="",
    )
    base_styles = build_styles()
    styles = build_script_styles(base_styles)
    story = []

    # Header
    story.append(Paragraph("Sunday Announcements", styles["script_title"]))

    meta_parts = []
    if data.get("date"):
        meta_parts.append(data["date"])
    if data.get("estimated_seconds"):
        meta_parts.append(f"~{data['estimated_seconds']} seconds")
    if data.get("items_covered") and data.get("items_submitted"):
        meta_parts.append(f"{data['items_covered']} of {data['items_submitted']} items")
    if meta_parts:
        story.append(Paragraph("  |  ".join(meta_parts), styles["script_meta"]))

    story.append(HRFlowable(width="100%", thickness=2, color=GOLD, spaceBefore=4, spaceAfter=20))

    # Deliverer / tone notes
    if data.get("deliverer") or data.get("tone_notes"):
        note_parts = []
        if data.get("deliverer"):
            note_parts.append(f"Deliverer: {data['deliverer']}")
        if data.get("tone_notes"):
            note_parts.append(data["tone_notes"])
        story.append(Paragraph("  |  ".join(note_parts), styles["script_note"]))

    # Script body
    if data.get("script_body"):
        formatted = format_script_text(data["script_body"])
        for p in formatted.split("\n\n"):
            p = p.strip()
            if p:
                story.append(Paragraph(p, styles["script_body"]))

    # Bumped items
    if data.get("bumped_items"):
        story.append(HRFlowable(width="100%", thickness=0.5, color=MED_GRAY, spaceBefore=20, spaceAfter=8))
        story.append(Paragraph("For the Bulletin / Slides / Email", styles["bumped_header"]))
        items = []
        for bi in data["bumped_items"]:
            item_name = bi.get("item", "")
            summary = bi.get("summary", "")
            items.append(f"<b>{item_name}:</b> {summary}")
        add_bullet_list(story, items, styles)

    page_footer = make_page_footer("church")
    doc.build(story, onFirstPage=page_footer, onLaterPages=page_footer)
    return os.path.abspath(output_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate-pdf.py <input.json> [output.pdf]")
        sys.exit(1)
    json_input = sys.argv[1]
    pdf_output = sys.argv[2] if len(sys.argv) > 2 else None
    result_path = generate_pdf(json_input, pdf_output)
    print(f"PDF generated: {result_path}")
```

- [ ] **Step 2: Verify with test JSON**

```bash
cd pastor-ai-skills
python -c "
import json
data = {
    'date': 'April 20, 2026',
    'estimated_seconds': 75,
    'items_submitted': 7,
    'items_covered': 3,
    'deliverer': 'Worship Pastor',
    'tone_notes': 'High energy, celebratory. Baptism Sunday.',
    'script_body': 'Before we get to worship, three things you actually want to know about.\n\n[pause, look around the room]\n\nIf you have been thinking about getting baptized, this is your moment. Baptism Sunday is today. After the message, we are heading outside. If you did not sign up, that is fine. Come talk to me or anyone on our team and we will get you ready.\n\n[smile]\n\nAlso, Family Camp registration closes Wednesday. If your family wants a spot, grab your phone right now and register. The link is on the screen. Do not wait until Thursday. You will be mad at yourself.\n\nLast thing: we need four more volunteers for VBS this summer. If you love chaos and small children, see Christina at the welcome table.\n\n[pause]\n\nAlright. Now let us do what we came here to do.',
    'bumped_items': [
        {'item': 'Youth group schedule change', 'summary': 'Friday moved to Saturday this week only. 6pm at the church.'},
        {'item': 'Food pantry', 'summary': 'Collecting canned goods through April 30. Drop-off bins in the lobby.'},
        {'item': 'New sermon series', 'summary': 'Starting next Sunday: \"Hold Fast\" through Hebrews.'},
        {'item': 'Offering moment', 'summary': 'Give online at newhopehk.org/give or text GIVE to 555-1234.'}
    ]
}
with open('_test.json', 'w') as f:
    json.dump(data, f)
"
python written-communication/announcement-script/generate-pdf.py _test.json _test_output.pdf
ls -la _test_output.pdf
rm _test.json _test_output.pdf
```

Expected: PDF generated successfully.

- [ ] **Step 3: Update SKILL.md with Output Format section**

Append the Output Format section after the "Notes for the Deliverer" section at the end of `written-communication/announcement-script/SKILL.md`. Replace the current text-based output format with PDF instructions. Include the JSON schema:

```json
{
  "date": "April 20, 2026",
  "estimated_seconds": 75,
  "items_submitted": 7,
  "items_covered": 3,
  "deliverer": "Worship Pastor",
  "tone_notes": "High energy, celebratory. Baptism Sunday.",
  "script_body": "Full script text. Use [cue] for delivery cues. Separate paragraphs with double newlines.",
  "bumped_items": [
    {
      "item": "Youth group schedule change",
      "summary": "Friday moved to Saturday this week only."
    }
  ]
}
```

Important notes:
- `script_body` is a plain text string. Delivery cues use square brackets: `[pause]`, `[smile]`, `[hold up card]`. These render in italic lighter text in the PDF.
- `bumped_items` is an array of items that did not make the spoken cut, with one-line summaries.
- This is a church-branded document. No REACHRIGHT branding.
- Do not use em dashes.

- [ ] **Step 4: Commit**

```bash
git add written-communication/announcement-script/generate-pdf.py written-communication/announcement-script/SKILL.md
git commit -m "feat: announcement-script outputs formatted PDF with church branding"
```

---

## Final Verification

After all tasks are complete:

- [ ] **Verify all generators import from shared library successfully**

```bash
cd pastor-ai-skills
for f in sermon-prep/sermon-research/generate-pdf.py sermon-prep/sermon-series/generate-pdf.py sermon-prep/sermon-brainstorm/generate-pdf.py sermon-repurposing/small-group-questions/generate-pdf.py pastoral-rhythm/meeting-agenda/generate-pdf.py written-communication/church-letter/generate-pdf.py pastoral-rhythm/midweek-devotional/generate-pdf.py written-communication/announcement-script/generate-pdf.py; do
    echo "Testing: $f"
    python -c "import sys, os; sys.path.insert(0, os.path.join(os.path.dirname('$f'), 'shared')); exec(open('$f').read().split('if __name__')[0])" 2>&1 | head -1
done
```

- [ ] **Verify file structure matches the spec**

```bash
cd pastor-ai-skills
echo "--- shared ---"
ls shared/
echo "--- generators ---"
find . -name "generate-pdf.py" | sort
```

Expected:
```
--- shared ---
pdf_utils.py
--- generators ---
./pastoral-rhythm/meeting-agenda/generate-pdf.py
./pastoral-rhythm/midweek-devotional/generate-pdf.py
./sermon-prep/sermon-brainstorm/generate-pdf.py
./sermon-prep/sermon-research/generate-pdf.py
./sermon-prep/sermon-series/generate-pdf.py
./sermon-repurposing/small-group-questions/generate-pdf.py
./written-communication/announcement-script/generate-pdf.py
./written-communication/church-letter/generate-pdf.py
```
