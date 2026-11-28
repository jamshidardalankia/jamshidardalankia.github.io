# Two website layouts

The original site remains at `/`, with its existing `styles.css`, content,
navigation and subpages unchanged.

The alternate layout is at `/modern/`. It uses a separate stylesheet and
provides Research, Teaching, Research Applications, Code and About pages.
Its sidebar includes a link back to the original version. Internal links stay
in the same tab; external research and profile links open a new tab.

## Updating shared content

Edit the original source pages, then run:

```sh
python3 scripts/build-modern.py
```

This regenerates the alternate HTML from those source pages while preserving
the source content and Jekyll includes. Commit the regenerated files with the
content changes. Edit `modern/styles.css` for alternate-layout styling.

For an already-rendered static copy, run the same generator with
`--root /absolute/path/to/static/root`. Copy `modern/styles.css` and the existing
`assets/profile.jpg` alongside that output.

The alternate pages use `noindex, follow` while the two designs are being
compared. The original site's indexing behavior is unchanged.

## Compact academic presentation

The layout follows the proportions and reading hierarchy of a traditional
faculty research page: a 208px profile column, a 160px portrait, compact sans-serif paper titles,
muted metadata, one blue accent, and whitespace between sections. Section
headings use sentence case; navigation rows have no borders. Abstracts
and publication figures remain in native, keyboard-accessible disclosures.
Research, teaching, education, experience, service, conferences, applications,
and data-source details are retained from the shared source pages.

## Unfinished materials

Do not show a Materials to add checklist on the public pages. Missing paper
resources remain absent until real material is supplied. The existing image is
only 126 × 128 pixels; a future replacement should be an approved portrait of
at least 600 × 600 pixels. Keep unpublished research at the public level of
detail approved by the owner.

## Resources and personal contributions

Each research entry shows only its available resources, in a consistent order:
Paper, Code, Audio summary, Abstract (or Overview), and My role. Missing resources
have no visible controls or public checklist. Entries with no ready resources have no
resource row. Native disclosures open inline and share a per-paper `name`, so
supporting browsers keep one panel open at a time. There are no dead or invented
links. The same pattern supports earlier preprints and the invited book chapter.
The classic version remains unchanged.

Edit `_data/paper_resources.json` using the article IDs from `index.html`, then
run the generator. `role` is the author's concise personal contribution, while
`role_source` records the evidence for maintainers and is not rendered. Never
infer a role from author order. The banking description is supplied by the
author; the multilayer-paper description follows the publisher's author roles.

`paper_url` optionally overrides the existing title link. `code_url` optionally
supplies a public repository, with `_data/research_code.csv` as a fallback.
Audio is shown only when a real, reviewed file is supplied, for example:

```json
"audio": {
  "src": "../audio/approved-summary.mp3",
  "description": "AI-generated audio summary, reviewed by the author.",
  "transcript_url": "../audio/approved-summary-transcript.html"
}
```

The paths are relative to `/modern/`. Include the actual audio and transcript
when filling those fields. The player uses native audio controls, no autoplay,
and no preloading. Use the AI/review description only when it is accurate.
For a rendered Sites copy, copy the JSON and research-code CSV into its `_data`
directory before regenerating the pages with `--root`.

## Earlier preprints

`_data/earlier_preprints.json` lists earlier arXiv work separately from current
working papers and publications. It generates a collapsed section after
publications and before conference activity. It uses the same available-resource
row and omits missing My role descriptions. The year is the original arXiv posting year; paper titles
and author order follow the available paper records. The survival paper's older
title, "Optimized Memory Reveals the Survival Strategy for a Multi-agent
Competition", refers to the same arXiv identifier and must not be duplicated.

Link to the original abstract until its exact text is available for reuse; do
not invent an abstract or infer journal-submission history. The section makes
no claim about whether a paper has been submitted, rejected, or peer reviewed.
Copy this JSON into the rendered mirror's `_data` directory before rebuilding.

## Research stages and visual hierarchy

The research page starts with a concise research-interest statement supplied
by the owner. The order is Working papers & manuscripts, Publications (including
the invited chapter), Earlier preprints, and conferences. At the owner's request,
`organize_research` groups `local-pathways` and `ai-investor-behavior` with the
current manuscripts. No empty Work in progress heading remains. This display
choice does not imply that methods or results are final. Keep their existing
public descriptions; do not add findings. The saved classic layout is unchanged.

Section headings use 18px with weight 600; entry titles use 16px with weight
500; paper metadata, resource links and abstracts use 14px. Abstracts retain
justified text with a 1.65 line height. Recognition
notes use 13px on desktop and 14px on smaller screens. These values respect the
default browser setting. Research interests use 15px, with understated linked
topics that lead to the relevant project on the same page. The 48px section gaps
and 32px entry gaps preserve the reading hierarchy. Keep the established
DarkBlue accent. `modern/favicon.svg` is a local typographic JA monogram, shared
by all five modern pages; copy it alongside the stylesheet when rendering the
Sites mirror. The Scholar screenshot confirms the two earlier preprints and
shows two records for the same book-chapter title, which remains one site entry.

## Paper-level recognition

`recognition` in `_data/paper_resources.json` is an optional list of objects
with `text` and a supporting `source`. Render only the short text beneath the
authors, in muted italic type. The four initial notes repeat acceptances already
recorded in the SEA conference section. Use "Accepted for presentation"; do
not imply that an accepted talk was delivered or that acceptance was an award.
Keep dates, locations, program titles, and supporting links in the conference
section. Add other paper-specific honors only when their attribution is known.

## Open conference and teaching groups

Conference groups use regular headings and indented paper lists. They are
always visible, including earlier conference activity and honors. Program titles use regular
15px text to distinguish them from the primary research entries. Preserve the
SEA IDs, original program titles, authors, and links; label the counts as
accepted papers rather than claiming every accepted talk was delivered.

`organize_teaching` places Python Programming under Course instruction and the
investment-management course under a visible Teaching and thesis mentoring
heading. Their original roles and dates remain unchanged; no additional page or
foldout is created. Data Science for Quantitative Finance includes the owner's
guest-lecture topics: copulas and programming for econometric analysis.
The teaching-approach introduction uses the owner's wording about intuition
and real-world examples before introducing the mathematics.
Middle East Economics appears under Graduate Teaching Assistantships for Fall
2025 at Virginia Tech, before the Spring 2022 course.

The About introduction uses the owner's approved wording about financial
economics, systemic risk, crises, portfolio choice, AI, and econometrics.
Keep engineering out of this introductory paragraph.

## Selected student feedback

The modern Teaching page ends with one combined feedback section: seven exact,
anonymous student excerpts and the approved overall-teaching-effectiveness
result, 5.25 out of 6, with 12 responses and a rounded 67% response rate.
The numerical result comes from one evaluation, not an average across courses;
the quotes are selected from multiple evaluations. Keep the visible wording
"Selected teaching evaluation" and "Selected student feedback". The excerpts
retain the students' wording. No raw reports or student identities are published.
Use ordinary 16px text for quotes and 14px metadata, without frames or cards.
