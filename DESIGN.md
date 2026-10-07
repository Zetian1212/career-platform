---
name: Zetian Tao, Career Platform
description: A polished tile-grid portfolio that introduces a finance-and-systems student as a person, not a template.
colors:
  bg: "#f2f3f7"
  tile: "#ffffff"
  ink: "#11131a"
  muted: "#5a6072"
  line: "#e1e4ec"
  control-line: "#8a90a2"
  accent: "#4f3ff0"
  accent-deep: "#3a2bd1"
  accent-soft: "#ece9ff"
  on-accent-2: "#e6e3ff"
  dark-2: "#262a36"
  on-dark-2: "#b9bccb"
  mint: "#dcf5e8"
  mint-ink: "#0c5537"
  sky: "#dfeaff"
  sky-ink: "#1b4a9c"
  peach: "#ffe8da"
  peach-ink: "#7a3312"
  live: "#3ee08f"
  cached: "#f2b544"
  cached-panel: "#fff4dc"
  error: "#c0262d"
typography:
  display:
    fontFamily: "Manrope, Helvetica Neue, Arial, sans-serif"
    fontSize: "clamp(2.75rem, 1.6rem + 4.2vw, 5.25rem)"
    fontWeight: 800
    lineHeight: 0.95
    letterSpacing: "-0.045em"
  page-title:
    fontFamily: "Manrope, Helvetica Neue, Arial, sans-serif"
    fontSize: "clamp(2.5rem, 1.8rem + 2.8vw, 4rem)"
    fontWeight: 800
    lineHeight: 0.95
    letterSpacing: "-0.045em"
  title-lg:
    fontFamily: "Manrope, Helvetica Neue, Arial, sans-serif"
    fontSize: "clamp(1.6rem, 1.3rem + 1vw, 2rem)"
    fontWeight: 800
    lineHeight: 1.2
    letterSpacing: "-0.03em"
  title:
    fontFamily: "Manrope, Helvetica Neue, Arial, sans-serif"
    fontSize: "1.4rem"
    fontWeight: 800
    lineHeight: 1.2
    letterSpacing: "-0.02em"
  lede:
    fontFamily: "Manrope, Helvetica Neue, Arial, sans-serif"
    fontSize: "clamp(1.15rem, 1rem + 0.5vw, 1.35rem)"
    fontWeight: 400
    lineHeight: 1.45
  body:
    fontFamily: "Manrope, Helvetica Neue, Arial, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.6
  body-lg:
    fontFamily: "Manrope, Helvetica Neue, Arial, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 400
    lineHeight: 1.65
  label:
    fontFamily: "Manrope, Helvetica Neue, Arial, sans-serif"
    fontSize: "1rem"
    fontWeight: 700
    lineHeight: 1.6
  meta:
    fontFamily: "Manrope, Helvetica Neue, Arial, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 700
    lineHeight: 1.6
    fontFeature: "tnum"
rounded:
  focus: "6px"
  input: "12px"
  tile: "22px"
  pill: "999px"
spacing:
  gap: "1rem"
  page-gutter: "1.25rem"
  tile-pad: "2rem"
  tile-pad-intro: "2.75rem"
  tile-pad-mobile: "1.5rem"
  page-max: "76rem"
components:
  button-primary:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.tile}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "0 1.35rem"
    height: "2.875rem"
  button-primary-hover:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.tile}"
  button-soft:
    backgroundColor: "{colors.accent-soft}"
    textColor: "{colors.accent-deep}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "0 1.35rem"
    height: "2.875rem"
  button-soft-hover:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.tile}"
  nav-link:
    textColor: "{colors.muted}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "0 1rem"
    height: "2.75rem"
  nav-link-current:
    backgroundColor: "{colors.tile}"
    textColor: "{colors.ink}"
  chip:
    backgroundColor: "{colors.bg}"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    padding: "0.5rem 0.9rem"
  chip-dark:
    backgroundColor: "{colors.dark-2}"
    textColor: "{colors.tile}"
    rounded: "{rounded.pill}"
    padding: "0.5rem 0.9rem"
  tile:
    backgroundColor: "{colors.tile}"
    textColor: "{colors.ink}"
    rounded: "{rounded.tile}"
    padding: "{spacing.tile-pad}"
  tile-intro:
    backgroundColor: "{colors.tile}"
    rounded: "{rounded.tile}"
    padding: "{spacing.tile-pad-intro}"
  tile-dark:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.on-dark-2}"
    rounded: "{rounded.tile}"
    padding: "{spacing.tile-pad}"
  tile-accent:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.on-accent-2}"
    rounded: "{rounded.tile}"
    padding: "{spacing.tile-pad}"
  tile-mint:
    backgroundColor: "{colors.mint}"
    textColor: "{colors.ink}"
    rounded: "{rounded.tile}"
  tile-sky:
    backgroundColor: "{colors.sky}"
    textColor: "{colors.ink}"
    rounded: "{rounded.tile}"
  tile-peach:
    backgroundColor: "{colors.peach}"
    textColor: "{colors.ink}"
    rounded: "{rounded.tile}"
  input:
    backgroundColor: "{colors.tile}"
    textColor: "{colors.ink}"
    rounded: "{rounded.input}"
    padding: "0.7rem 0.85rem"
  degraded-banner:
    backgroundColor: "{colors.cached-panel}"
    textColor: "{colors.ink}"
    padding: "0.75rem 1.25rem"
---

# Design System: Zetian Tao, Career Platform

## Overview

**Creative North Star: "The Tiled Introduction"**

The site is a set of white and tinted tiles of different sizes laid on a cool light-gray ground, read like meeting someone in person: a name and a study line first, then a live status, the school, who they are, what they did, what they know, what they built, and how to reach them. Each tile carries one kind of fact and one role color, so the grid reads as a composed introduction rather than a uniform card wall.

The finish is polished and friendly without being playful: one variable sans (Manrope) at heavy weight with tight tracking for every heading, soft two-layer shadows that barely lift tiles off the ground, generous 22px corners, pill-shaped controls. Color is confined to whole tiles (one indigo, one ink-black, and pastel mint, sky, and peach) plus soft-indigo buttons; text inside stays ink or muted gray. Density is moderate: tiles hold short paragraphs and lists, never long prose.

This world replaces the rejected "Initiation Note" research-report design (navy, Libre Franklin, hairline rules), which was judged too empty and plain. Nothing from it carries over.

**Key Characteristics:**
- 12-column tile grid with mixed spans and dense packing; tiles are the only container.
- Manrope variable, self-hosted, 800 weight for every heading.
- One indigo accent; ink-black and three pastel tints as per-tile roles.
- Soft two-layer ambient shadow on every tile; 22px tile corners; pill controls.
- One staggered load cascade; a small hover lift on work tiles; nothing moves under reduced motion.

## Colors

A cool neutral ground with one saturated indigo, an ink-black counterweight, and three low-chroma pastels, each tied to a tile role.

### Primary
- **Signal Indigo** (accent): the one saturated color. Fills the single identity tile per page (the education tile on Home and Resume, one link tile on Contact), the hover state of every button, the focus ring, and text selection.
- **Deep Indigo** (accent-deep): indigo text on light surfaces: soft-button labels, job date lines, and the accent node label in the architecture diagram.
- **Indigo Wash** (accent-soft): soft-button fill and the accent node in the diagram.
- **Indigo Mist** (on-accent-2): body text on an indigo tile; headings and links on indigo stay white.

### Secondary
- **Ink Tile** (ink as background): the dark tile (status tile on Home, "Built with" on a project page, one link tile on Contact). Body text on it is **Slate Mist** (on-dark-2); headings and links are white. Chips inside it use **Graphite** (dark-2).

### Tertiary (role tints, each paired with its own ink for the tile heading)
- **Mint** (mint) with **Forest Ink** (mint-ink): Right now, and odd-numbered skill groups (Finance skills). Forest Ink also colors list markers.
- **Sky** (sky) with **Harbor Ink** (sky-ink): Off the clock, and even-numbered skill groups (Technical skills).
- **Peach** (peach) with **Rust Ink** (peach-ink): About me only.
- Chips on mint or sky sit on 78% white so they read as pills on the tint.

### Status
- **Live Green** (live) and **Amber Cached** (cached): the status dot in the dark status tile, each with a 4px 22%-alpha halo of its own color. **Cream Notice** (cached-panel) is the full-width degraded banner shown when the database is down. **Alert Red** (error) is admin form error text only.

### Neutral
- **Cool Mist** (bg): page ground, default chip fill, and plain diagram nodes.
- **White Tile** (tile): every default tile, active nav pill, input fill.
- **Ink** (ink): all heading and body text on light surfaces; primary button fill.
- **Slate** (muted): ledes, descriptions, nav links at rest, footer.
- **Hairline** (line): the single rule between resume entries.
- **Control Line** (control-line): input borders (3:1 against white) and the dashed fallback node in the diagram.

### Named Rules
**The Tint-Is-a-Role Rule.** A tint names what a tile holds, never decorates it: peach is About, mint is now and the first skill group, sky is off-hours and the second skill group, ink is the system status or build facts, indigo is the identity anchor. A new tile that does not fit a role is white.

**The One Indigo Tile Rule.** At most one indigo-filled tile per page. Indigo elsewhere appears only as soft buttons, dates, hover, focus, and selection.

## Typography

**Display Font:** Manrope (with Helvetica Neue, Arial, sans-serif)
**Body Font:** Manrope (same family)

**Character:** One self-hosted variable sans (weights 200 to 800, OFL) does every job. Headings are 800 with negative tracking so they read as solid, confident shapes; body stays 400 at a relaxed 1.6 leading; controls and labels use 700.

### Hierarchy
- **Display** (800, clamp 2.75rem to 5.25rem, 0.95, -0.045em): the single page greeting or page name in the intro tile ("Hi, I'm Zetian.", "Contact", "Page not found").
- **Page title** (800, clamp 2.5rem to 4rem): the h1 in a full-width page-head tile (Resume, Portfolio).
- **Title large** (800, clamp 1.6rem to 2rem, -0.03em): section-leading tile headings (About me, Experience, project names, Certifications).
- **Title** (800, 1.4rem, 1.2, -0.02em): every other tile heading; on tinted tiles it takes the tint's ink.
- **Lede** (400, clamp 1.15rem to 1.35rem, 1.45, muted): the one sentence under the display line, max 36ch in the intro tile.
- **Body large** (400, 1.125rem, 1.65, max 62ch): About paragraphs.
- **Body** (400, 1rem, 1.6): descriptions, max 52 to 70ch.
- **Label** (700, 1rem): nav, buttons, link rows; chips and list items use 600.
- **Meta** (700, 0.875rem, tabular numerals): job date ranges in Deep Indigo; resume date lines use tabular 700 at body size.

### Named Rules
**The Heading-Names-Itself Rule.** Every tile's first line is its heading, in plain words ("Right now", "Finance skills", "Get in touch"). No small uppercase label, eyebrow, or kicker sits above a heading. A data line such as a job's dates may precede the company name because it is the fact, not a category label.

## Layout

A centered page of max 76rem with 1.25rem gutters holds a header row, the tile grid, and a footer. The grid is 12 equal columns with a 1rem gap, dense auto-flow, and content aligned to the top.

Span vocabulary: full (12), wide (8), half (6), side (4). The intro tile spans 8 columns and two rows, with its text at the top and the action pills pinned to the bottom; it collapses to one row (single) or full width when it stands alone. A tall tile spans two rows (About me beside Right now and Off the clock). A fit tile aligns to the top instead of stretching. A page-head tile is full width with the title and actions on one baseline row. The experience band is a full-width, short tile (1.5rem by 2rem padding) carrying the section title and a soft button, followed by one side tile per job, so three jobs fill one row.

Tile padding is 2rem; intro and page-head tiles use 2.75rem. At 860px and below every span becomes full width, two-row spans release, the project tile stacks its diagram under its text, and all tile padding drops to 1.5rem. At 30rem and below nav pills tighten to 0.75rem side padding and action buttons stretch to share the row.

**The Mixed-Span Rule.** A page is composed of tiles of different sizes; a row of identical tiles appears only where the content is genuinely parallel (the job tiles, the two skill groups).

## Elevation & Depth

Depth is a single ambient layer: every tile, the admin card, and the active nav pill sit on the ground with the same soft two-layer shadow (a 1px contact shadow plus a wide 24px blur, both ink at 5 to 6% alpha). There are no borders on tiles and no tonal stacking. Job and project tiles, the clickable work, lift 3px on hover and their shadow deepens.

### Shadow Vocabulary
- **Tile rest** (`box-shadow: 0 1px 2px rgba(17,19,26,.06), 0 8px 24px rgba(17,19,26,.05)`): every tile, card, and the current nav pill.
- **Work hover** (`box-shadow: 0 2px 4px rgba(17,19,26,.06), 0 16px 36px rgba(17,19,26,.09)`): job and project tiles on hover only.
- **Status halo** (`box-shadow: 0 0 0 4px` the dot color at 22%): the live or cached status dot.

### Named Rules
**The One Shadow Rule.** All resting surfaces share one shadow. Never add a hard offset shadow, a colored shadow, or a border to stand a tile out; use a role tint instead.

## Shapes

Generously rounded rectangles (22px) for every tile and admin card; full pills (999px) for buttons, nav links, and chips; gently rounded 12px for inputs, the skip link, and diagram nodes; 6px on the focus outline. Circles appear only as the status dot. The architecture diagram is flat: rounded nodes in ground, indigo-wash, ink, and a dashed control-line outline for the fallback snapshot, joined by 2px soft lavender-gray connectors.

## Components

### Buttons
- **Shape:** full pill (999px), min height 2.875rem, 1.35rem side padding, 700 label.
- **Primary:** ink fill, white label. One per action row, for the main action (Email me, Source code, Home).
- **Soft:** indigo-wash fill, deep-indigo label, for every secondary action (View resume, LinkedIn, GitHub, Full details, Project details).
- **Hover:** both go to Signal Indigo with a white label in 140ms ease-out. Focus is the global 3px indigo outline at 3px offset.
- Admin `<button>` elements use the primary pill styling.

### Chips
- **Style:** pill (999px), 0.5rem by 0.9rem, 600 weight, ground fill on white tiles, 78% white on mint or sky, Graphite with white text inside the ink tile. Chips are static facts (skills, technologies), never filters.

### Cards / Containers (tiles)
- **Corner Style:** 22px.
- **Background:** white by default, or one role tint (see Colors).
- **Shadow Strategy:** the tile rest shadow (see Elevation).
- **Border:** none.
- **Internal Padding:** 2rem; 2.75rem for intro and page-head; 1.5rem on mobile.

### Inputs / Fields (admin)
- **Style:** white fill, 1px control-line border, 12px radius, 0.7rem by 0.85rem padding, inherited Manrope. Labels are 700 above the field; textareas start at 8rem and resize vertically. Forms sit in a full-width card, max 36rem wide.
- **Focus:** the global 3px indigo outline.
- **Error:** Alert Red, 700 weight text.

### Navigation
- **Header:** site name at left (800, -0.02em tracking), pill nav at right; wraps on narrow screens.
- **Links:** 700 muted text in a 2.75rem-tall pill. Hover fills the pill white and darkens the text to ink. The current section (`aria-current="page"`) is a white pill with ink text and the tile rest shadow.
- A skip link (ink, white text, 12px radius) drops in on focus.

### Intro tile
The page's opening tile: display heading and lede at top, action pills at bottom. On Home it spans 8 columns by 2 rows; on Project it is wide and single-row; on 404 it is full width.

### Status tile
Ink tile with a Title heading led by the status dot: Live Green "This site is online", or Amber Cached "Running on a cached copy" when degraded, then one Slate Mist sentence on how the site is hosted.

### Education tile
The indigo tile: school name as Title in white, degree, majors joined with "+", and class year in Indigo Mist.

### About / Right now / Off the clock
About me is a tall wide peach tile with Title-large in Rust Ink and Body-large paragraphs. Right now (mint) and Off the clock (sky) are side tiles holding a short bulleted list in 600 weight, list markers in the tint ink on mint.

### Experience band and job tiles
A full-width short band holds "Experience" (Title-large) and a soft "Full details" button at opposite ends. Each job is a white side tile: dates (Meta, Deep Indigo), company (Title), role line (600), then the first description line in muted 0.95rem. Job tiles lift on hover.

### Skill tiles
One half tile per skill group, alternating mint and sky, titled "{Group} skills", holding chips of only the skills in the profile.

### Project tile with architecture diagram
A wide (Home) or full (Portfolio) tile split into text and an inline SVG diagram (two columns, stacked on mobile): Title-large linked project name, muted summary, optional chips, soft or primary buttons. The diagram is 13px 700 Manrope, labelled for screen readers with a full sentence. Project tiles lift on hover. On a project page the same diagram sits alone in a full "How it runs" tile.

### Contact tile
A white side tile: "Get in touch" Title, the email as a large 800 link (1.3rem; up to 2.6rem on the Contact page), and a muted 700 link row at the bottom with 2.75rem tap targets.

### Degraded banner
A full-width Cream Notice strip above the header, centered 600 ink text, announced as a status region.

### Footer
Muted 0.9rem single line inside the page width, with an underlined source link.

### Motion
- **Load cascade:** every grid tile rises 12px from 35% opacity over 640ms on `cubic-bezier(.16, 1, .3, 1)`, staggered 50ms per tile and capped at 300ms from the seventh tile on. It runs once on load.
- **Work lift:** job and project tiles translate up 3px over 200ms with the deeper hover shadow.
- **Button color:** 140ms ease-out background and text color.
- Under `prefers-reduced-motion: reduce` the cascade does not run and the lift is removed.

## Do's and Don'ts

### Do:
- **Do** compose every page from tiles on the 12-column grid using the full, wide, half, side, intro, and tall spans; mix sizes.
- **Do** give a tile a tint only when it fills that tint's role, and color its heading with the tint's own ink.
- **Do** keep at most one indigo tile per page; use soft indigo pills for secondary actions and one ink pill for the primary action.
- **Do** set every heading in Manrope 800 with negative tracking, and let the heading be the tile's first line.
- **Do** fill tiles only from real profile data (education, experience, skills, projects, links, bio, interests); hide a tile when its data is absent, or say plainly that it is coming.
- **Do** keep every tap target at least 2.75rem tall and every focus state on the 3px indigo outline.
- **Do** disable the load cascade and hover lift under reduced motion.

### Don't:
- **Don't** put an eyebrow, kicker, or small uppercase label above a heading; the heading names itself.
- **Don't** invent stats, testimonials, skills, logos, or filler copy to fill a tile.
- **Don't** use tints, indigo, or the ink tile as decoration or to balance a row.
- **Don't** add borders, hard offset shadows, or colored shadows to tiles; there is one shadow.
- **Don't** introduce a second typeface or a system display face.
- **Don't** add motion beyond the single load cascade, the work-tile lift, and button color transitions.
- **Don't** bring back the Initiation Note vocabulary: navy, Libre Franklin, hairline-ruled report layout.
