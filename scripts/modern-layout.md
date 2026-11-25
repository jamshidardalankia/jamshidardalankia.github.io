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
