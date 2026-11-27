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
faculty research page: a 236px profile column, compact sans-serif paper titles,
muted metadata, one blue accent, and rules beneath section headings. Abstracts
and publication figures remain in native, keyboard-accessible disclosures.
Research, teaching, education, experience, service, conferences, applications,
and data-source details are retained from the shared source pages.

## Red completion squares

The generator adds small red disclosures for material the owner has not yet
provided: a higher-resolution portrait, public overviews, research resources,
role descriptions, teaching-evaluation evidence, and selected code links.
They contain prompts, not fabricated content. Remove a corresponding reminder
when supplying the material. Working-paper overview reminders disappear when
an abstract/overview disclosure is added to the original paper entry. Code
reminders disappear when `_data/research_code.csv` contains a release.

The existing image is only 126 × 128 pixels; replace it with an approved image
of at least 600 × 600 pixels before removing the portrait reminder. Keep
unpublished research at the public level of detail approved by the owner.

## Resources and personal contributions

Every research entry, including working papers and the invited book chapter,
has the same compact row: Paper, Code, Audio summary, Abstract (or Overview),
and My role. Native disclosures open inline and share a per-paper `name`, so
supporting browsers keep one panel open at a time. Missing material is marked
by a small red square and an explicit note; there are no dead or invented links.
The classic version remains unchanged.

Edit `_data/paper_resources.json` using the article IDs from `index.html`, then
run the generator. `role` is the author's concise personal contribution, while
`role_source` records the evidence for maintainers and is not rendered. Never
infer a role from author order. The banking description is supplied by the
author; the multilayer-paper description follows the publisher's author roles.

`paper_url` optionally overrides the existing title link. `code_url` optionally
supplies a public repository, with `_data/research_code.csv` as a fallback.
Audio remains a reminder until a real, reviewed file is supplied, for example:

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
working papers and publications. It generates a collapsed section after Work
in progress and before conference activity. It retains the standard resource
row and My role panel. The year is the original arXiv posting year; paper titles
and author order follow the available paper records. The survival paper's older
title, "Optimized Memory Reveals the Survival Strategy for a Multi-agent
Competition", refers to the same arXiv identifier and must not be duplicated.

Link to the original abstract until its exact text is available for reuse; do
not invent an abstract or infer journal-submission history. The section makes
no claim about whether a paper has been submitted, rejected, or peer reviewed.
Copy this JSON into the rendered mirror's `_data` directory before rebuilding.
