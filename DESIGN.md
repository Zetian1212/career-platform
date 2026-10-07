---
name: Zetian Tao, Career Platform
description: A resume and portfolio set as page one of a sell-side equity research initiation note.
colors:
  report-paper: "oklch(98.6% 0.003 250)"
  key-data-panel: "oklch(95.4% 0.012 255)"
  report-ink: "oklch(21% 0.025 262)"
  secondary-ink: "oklch(43% 0.025 262)"
  hairline: "oklch(86% 0.012 262)"
  control-line: "oklch(58% 0.02 262)"
  research-navy: "oklch(34% 0.085 258)"
  research-navy-deep: "oklch(27% 0.07 260)"
  on-navy: "oklch(97.5% 0.008 258)"
  on-navy-muted: "oklch(84% 0.035 258)"
  focus-blue: "oklch(52% 0.16 255)"
  live-green: "oklch(45% 0.11 155)"
  cached-amber: "oklch(49% 0.12 62)"
  cached-panel: "oklch(95% 0.045 85)"
  error-red: "oklch(48% 0.17 27)"
typography:
  display:
    fontFamily: "Libre Franklin, Franklin Gothic Medium, Helvetica Neue, Arial, sans-serif"
    fontSize: "clamp(2.75rem, 1.4rem + 4.6vw, 5rem)"
    fontWeight: 800
    lineHeight: 0.98
    letterSpacing: "-0.035em"
  headline:
    fontFamily: "Libre Franklin, Franklin Gothic Medium, Helvetica Neue, Arial, sans-serif"
    fontSize: "clamp(2.25rem, 1.5rem + 2.8vw, 3.5rem)"
    fontWeight: 800
    lineHeight: 1
    letterSpacing: "-0.03em"
  discipline:
    fontFamily: "Libre Franklin, Franklin Gothic Medium, Helvetica Neue, Arial, sans-serif"
    fontSize: "clamp(1.1875rem, 1rem + 0.6vw, 1.4375rem)"
    fontWeight: 600
    lineHeight: 1.3
    letterSpacing: "-0.01em"
  title:
    fontFamily: "Libre Franklin, Franklin Gothic Medium, Helvetica Neue, Arial, sans-serif"
    fontSize: "clamp(1.25rem, 1.1rem + 0.5vw, 1.5rem)"
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: "-0.015em"
  title-sm:
    fontFamily: "Libre Franklin, Franklin Gothic Medium, Helvetica Neue, Arial, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: "-0.01em"
  lede:
    fontFamily: "Libre Franklin, Franklin Gothic Medium, Helvetica Neue, Arial, sans-serif"
    fontSize: "1.1875rem"
    fontWeight: 400
    lineHeight: 1.6
  body:
    fontFamily: "Libre Franklin, Franklin Gothic Medium, Helvetica Neue, Arial, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.6
    fontFeature: "\"lnum\" 1"
  label:
    fontFamily: "Libre Franklin, Franklin Gothic Medium, Helvetica Neue, Arial, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 500
    lineHeight: 1.6
  caption:
    fontFamily: "Libre Franklin, Franklin Gothic Medium, Helvetica Neue, Arial, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 400
    lineHeight: 1.6
rounded:
  none: "0px"
spacing:
  gutter: "clamp(1rem, 4vw, 3rem)"
  section: "clamp(3rem, 6vw, 4.5rem)"
  measure: "64ch"
  page: "72rem"
components:
  button-primary:
    backgroundColor: "{colors.research-navy}"
    textColor: "{colors.on-navy}"
    rounded: "{rounded.none}"
    padding: "0.7rem 1.25rem"
    height: "2.875rem"
  button-primary-hover:
    backgroundColor: "{colors.research-navy-deep}"
    textColor: "{colors.on-navy}"
  button-quiet:
    backgroundColor: "transparent"
    textColor: "{colors.research-navy}"
    rounded: "{rounded.none}"
    padding: "0.7rem 1.25rem"
    height: "2.875rem"
  button-quiet-hover:
    backgroundColor: "{colors.key-data-panel}"
    textColor: "{colors.report-ink}"
  masthead:
    backgroundColor: "{colors.research-navy}"
    textColor: "{colors.on-navy}"
    typography: "{typography.body}"
  key-data:
    backgroundColor: "{colors.key-data-panel}"
    textColor: "{colors.report-ink}"
    rounded: "{rounded.none}"
    padding: "1.25rem 1.5rem 0.5rem"
  exhibit-caption:
    textColor: "{colors.secondary-ink}"
    typography: "{typography.caption}"
  input:
    backgroundColor: "{colors.report-paper}"
    textColor: "{colors.report-ink}"
    rounded: "{rounded.none}"
    padding: "0.65rem 0.75rem"
  degraded-banner:
    backgroundColor: "{colors.cached-panel}"
    textColor: "{colors.report-ink}"
    padding: "0.75rem 1rem"
  disclosures:
    backgroundColor: "{colors.key-data-panel}"
    textColor: "{colors.secondary-ink}"
    typography: "{typography.label}"
    padding: "2rem 1rem 2.5rem"
---

# Design System: Zetian Tao, Career Platform

## Overview

**Creative North Star: "The Initiation Note"**

Every page is set as page one of a sell-side equity research initiation, with the candidate as the covered name. A navy house band carries the navigation; below it, a coverage line, a tinted key-data box, a thesis paragraph, and numbered, ruled exhibits do the work that a hero, skill pills and equal cards would do on a portfolio template. The reader is a recruiter in finance or technology who scans before reading, so density is that of a printed report: one column of measured prose beside one column of data, nothing ornamental between them.

The material is cool report-white paper and near-black ink. Structure comes from rules, not containers: a heavy ink rule opens each exhibit, hairlines separate rows, and a navy rule marks a column header. There are no rounded corners, no drop shadows, no cards, and no imagery. One sans family, Libre Franklin, carries every role through weight alone, with lining figures site-wide and tabular figures wherever a date or figure sits in a column.

Motion is limited to 120ms ease-out colour and underline transitions on links and buttons. Nothing animates into view.

**Key Characteristics:**
- Navy house band at the top, pale panel disclosures band at the foot, paper between.
- Two-column title block: name, discipline and thesis on the left (about 1.85fr); key data on the right (min 19rem).
- Numbered exhibits ("Exhibit 1: Skills by discipline") opened by a 3px ink rule, closed by a small "Source:" caption when the content has a real source.
- Square everything: zero radius on buttons, inputs, panels and the status marker.
- One family, weight-led hierarchy from 800 (name) down to 400 (body).

## Colors

A restrained research-house palette: cool near-white paper, blue-black ink, and one saturated research navy, with three semantic hues reserved for state.

### Primary
- **Research Navy** (oklch(34% 0.085 258)): the house colour. Fills the masthead band and the primary action button; sets link text, the discipline line under the name, the 4px top rule of the key-data box, and the 2px rule under skill-column headers. Also the text-selection fill.
- **Deep Research Navy** (oklch(27% 0.07 260)): hover state for filled navy buttons only.

### Neutral
- **Report Paper** (oklch(98.6% 0.003 250)): page background and input fill. Cool, nearly neutral white, never cream.
- **Key Data Panel** (oklch(95.4% 0.012 255)): the one tinted surface. Used for the key-data box, the disclosures footer band, and the quiet button's hover fill.
- **Report Ink** (oklch(21% 0.025 262)): body text, headings, and the heavy 3px exhibit rule and 1px key-data heading rule.
- **Secondary Ink** (oklch(43% 0.025 262)): coverage lines, dates, metadata, key-data labels, source captions, disclosure text.
- **Hairline** (oklch(86% 0.012 262)): 1px row separators in ledgers, skill columns, key-data rows, contact rows and the footer top edge.
- **Control Line** (oklch(58% 0.02 262)): 1px stroke on form inputs, darker than the hairline so fields read as controls.
- **On Navy** (oklch(97.5% 0.008 258)) and **On Navy Muted** (oklch(84% 0.035 258)): text on the masthead; muted for idle nav links, full for the current page and the name.

### Semantic
- **Focus Blue** (oklch(52% 0.16 255)): 3px focus outline everywhere except on the masthead, where the outline switches to On Navy.
- **Live Green** (oklch(45% 0.11 155)): the "Live database" status.
- **Cached Amber** (oklch(49% 0.12 62)) with **Cached Panel** (oklch(95% 0.045 85)): the "Cached snapshot" status and the degraded banner (panel fill, amber bottom rule).
- **Error Red** (oklch(48% 0.17 27)): form error text, semibold.

### Named Rules
**The House Band Rule.** Navy appears as a filled surface in exactly two places: the masthead band and the primary action button. Everywhere else it is a line or text (links, discipline line, column-header rules, key-data top rule), never a second filled block.

**The One Tint Rule.** The only tinted surface is the Key Data Panel. If a new region needs separation, use a rule, not a new fill.

## Typography

**Display Font:** Libre Franklin, self-hosted variable woff2, weights 100 to 900 (with Franklin Gothic Medium, Helvetica Neue, Arial, sans-serif)
**Body Font:** Libre Franklin (same file)

**Character:** A news-gothic grotesque that reads as financial print. Hierarchy is carried by weight and size in one family: a heavy, tightly tracked name; semibold navy discipline line; bold exhibit titles; regular body.

### Hierarchy
- **Display** (800, clamp(2.75rem, 1.4rem + 4.6vw, 5rem), 0.98, -0.035em): the candidate's name on Home and the project title on project pages. Once per page.
- **Headline** (800, clamp(2.25rem, 1.5rem + 2.8vw, 3.5rem), 1, -0.03em): interior page heads (Resume, Portfolio, Contact, Page not found).
- **Discipline** (600, clamp(1.1875rem, 1rem + 0.6vw, 1.4375rem), 1.3, navy): the coverage subject under the name, majors joined with " + ".
- **Title** (700, clamp(1.25rem, 1.1rem + 0.5vw, 1.5rem), -0.015em): exhibit headings.
- **Title Small** (700, 1.25rem, -0.01em): ledger row titles and project-page sub-heads.
- **Lede** (400, 1.1875rem, 1.6): the thesis paragraph, capped at 64ch.
- **Body** (400, 1rem, 1.6): all running text, prose capped at 64ch.
- **Label** (500, 0.875rem to 0.9375rem): key-data labels, ledger dates and metadata, nav links (0.9375rem, 500; 650 when current), column heads (0.9375rem, 700, navy).
- **Caption** (400, 0.8125rem, secondary ink): exhibit "Source:" lines.

### Named Rules
**The One Family Rule.** Libre Franklin only. Do not introduce a second face for display, labels, or numbers; change weight instead.

**The Figures Rule.** Lining figures are on for the whole body. Any date, date range, or path that sits in a column or data cell also takes tabular figures (`tabular-nums lining-nums`), so dates align down a ledger.

## Layout

The page frame is a single centred column, max 72rem, with a fluid gutter (clamp(1rem, 4vw, 3rem)) on both sides; masthead and disclosures inner rows share the same width so the left edge holds from top to bottom. Top padding of the main column is clamp(2.5rem, 6vw, 4.5rem).

The title block is a two-column grid (minmax(0, 1.85fr) and minmax(19rem, 1fr)) with a gap of clamp(2rem, 5vw, 4.5rem); text on the left, key data on the right, aligned to the top. Exhibits stack below at a section spacing of clamp(3rem, 6vw, 4.5rem); the disclosures footer sits 1.25x that below the last exhibit. Running text is capped at 64ch; disclosure text at 72ch.

Inside exhibits, the skill table is two equal columns; dated ledger rows put a 10rem date column before the content; key-data and contact rows use a fixed label column (6.75rem and 8.5rem) beside the value.

Breakpoints: at 52rem the title block and dated ledger rows collapse to one column (key data moves below the thesis; dates sit above titles). At 30rem the skill table, key-data rows and contact rows stack, the masthead tightens, and buttons in the action row go full width.

## Elevation & Depth

Flat. There are no drop shadows anywhere. Depth is expressed by rule weight and by the single tinted panel: a 3px ink rule opens an exhibit, a 4px navy rule caps the key-data box, a 2px navy rule underlines column heads, and 1px hairlines divide rows. The only `box-shadow` in the build is a 3px inset bar under the nav links, which is an underline (a rule), not elevation.

### Named Rules
**The Rule Weight Rule.** Separation is a line, and its weight says its rank: 4px navy (key-data cap), 3px ink (exhibit open), 2px navy (column head), 1px ink (key-data heading), 1px hairline (row). Do not add a new weight.

## Shapes

Every corner is square (0px): buttons, inputs, the key-data box, the degraded banner and the status marker, which is a 0.55rem filled square, not a dot. Borders are 1px except the 1.5px button stroke and the structural rules above. There is no clipping, masking, or decorative geometry.

## Components

### Masthead
- **Character:** the research house's band; the only full-bleed navy surface.
- **Name:** On Navy, 700, 1.0625rem, links home; underline on hover.
- **Nav:** On Navy Muted, 0.9375rem, 500, min height 2.875rem. Hover lifts to On Navy with a 3px muted inset underline; the current page (`aria-current`) is On Navy, 650, with a 3px On Navy underline. Wraps under the name on narrow screens. Focus outline switches to On Navy.

### Title Block
- Display name, navy discipline line, secondary-ink coverage line (school, class year, location joined with " · "), the thesis at lede size, then the action row (gap 0.75rem 1.5rem).

### Key Data Box
- **Style:** Key Data Panel fill, 4px navy top rule, square, padding 1.25rem 1.5rem 0.5rem (1rem inline on small screens).
- **Heading:** "Key data", 1rem, 700, over a 1px ink rule.
- **Rows:** label column 6.75rem in secondary ink (0.875rem, 500); value semibold (600); 1px hairline between rows, none after the last. Dates use tabular figures. Multi-value cells stack one value per line.
- Reused on project pages for Role, Built with, Started, Live, Source.

### Exhibit
- **Style:** 3px ink top rule, 1rem padding above the title, section spacing above.
- **Heading:** "Exhibit N: Subject", numbered in the h2 itself and counted per page in order of appearance.
- **Source caption:** 0.8125rem secondary ink, "Source: ..." naming the real origin of the data, placed after the content. Omitted when there is no honest single source.
- **Empty state:** a plain secondary-ink sentence at 64ch; empty exhibits are otherwise hidden.

### Skill Table
- Two equal columns (Finance, Technical) with a column gap of clamp(1.5rem, 4vw, 3.5rem). Column head 0.9375rem, 700, navy, over a 2px navy rule; each skill a row with 0.6rem vertical padding over a 1px hairline. Stacks to one column below 30rem.

### Ledger Rows
- An ordered list of rows (projects, education, experience, certifications), each padded 1.25rem / 1.375rem and divided by a 1px hairline, none after the last.
- Title Small heading (linked when there is a destination); body capped at 64ch; metadata in secondary ink at 0.9375rem, items joined with " · ".
- **Dated variant:** a 10rem date column (secondary ink, 500, tabular figures, "Mon YYYY – Mon YYYY" with an en dash, or "– Present") beside the content; stacks above the title below 52rem. Experience bullets are a plain disc list with 0.35rem between items.

### Buttons and Text Links
- **Shape:** square (0px), min height 2.875rem, padding 0.7rem 1.25rem, 600 weight, 1.5px stroke.
- **Primary:** filled Research Navy with On Navy text; hover to Deep Research Navy. One per action row. When the action is email, the label shows the address.
- **Quiet:** transparent with navy text and navy stroke; hover fills Key Data Panel, text and stroke go to ink.
- **Text link:** navy, 1px underline at 0.22em offset, 600 weight in action rows with the same 2.875rem target height; hover goes to ink with a 2px underline. Used for secondary destinations (LinkedIn, GitHub, other pages).
- Transitions: 120ms ease-out on colour, border and underline thickness.
- Below 30rem, buttons in the action row go full width.

### Inputs / Fields (admin)
- **Style:** Report Paper fill, 1px Control Line stroke, square, padding 0.65rem 0.75rem, inheriting the body font. Labels 600 above the field; forms max 36rem wide in a single column.
- **Submit:** the bare `button` element is filled navy with no stroke, hover to deep navy.
- **Focus:** the global 3px Focus Blue outline at 3px offset.
- **Error:** Error Red, 600, as a text line.
- Admin sections reuse the legacy `card` container, which in this world is a ruled section (1px hairline top, 1.5rem vertical padding), not a box.

### Status Indicator
- Inline label preceded by a 0.55rem square in currentColor: Live Green "Live database" or Cached Amber "Cached snapshot", semibold inside the key-data box.

### Degraded Banner
- Full-width strip directly under the masthead: Cached Panel fill, ink text at 500, 1px Cached Amber bottom rule, centred, with `role="status"`. Appears only when the snapshot is serving.

### Disclosures Footer
- Full-bleed Key Data Panel band with a 1px hairline top. Heading "How this site runs" at 0.875rem, 700, ink; paragraphs 0.875rem in secondary ink at 72ch, ending with a "Source:" line linking the repository.

## Do's and Don'ts

### Do:
- **Do** number every exhibit in its h2 ("Exhibit 1: Skills by discipline") and count per page in order of appearance.
- **Do** close an exhibit with a "Source:" caption (0.8125rem, secondary ink) when its content has a real, nameable source; omit the caption rather than write a vague one.
- **Do** separate with rules: 1px hairlines between rows, a 3px ink rule to open each exhibit, a 2px navy rule under column heads.
- **Do** keep one filled navy primary action per action row, followed by a quiet button and then plain text links.
- **Do** set every date, date range and data figure with tabular lining figures and en-dash ranges ("Mon YYYY – Mon YYYY").
- **Do** cap running text at 64ch and keep the name, discipline line and key data in the first viewport on desktop.
- **Do** hide sections with no real content instead of filling them; a single secondary-ink sentence is the only empty state.

### Don't:
- **Don't** use cards, rounded corners, or drop shadows; every corner is 0px and every container is a ruled region or the one tinted panel.
- **Don't** fill any surface with navy other than the masthead band and the primary button.
- **Don't** introduce a second typeface, an icon font, or glyph icons; the status marker is a CSS square.
- **Don't** put an eyebrow, kicker, or small uppercase label above a heading; the exhibit number lives in the heading text itself.
- **Don't** render skills as pills, tags or chips; they are rows in a ruled two-column table.
- **Don't** add a new tinted surface or a new rule weight to separate a region.
