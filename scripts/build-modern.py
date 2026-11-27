#!/usr/bin/env python3
"""Build the alternate layout from the existing site's public content.

Run with Python 3 after editing index.html, code/index.html, or
research-applications/index.html. No packages are required. The original pages
and styles are never changed. Jekyll markup is retained when present.
"""

import argparse
import csv
import hashlib
import json
import re
from html import escape, unescape
from pathlib import Path
from urllib.parse import urlsplit


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


def resource_url(value):
    """Allow web links and site-relative resources, never executable URLs."""
    value = value.strip()
    if not value:
        return ""
    parsed = urlsplit(value)
    if parsed.scheme not in ("", "http", "https") or value.startswith("//"):
        raise ValueError(f"Unsupported resource URL: {value}")
    return value


def resource_link(url, label, css_class="", description=""):
    url = resource_url(url)
    external = urlsplit(url).scheme in ("http", "https") and urlsplit(url).hostname != "jamshidardalankia.github.io"
    target = ' target="_blank" rel="noopener"' if external else ""
    accessible = f' aria-label="{escape(description, quote=True)}"' if description else ""
    return f'<a class="{css_class}" href="{escape(url, quote=True)}"{target}{accessible}>{escape(label)}</a>'


def resource_disclosure(paper_id, kind, label, title, body, pending=False):
    marker = '<span class="missing-square" aria-hidden="true"></span>' if pending else ""
    status = "; material to add" if pending else ""
    state = " resource-pending" if pending else ""
    return (f'<details class="paper-resource resource-{kind}{state}" name="resources-{paper_id}">'
            f'<summary aria-label="{escape(label + " for " + title + status, quote=True)}">'
            f'{escape(label)}{marker}</summary><div class="resource-content">{body}</div></details>')


def earlier_preprints(root):
    """Keep earlier public work accessible without crowding current research."""
    data_path = root / "_data/earlier_preprints.json"
    records = json.loads(data_path.read_text()) if data_path.exists() else []
    if not records:
        return ""
    papers = []
    for item in records:
        authors = [f'<strong>{escape(name)}</strong>' if name == "Jamshid Ardalankia" else escape(name)
                   for name in item["authors"]]
        byline = ', '.join(authors[:-1]) + ', and ' + authors[-1] if len(authors) > 1 else authors[0]
        title = escape(item["title"])
        papers.append(
            f'<article class="entry paper" id="{escape(item["id"], quote=True)}">'
            f'<div class="paper-heading"><h3>{resource_link(item["url"], item["title"])}</h3>'
            f'<time class="paper-year" datetime="{item["year"]}">{item["year"]}</time></div>'
            f'<p class="byline">{byline}</p>'
            f'<details class="paper-abstract"><summary><span>Abstract</span>'
            f'<span class="sr-only"> for {title}</span></summary>'
            f'{resource_link(item["url"], "Read the original abstract on arXiv", "manuscript-link")}'
            '</details></article>')
    return ('<section class="group" id="earlier-preprints" aria-labelledby="preprints-heading">'
            '<h2 class="label" id="preprints-heading">Earlier preprints</h2>'
            f'<details class="research-archive"><summary>View earlier preprints ({len(records)})</summary>'
            '<div class="details-body">' + ''.join(papers) + '</div></details></section>')


def organize_research(research):
    """Distinguish developing projects from manuscripts ready to circulate."""
    working = element(research, "section", 'aria-labelledby="working-heading"')
    progress = element(research, "section", 'aria-labelledby="progress-heading"')
    developing = element(working, "article", 'id="local-pathways"')
    working_updated = working.replace(developing, "")
    progress_updated = progress.replace('</h2>', '</h2>\n' + developing, 1)
    introduction = ('<section class="research-intro" aria-labelledby="interests-heading">'
                    '<h2 id="interests-heading">Research interests</h2>'
                    '<p>Financial economics: '
                    '<a href="#ardalankia2025hidden">financial networks</a>; '
                    '<a href="#local-pathways">systemic risk and financial crises</a>; '
                    '<a href="#structural-crowding">asset pricing and portfolio choice</a>; '
                    '<a href="#ai-investor-behavior">AI, large language models, '
                    'and financial market stability</a>.</p></section>')
    organized = research.replace(progress, "").replace(
        working, introduction + '\n' + working_updated + '\n' + progress_updated, 1)
    return re.sub(r'(?m)^[ \t]+$', '', organized)


def add_paper_resources(research, root):
    """Keep every paper's links and disclosures together without fabricating assets."""
    data_path = root / "_data/paper_resources.json"
    resources = json.loads(data_path.read_text()) if data_path.exists() else {}
    code_path = root / "_data/research_code.csv"
    releases = list(csv.DictReader(code_path.open())) if code_path.exists() else []

    for match in list(re.finditer(r'<article class="entry paper" id="([^"]+)"', research)):
        paper_id = match[1]
        paper = element(research, "article", f'id="{paper_id}"')
        updated = paper
        heading = element(paper, "div", 'class="paper-heading"')
        heading_text = re.search(r'<h[3-5]\b[^>]*>(.*?)</h[3-5]>', heading, re.S)[1]
        title = unescape(re.sub(r'<[^>]+>', '', heading_text))
        entry = resources.get(paper_id, {})
        recognition = entry.get("recognition", [])
        if recognition:
            byline = element(updated, "p", 'class="byline"')
            notes = ''.join(f'<p class="paper-recognition">{escape(item["text"])}</p>'
                            for item in recognition)
            updated = updated.replace(byline, byline + notes, 1)
        heading_link = re.search(r'href="([^"]+)"', heading_text)
        paper_url = entry.get("paper_url") or (unescape(heading_link[1]) if heading_link else "")
        row = []

        if paper_url:
            row.append(resource_link(paper_url, "Paper", "paper-resource-link resource-paper", "Read " + title))
        else:
            row.append(resource_disclosure(paper_id, "paper", "Paper", title,
                       '<p class="resource-note">Public manuscript link to be added.</p>', True))

        code_url = entry.get("code_url") or next((r["repository"] for r in releases if r["paper_id"] == paper_id and r.get("repository")), "")
        if code_url:
            row.append(resource_link(code_url, "Code", "paper-resource-link resource-code", "Code for " + title))
        else:
            row.append(resource_disclosure(paper_id, "code", "Code", title,
                       '<p class="resource-note">Public code repository link to be added.</p>', True))

        audio = entry.get("audio") or {}
        if audio.get("src"):
            audio_src = escape(resource_url(audio["src"]), quote=True)
            audio_body = f'<audio controls preload="none" aria-label="Audio summary of {escape(title, quote=True)}" src="{audio_src}"></audio>'
            if audio.get("description"):
                audio_body += f'<p class="resource-note">{escape(audio["description"])}</p>'
            if audio.get("transcript_url"):
                audio_body += resource_link(audio["transcript_url"], "Read transcript", "resource-transcript")
            row.append(resource_disclosure(paper_id, "audio", "Audio summary", title, audio_body))
        else:
            row.append(resource_disclosure(paper_id, "audio", "Audio summary", title,
                       '<p class="resource-note">Audio summary to be added.</p>', True))

        if 'class="paper-abstract"' in paper:
            abstract = element(paper, "details", 'class="paper-abstract"')
            label = "Overview" if re.search(r'<span>(?:View )?[Oo]verview</span>', abstract) else "Abstract"
            body = re.sub(r'^\s*<summary\b[^>]*>.*?</summary>', '', inner(abstract), count=1, flags=re.S)
            row.append(resource_disclosure(paper_id, "abstract", label, title, body))
            updated = updated.replace(abstract, "")
        else:
            row.append(resource_disclosure(paper_id, "abstract", "Overview", title,
                       '<p class="resource-note">Short public overview to be added.</p>', True))

        role = entry.get("role", "")
        role_body = f'<p class="role-text">{escape(role)}</p>' if role else '<p class="resource-note">Brief description of my contribution to be added.</p>'
        row.append(resource_disclosure(paper_id, "role", "My role", title, role_body, not role))

        # The modern resource row replaces the classic code include/link.
        updated = re.sub(r'{%\s*include paper-code\.html\s+paper="[^"]+"\s*%}', '', updated)
        updated = re.sub(r'<a\b[^>]*class="[^"]*project-code[^\"]*"[^>]*>.*?</a>', '', updated, flags=re.S)
        row_html = f'<div class="paper-resources" role="group" aria-label="Resources for {escape(title, quote=True)}">' + ''.join(row) + '</div>'
        updated = updated.replace('</article>', row_html + '</article>')
        research = research.replace(paper, updated)
    return research


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
    research = organize_research(research)
    archive = earlier_preprints(root)
    research = research.replace('<section class="group meetings"', archive + '\n<section class="group meetings"', 1)
    research = add_paper_resources(research, root)
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
  <link rel="icon" type="image/svg+xml" href="{prefix}favicon.svg">
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
