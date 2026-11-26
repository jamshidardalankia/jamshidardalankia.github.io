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
provided: a higher-resolution portrait, public overviews for the two working
papers without summaries, teaching-evaluation evidence, and selected code links.
They contain prompts, not fabricated content. Remove a corresponding reminder
when supplying the material. Working-paper overview reminders disappear when
an abstract/overview disclosure is added to the original paper entry. Code
reminders disappear when `_data/research_code.csv` contains a release.

The existing image is only 126 × 128 pixels; replace it with an approved image
of at least 600 × 600 pixels before removing the portrait reminder. Keep
unpublished research at the public level of detail approved by the owner.

