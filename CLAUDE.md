# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Dependency

PDF-generating skills require `reportlab`:

```bash
pip install reportlab
```

## Running PDF Generators

Each skill with PDF output has a `generate-pdf.py` that takes a JSON file:

```bash
python sermon-prep/sermon-research/generate-pdf.py input.json
python sermon-prep/sermon-research/generate-pdf.py input.json output.pdf
```

All generators follow the same pattern: read JSON → build ReportLab story → write PDF. The output path defaults to a slug derived from the passage or title if not provided.

## Architecture

### Skill System

Each skill is a directory containing:
- `SKILL.md` — AI behavior definition (instructions, output format, JSON schema for PDF)
- `generate-pdf.py` — optional PDF generator, present only when the skill produces a formatted document

Skills are organized by category:

| Category | Directory |
|---|---|
| Sermon prep | `sermon-prep/` |
| Written communication | `written-communication/` |
| Sermon repurposing | `sermon-repurposing/` |
| Social media | `social-media/` |
| Pastoral rhythm | `pastoral-rhythm/` |
| Shared context | `foundation/pastor-foundation/` |

Custom slash commands (this workspace only) live in `.claude/skills/`:

| Command | Description |
|---|---|
| `/sermon-prep` | Full workflow: brainstorm → research → outline, saved to `outlines/` |
| `/childrens-lesson` | ECO Presbyterian children's ministry — produces Sunday and Wednesday lessons from one passage; Wednesday adds a craft |
| `/fpc-brand-guidelines` | FPC Griffin brand identity — apply when creating bulletins, posters, social posts, or any designed piece for First Presbyterian Church of Griffin |

#### `fpc-brand-guidelines` quick reference

Brand Blue: `#195C79`. Full palette and usage ratios in the skill's `SKILL.md`. Fonts: **CMG Sans** (sans-serif, multiple weights) and **Clarendon URW** (serif). Font files live in `assets/fonts/`. Logos in three variants (default, white, light background) in PNG and SVG at `assets/logos/`. Tagline: "Know joy. Know love. Know Jesus." — final clause always visually distinct, never reorder.

#### `childrens-lesson` quick reference

Persona: Reformed Presbyterian children's minister (ECO denomination). Produces both lessons in one response. Lesson order: What We Learn → Worship → Game → Object Lesson → [Craft, Wednesday only] → Teaching → Discussion → Closing Prayer. Theological guardrail: indicative before imperative — every lesson grounds application in what God has done, not what children must achieve.

### PDF Pipeline

Skills that output PDFs follow a two-step process defined in their `SKILL.md`:

1. Claude runs the conversation/generation and assembles structured data
2. Claude writes a temporary JSON file matching the skill's schema, then runs `generate-pdf.py`

### Shared PDF Library (`shared/pdf_utils.py`)

All `generate-pdf.py` scripts import from `shared/pdf_utils.py` via a relative path (`../../shared`). The library provides:

- `build_styles()` — returns a dict of named `ParagraphStyle` objects
- `create_doc(path, title, author)` — returns a configured `SimpleDocTemplate` (letter, 1" side margins, 0.85" top/bottom)
- `add_title_banner(story, title, subtitle, meta_parts, styles)` — navy banner with gold accent rule
- `add_section(story, title, content, styles)` — section header + body paragraphs
- `add_bullet_list(story, items, styles)` — gold-bulleted list
- `add_table(story, headers, rows, col_widths, styles)` — styled table with navy header and alternating rows
- `add_shaded_box(story, elements, styles)` — gold left border + cream background container
- `add_reachright_footer(story, styles)` — REACHRIGHT branding banner at document end
- `make_page_footer(brand)` — canvas callback for page footers; `brand="reachright"` (gold rule + attribution) or `brand="church"` (gray rule + page number only)

### Visual Design

Color palette: deep navy (`#1B2A4A`) + warm gold (`#B8860B`). Editorial study-bible aesthetic. All skills producing church-facing documents (letters, agendas) use `brand="church"` for the footer; skills producing REACHRIGHT-branded research tools use `brand="reachright"`.

### Foundation Layer

`foundation/pastor-foundation/SKILL.md` defines the shared context all task skills build on: church context variables (name, pastor, denomination, attendance, location, translation), theological guardrails, voice/tone rules, and a banned-phrases list. Any new skill should reference this foundation.

### Finished Output

Completed sermon outlines and files go in `outlines/`.
