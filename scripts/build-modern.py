#!/usr/bin/env python3
"""Build the alternate layout from the existing site's public content.

Run with Python 3 after editing index.html, code/index.html, or
research-applications/index.html. No packages are required. The original pages
and styles are never changed. Jekyll markup is retained when present.
"""

import argparse
import csv
import hashlib
import re
from html import escape
from pathlib import Path


def element(text, tag, marker):
    """Return one balanced element selected by an exact opening-tag marker."""
    start = next(m for m in re.finditer(rf"<{tag}\b[^>]*>", text)
                 if marker in m.group())
    depth = 0
    for match in re.finditer(rf"</?{tag}\b[^>]*>", text[start.start():]):
        depth += -1 if match.group().startswith("</") else 1
        if depth == 0:
            return text[start.start():start.start() + match.end()]
    raise ValueError(f"Unclosed {tag}: {marker}")


def inner(block):
    return block[block.index(">") + 1:block.rfind("</")]


def lower_levels(block):
    return re.sub(r"(<\/?h)([3-6])\b", lambda m: m[1] + str(int(m[2]) - 1), block)


def reminder(label, explanation, visible=False):
    caption = escape(label) if visible else f'<span class="sr-only">{escape(label)}</span>'
    return (f'<details class="completion"><summary title="{escape(label, quote=True)}">'
            f'<span class="missing-square" aria-hidden="true"></span>{caption}</summary>'
            f'<p>{escape(explanation)}</p></details>')


def build(root):
    style_version = hashlib.sha256((root / "modern/styles.css").read_bytes()).hexdigest()[:12]
    home = (root / "index.html").read_text()
    apps = (root / "research-applications/index.html").read_text()
    code = (root / "code/index.html").read_text()
    profile_links = element(home, "nav", 'class="profile-links"')
    frontmatter = "---\nlayout: academic-page\n---\n" if home.startswith("---\n") else ""
    research = element(home, "section", 'id="research"')
    research = re.sub(r'<h2\b[^>]*>Research</h2>', '', research, count=1)
    research = lower_levels(research).replace('href="./figures/', 'href="../figures/').replace('src="./figures/', 'src="../figures/')
    research = research.replace('<span>Overview</span>', '<span>View overview</span>')
    research = research.replace('<span>Abstract and figure</span>', '<span>View abstract and figure</span>')
    research = research.replace('<span>Abstract</span>', '<span>View abstract</span>')
    for paper_id in ("crypto-regimes", "local-pathways"):
        paper = element(research, "article", f'id="{paper_id}"')
        if 'class="paper-abstract"' not in paper:
            updated = paper.replace('</article>', reminder('Add a public overview', 'Add a short, approved overview of this working paper when ready. A full manuscript is not required.') + '</article>')
            research = research.replace(paper, updated)
    teaching = element(home, "section", 'id="teaching"')
    teaching = re.sub(r'<h2\b[^>]*>Teaching</h2>', '', teaching, count=1)
    teaching = lower_levels(teaching)
    teaching += '<section class="teaching-group" aria-labelledby="evaluations-heading"><h2 id="evaluations-heading">Teaching evaluations</h2>' + reminder('Teaching evaluation summary', 'Add an exact, anonymous student quote with its course and term, or a rating with its scale and number of responses.', True) + '</section>'
    education = element(home, "section", 'id="education"')
    experience = element(home, "section", 'id="experience"')
    service = element(home, "section", 'id="service"')
    applications = inner(element(apps, "main", 'id="main"'))
    applications = re.sub(r'<h1\b[^>]*>.*?</h1>', '', applications, count=1, flags=re.S)
    code_body = inner(element(code, "main", 'id="main"'))
    code_body = re.sub(r'<h1\b[^>]*>.*?</h1>', '', code_body, count=1, flags=re.S)

    data_file = root / '_data/research_code.csv'
    releases = list(csv.DictReader(data_file.open())) if data_file.exists() else []
    if not releases:
        marker = '<section class="subpage-section" aria-labelledby="repositories-pending"><h2 id="repositories-pending">Project repositories</h2>' + reminder('Selected research code', 'Add the public GitHub repository URL and related paper for each code release you choose to share.', True) + '</section>'
        code_body = code_body.replace('<section class="subpage-section" aria-labelledby="research-data">', marker + '<section class="subpage-section" aria-labelledby="research-data">')
    about_intro = '<p class="about-intro">I study how financial networks shape systemic risk and portfolio diversification.</p>'
    pages = {
        "": ("Research", "research-heading", research, "Financial networks",
             "I study how financial networks shape systemic risk and portfolio diversification."),
        "teaching": ("Teaching", "teaching-heading", teaching, "Economics & quantitative finance", ""),
        "research-applications": ("Research Applications", "applications-heading", applications, "From research to practice", ""),
        "code": ("Code", "code-heading", code_body, "Research resources", ""),
        "about": ("About", "about-heading", about_intro + education + experience + service, "Academic background", ""),
    }
    navigation = [("", "Research"), ("teaching", "Teaching"),
                  ("research-applications", "Research Applications"),
                  ("code", "Code"), ("about", "About")]
    for slug, (title, heading_id, content, eyebrow, intro) in pages.items():
        prefix = "../" if slug else "./"
        classic = "../../" if slug else "../"
        nav = []
        for destination, label in navigation:
            href = prefix + (destination + "/" if destination else "")
            current = ' aria-current="page"' if destination == slug else ""
            nav.append(f'<a href="{href}"{current}>{label}</a>')
        description = intro or f"{title} — Jamshid Ardalankia, PhD candidate in Economics at Virginia Tech."
        heading = f'<h1 id="{heading_id}" class="sr-only">Research</h1>' if not slug else f'<header class="page-header"><h1 id="{heading_id}">{title}</h1></header>'
        portrait_note = reminder('Add a higher-resolution portrait', 'Replace the current 126 × 128 pixel image with a higher-resolution portrait, ideally at least 600 × 600 pixels.')
        page = f'''{frontmatter}<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{escape(description, quote=True)}">
  <meta name="robots" content="noindex, follow">
  <meta name="referrer" content="no-referrer">
  <meta http-equiv="Content-Security-Policy" content="script-src 'none'; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'">
  <title>{title} | Jamshid Ardalankia</title>
  <link rel="icon" href="data:,">
  <link rel="stylesheet" href="{prefix}styles.css?v={style_version}">
</head>
<body class="modern-site" id="top">
  <a class="skip-link" href="#main">Skip to content</a>
  <div class="site-shell">
    <header class="sidebar">
      <div class="identity">
        <p class="institution">VIRGINIA TECH</p>
        <div class="portrait-wrap"><img class="portrait" src="{classic}assets/profile.jpg" width="126" height="128" alt="Jamshid Ardalankia speaking at an event">{portrait_note}</div>
        <a class="name" href="{prefix}">Jamshid Ardalankia</a>
        <p class="role">PhD candidate in Economics</p>
        <p class="affiliation">Department of Economics</p>
        <a class="email" href="mailto:ardalankia@vt.edu">ardalankia@vt.edu</a>
      </div>
      <nav class="site-nav" aria-label="Primary navigation">
        {''.join(nav)}
      </nav>
      {profile_links}
      <p class="version-link"><a href="{classic}">Classic version</a></p>
    </header>
    <div class="main-column">
      <main id="main" class="content" tabindex="-1">
        {heading}
        {content}
      </main>
      <p class="reminder-key"><span class="missing-square" aria-hidden="true"></span>Material to add — select a square for details.</p>
      <footer class="site-footer"><span>© Jamshid Ardalankia</span><a href="#top">Back to top</a></footer>
    </div>
  </div>
</body>
</html>
'''
        destination = root / "modern" / slug / "index.html"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(page)
        print(destination.relative_to(root))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    build(parser.parse_args().root)

