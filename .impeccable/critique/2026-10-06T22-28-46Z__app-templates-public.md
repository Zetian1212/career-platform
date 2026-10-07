---
target: my website (public pages)
total_score: 16
max_score: 32
na_heuristics: 7,10
p0_count: 1
p1_count: 4
target_identity: "file:/Users/zetiantao/Desktop/Everything/University/Y5/Cloud Computing/career-platform/.claude/worktrees/impeccable-init/app/templates/public"
timestamp: 2026-10-06T22-28-46Z
slug: app-templates-public
---
Method: dual-agent (A: design review · B: detector + browser)

## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 2 | Degraded banner is good; no active nav state; every page titled "Career Platform" |
| 2 | Match System / Real World | 2 | Title is a course-project name; headline "Student at LMU" hides the Finance + IS majors |
| 3 | User Control and Freedom | 2 | 404 returns raw JSON with no nav; public "Admin" link leads to a login wall |
| 4 | Consistency and Standards | 2 | "View project" vs "Read case study" for one destination; links in browser-default blue, never --brand |
| 5 | Error Prevention | 2 | Empty Experience card always renders; email is mailto-only, address never shown |
| 6 | Recognition Rather Than Recall | 3 | Flat, obvious IA |
| 7 | Flexibility and Efficiency | n/a | Single-pass reading surface (resume PDF is the missing accelerator) |
| 8 | Aesthetic and Minimalist Design | 2 | Every section the same card weight; nothing leads |
| 9 | Error Recovery | 1 | JSON 404, no designed error pages |
| 10 | Help and Documentation | n/a | Portfolio needs no help system |
| **Total** | | **16/32** | **Acceptable (50%)** |

## Design Specificity Verdict
Category-interchangeable default: Arial, Tailwind-gray tokens, identical 12px white cards, pill chips, browser-default links. Nothing expresses "finance + tech hybrid". The strongest proof (self-hosted on Azure, survives DB outage) is buried in one paragraph.
Detector: 1 CLI finding (overused-font: Arial, base.html via site.css:9). Browser overlay: line-length-too-long on project paragraphs on / and /portfolio/career-platform (~934px measure); /resume clean. No :focus-visible styles, no @media queries, --line border 1.25:1 contrast (inputs). Text contrast otherwise passes AA/AAA.

## Priority Issues
- [P0] Production unreachable: http://172.183.16.158 returns nginx 404; :8000 times out (operational, not design).
- [P1] Resume page reads as broken: empty Experience card, education without dates/structured majors, no PDF. Fix: hide/design empty states, structure education, decide on PDF, supply real content. /impeccable harden, /impeccable clarify
- [P1] Hero lacks positioning and a primary action: "Student" headline, contact as small default links, 8 mixed skill chips. Fix: headline from real facts (Finance + IS, LMU '27), primary Email/Resume actions, show the address, group skills Finance vs Technical. /impeccable clarify, /impeccable layout
- [P1] No visual identity; technical proof hidden. Fix: deliberate type pairing with tabular figures, accent color on links/actions, measure ~65-75ch, honest "how this site runs" strip. /impeccable typeset, /impeccable colorize or /impeccable bolder
- [P1] Chrome leaks: public Admin link, one <title> for all pages, JSON 404, no meta/OG tags, no active nav, no focus-visible styles. /impeccable polish, /impeccable harden
- [P2] Project "case study" repeats the listing summary; repo URL is plain text. /impeccable shape, /impeccable layout

## Persona Red Flags
- Morgan (finance recruiter, 40 links): tab says "Career Platform", hero says "Student", no PDF, empty Experience. Closes within 10s.
- Tech recruiter: GitHub is a small underline; Azure/fallback engineering invisible; repo URL not clickable.
- Casey (mobile): no media queries, sub-44px inline link targets, email address never shown.
- Riley: typo URLs give JSON; /admin advertised; skip link focus has no background.

## Minor Observations
Skip-link focus unstyled; summary repeats headline; verbose location; "Finance; Information Systems..." should be two majors; no footer, favicon, last-updated; chip color hardcoded.

## Questions to Consider
- Why hide the site's strongest proof instead of making it the signature moment?
- Should the hero present two labelled, equal halves (Finance / Technical)?
- What real content can fill the Resume page this week?
