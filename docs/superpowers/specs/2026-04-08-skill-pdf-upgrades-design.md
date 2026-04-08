# Skill PDF Upgrades Design Spec

**Date:** 2026-04-08
**Status:** Approved

## Problem

Only one skill (sermon-research) outputs a formatted PDF. All other skills dump output as terminal text. This makes it hard to save, print, share, or hand off skill output. The sermon-research PDF upgrade proved the value: better structure, readability, and a professional look.

## Goal

Bring PDF output to 8 skills total. Build a shared Python library so styling is consistent and maintainable across all generators. Use two branding modes: REACHRIGHT-branded for product-facing skills, church-branded (no REACHRIGHT mentions) for church-internal documents.

The 5 remaining skills (sermon-to-blog, sermon-to-youtube, church-social-post, social-media-calendar, church-email) stay as terminal text because their output gets copy/pasted into other platforms.

## Shared PDF Library

### Location

`shared/pdf_utils.py` at the repo root.

### What It Provides

Extracted from the current `sermon-research/generate-pdf.py`:

- **Color palette constants:** NAVY, GOLD, GOLD_LIGHT, BODY_COLOR, SLATE, MED_GRAY, LIGHT_BG, RULE_GRAY, WHITE, CONTENT_WIDTH
- **`build_styles()`** - All paragraph styles: title, passage, meta, section_header, body, body_bold, body_label, body_content, bullet, prompt, table_header, table_cell, table_cell_bold, brand_body, brand_url
- **`section_header(story, title, styles)`** - H2 header with gold accent underline
- **`add_section(story, title, content, styles)`** - Text section with paragraphs split on `\n\n`
- **`add_bullet_list(story, items, styles)`** - Gold-bulleted list items
- **`add_table(story, headers, rows, col_widths, styles)`** - Navy header row, alternating row backgrounds, gold accent line
- **`add_shaded_box(story, elements, styles)`** - Gold left border + cream background container
- **`add_title_banner(story, data, styles, brand)`** - Full-width navy banner. In "reachright" mode: shows "SERMON RESEARCH" (or skill title). In "church" mode: shows church name as the header.
- **`add_reachright_footer(story, styles)`** - REACHRIGHT branding banner at document end. Only called in "reachright" mode.
- **`make_page_footer(brand)`** - Returns a canvas callback function. In "reachright" mode: gold rule + "Powered by REACHRIGHT" + page number. In "church" mode: thin rule + page number only.
- **`create_doc(output_path, title, author)`** - Builds a SimpleDocTemplate with letter size, 1" side margins, 0.85" top/bottom margins.

### Two Branding Modes

- **`brand="reachright"`** - Navy/gold title banner with skill title, REACHRIGHT footer in document body, "Powered by REACHRIGHT" in page footer. Used for: sermon-research, sermon-series, sermon-brainstorm, small-group-questions, meeting-agenda.
- **`brand="church"`** - Same navy/gold visual styling for consistency. Title banner shows church name instead of REACHRIGHT product title. No REACHRIGHT mentions anywhere in the document or page footer. Used for: church-letter, midweek-devotional, announcement-script.

### How Generators Find the Shared Library

Each `generate-pdf.py` adds the shared directory to sys.path relative to its own file:

```python
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, "..", "..", "shared"))
from pdf_utils import (
    build_styles, create_doc, section_header, add_section,
    add_title_banner, add_reachright_footer, make_page_footer, ...
)
```

No pip install of the shared module required.

## Skills Getting PDF Output

### Tier 1: REACHRIGHT-Branded (5 skills)

#### 1. sermon-research (existing, refactor only)

- **Current state:** Fully working PDF with all styling inline in generate-pdf.py (503 lines)
- **Change:** Refactor to import shared utilities. Skill-specific functions (add_word_studies, add_cross_references, add_theological_themes, add_thinking_prompts) stay in the local generate-pdf.py.
- **Filename pattern:** `Sermon-Research-Romans-8-1-11.pdf`
- **SKILL.md:** No changes needed, already has the output format section.

#### 2. sermon-series

- **Filename pattern:** `Sermon-Series-[SeriesTitle].pdf`
- **Layout sections:**
  - Title banner: "SERMON SERIES" with series title as subtitle
  - Scope Assessment: text section (1 paragraph)
  - Series Title Options: 3-row table with Title and Tagline columns
  - Weekly Breakdown: main table with Week, Sermon Title, Scripture Passage, Big Idea, Connective Thread columns
  - Series Arc: text section (2-3 sentences)
  - Practical Notes: text section with subsections (Duration Check, Special Attention Weeks, Launch Recommendation)
  - REACHRIGHT footer
- **JSON schema fields:** series_title, series_tagline, passage_or_theme, num_weeks, date, pastor_name, church_name, scope_assessment, title_options[{title, tagline}], weekly_breakdown[{week, sermon_title, passage, big_idea, connective_thread}], series_arc, practical_notes{duration_check, special_attention, launch_recommendation}

#### 3. sermon-brainstorm

- **Filename pattern:** `Sermon-Brief-[Passage].pdf`
- **Note:** This skill is interactive (a conversation). The PDF is only generated at the end when the brief is produced.
- **Layout sections:**
  - Title banner: "SERMON BRIEF" with passage as subtitle
  - Each brief field as a labeled section with gold label + body content:
    - Big Idea
    - Key Tension
    - Audience Need
    - Desired Response
    - The Turn
    - Supporting Passages (bullet list)
    - One Image or Illustration Idea
  - Closing italic line: "This brief is a launchpad, not a script. Take it to prayer and make it yours."
  - REACHRIGHT footer
- **Expected length:** 1-2 pages. Short, dense, scannable.
- **JSON schema fields:** passage, series, date, pastor_name, church_name, big_idea, key_tension, audience_need, desired_response, the_turn, supporting_passages[{reference, note}], illustration_idea

#### 4. small-group-questions

- **Filename pattern:** `Small-Group-Guide-[Passage].pdf`
- **Layout sections:**
  - Title banner: "SMALL GROUP DISCUSSION GUIDE" with passage as subtitle, week date as meta
  - Big Idea callout: shaded box with the one-sentence big idea
  - Icebreaker section: two options as bullet list
  - "Read the Passage Together" with passage reference
  - Observation Questions: numbered list (2 questions)
  - Interpretation Questions: numbered list continuing (3 questions)
  - Application Questions: numbered list continuing (3 questions)
  - Going Deeper: numbered list continuing (2 questions)
  - Closing section: Prayer prompt in shaded box, optional challenge as body text
- **JSON schema fields:** passage, date, translation, pastor_name, church_name, big_idea, icebreakers[string], observation_questions[string], interpretation_questions[string], application_questions[string], going_deeper_questions[string], prayer_prompt, optional_challenge

#### 5. meeting-agenda

- **Filename pattern:** `Meeting-Agenda-[Date].pdf`
- **Layout sections:**
  - Title banner: "[MEETING TYPE] AGENDA" with date/time/location as meta
  - Time overview bar: total time allocated vs. available
  - Opening section with time block
  - Each agenda item as a structured block: time allocation, purpose tag (Update/Discussion/Decision), lead name, context, discussion question, decision needed
  - Action Items and Next Steps section
  - Closing section
  - Parking lot section (items deferred)
  - REACHRIGHT footer
- **JSON schema fields:** meeting_type, date, start_time, end_time, total_minutes, location, pastor_name, church_name, opening{minutes, prayer_note, checkin_question}, agenda_items[{title, minutes, purpose, lead, context, discussion_question, decision_needed, decision_detail}], action_items[{action, owner, deadline}], closing{minutes, note}, parking_lot[string], time_check{allocated, available}

### Tier 2: Church-Branded (3 skills)

#### 6. church-letter

- **Filename pattern:** `Church-Letter-[Date]-[Topic].pdf`
- **Layout:**
  - Clean letterhead: church name at top, no navy banner (more formal letter feel)
  - Date line
  - Addressee line (e.g., "Dear Grace Family,")
  - Letter body as justified text paragraphs
  - Pastor signature block: name, title, church name
  - No REACHRIGHT branding anywhere
- **JSON schema fields:** church_name, date, addressee, body (full text with \n\n paragraph breaks), pastor_name, pastor_title, framing_note, flags[string]

#### 7. midweek-devotional

- **Filename pattern:** `Midweek-Devotional-[Date].pdf`
- **Layout:**
  - Minimal, warm design. No heavy title banner.
  - Church name and date at top in understated type
  - Opening text (1-2 sentences)
  - Scripture in a styled callout box (gold left border, cream background)
  - Reflection as body text (3-5 sentences)
  - Takeaway highlighted in bold or a small accent box
  - Closing prayer or benediction in italic
  - No section headers visible to the reader (structural labels are for the skill, not the output)
  - No REACHRIGHT branding
- **Expected length:** Single page.
- **JSON schema fields:** church_name, date, pastor_name, passage_reference, translation, scripture_text, opening, reflection, takeaway, closing

#### 8. announcement-script

- **Filename pattern:** `Announcement-Script-[Date].pdf`
- **Layout:**
  - Clean single-page layout
  - Header: "Sunday Announcements" with date, estimated time, items covered count
  - Script body in readable type
  - Delivery cues (pause), (smile) in italic lighter color so they stand out from spoken text
  - Divider
  - "For the Bulletin/Slides/Email" section: bumped items listed with one-line summaries
  - No REACHRIGHT branding
- **Expected length:** Single page.
- **JSON schema fields:** date, estimated_seconds, items_submitted, items_covered, deliverer, tone_notes, script_body (full text with delivery cues marked as [pause], [smile], etc.), bumped_items[{item, summary}]

## Skills NOT Getting PDF (5 skills)

These skills produce output that gets copy/pasted into another platform. PDF would add friction, not value. Their SKILL.md files are already well-structured and need no changes.

- **sermon-to-blog** - Output pastes into WordPress/CMS
- **sermon-to-youtube** - Output pastes into YouTube Studio
- **church-social-post** - Output pastes into social platforms
- **social-media-calendar** - Output is a planning table, used in Asana or similar
- **church-email** - Output pastes into email platform

## Implementation Order

1. Build `shared/pdf_utils.py` (extract from sermon-research)
2. Refactor `sermon-research/generate-pdf.py` to import from shared (verify no regression)
3. Build REACHRIGHT-branded generators: sermon-series, sermon-brainstorm, small-group-questions, meeting-agenda
4. Build church-branded generators: church-letter, midweek-devotional, announcement-script
5. Update each skill's SKILL.md with output format section and JSON schema

## Dependencies

- Python 3
- `reportlab` library (`pip install reportlab`)
- No other external dependencies

## Anti-Patterns

- Do not use em dashes anywhere in generated content
- Do not use placeholder text in JSON schemas (use real foundation variables)
- Do not duplicate shared styling code in per-skill generators
- Do not add REACHRIGHT branding to church-branded documents
