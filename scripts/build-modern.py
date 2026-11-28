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
    """Group the four current manuscripts as requested by the owner."""
    working = element(research, "section", 'aria-labelledby="working-heading"')
    progress = element(research, "section", 'aria-labelledby="progress-heading"')
    ai_project = element(progress, "article", 'id="ai-investor-behavior"')
    working_updated = working.replace('</section>', ai_project + '\n</section>', 1)
    introduction = ('<section class="research-intro" aria-labelledby="interests-heading">'
                    '<h2 id="interests-heading">Research interests</h2>'
                    '<p>Financial economics: '
                    '<a href="#ardalankia2025hidden">financial networks</a>; '
                    '<a href="#local-pathways">systemic risk and financial crises</a>; '
                    '<a href="#structural-crowding">asset pricing and portfolio choice</a>; '
                    '<a href="#ai-investor-behavior">AI, large language models, '
                    'and financial market stability</a>.</p></section>')
    organized = research.replace(progress, "").replace(
        working, introduction + '\n' + working_updated, 1)
    return re.sub(r'(?m)^[ \t]+$', '', organized)


def open_conference_groups(research):
    """Show each conference and its indented paper list without disclosures."""
    for number, match in enumerate(list(re.finditer(r'<details class="disclosure conference"[^>]*>', research)), 1):
        block = element(research, "details", match.group())
        summary = element(block, "summary", "")
        body = inner(element(block, "div", 'class="details-body"'))
        body = re.sub(r'(<\/?h)3\b', r'\g<1>4', body)
        body = body.replace('Three papers accepted for presentation.', '3 papers accepted for presentation.')
        body = body.replace('One paper accepted for presentation', '1 paper accepted for presentation')
        existing_id = re.search(r'\bid="([^"]+)"', match.group())
        group_id = existing_id[1] if existing_id else f'conference-history-{number}'
        expanded = (f'<section class="conference" id="{group_id}" aria-labelledby="{group_id}-heading">'
                    f'<h3 id="{group_id}-heading">{inner(summary)}</h3>'
                    f'<div class="conference-body">{body}</div></section>')
        research = research.replace(block, expanded, 1)
    return research


def organize_teaching(teaching):
    """Keep instruction and mentoring visible under their actual role headings."""
    earlier = element(teaching, "details", 'class="disclosure earlier-teaching"')
    courses = re.findall(r'<article class="course">.*?</article>', earlier, re.S)
    python_course = next(course for course in courses if '<h3>Python Programming</h3>' in course)
    mentoring_course = next(course for course in courses if 'Investment Management and Computational Programming' in course)
    instruction = element(teaching, "section", 'aria-labelledby="teach-instruction"')
    updated_instruction = instruction.replace('</section>', python_course + '\n</section>', 1)
    design = element(teaching, "section", 'aria-labelledby="teach-design"')
    mentoring = ('<section class="teaching-group" aria-labelledby="teach-mentoring">'
                 '<h2 class="label" id="teach-mentoring">Teaching and thesis mentoring</h2>'
                 + mentoring_course + '</section>')
    teaching = teaching.replace(earlier, '').replace(instruction, updated_instruction, 1)
    teaching = teaching.replace(design, mentoring + '\n' + design, 1)
    teaching = teaching.replace('Guest lecture on copulas.',
                                'Guest lecture on copulas and programming for econometric analysis.', 1)
    teaching = teaching.replace('I start with the economic intuition, then introduce the mathematics.',
                                'I start with the intuition using real-world examples, then introduce the mathematics.', 1)
    feedback = '''<section class="teaching-group student-feedback" aria-labelledby="teach-feedback">
<h2 class="label" id="teach-feedback">Selected student feedback</h2>
<p class="evaluation-result"><span class="evaluation-label">Selected teaching evaluation:</span> Overall teaching effectiveness <strong>5.25/6</strong> <span class="evaluation-meta">· 12 responses · 67% response rate</span></p>
<div class="student-quotes">
<blockquote><p>“He provided many helpful examples and interpretations. I appreciated him breaking down and walking through each line.”</p></blockquote>
<blockquote><p>“Kind and engaging, able to bring in both theory and real world examples”</p></blockquote>
<blockquote><p>“Nicest, most helpful, most understanding professor I've had.”</p></blockquote>
<blockquote><p>“He was very thorough in giving multiple examples when explaining concepts and plots.”</p></blockquote>
<blockquote><p>“He made sure to make the class feel integrated in the classroom and the learning. It felt very personalized.”</p></blockquote>
<blockquote><p>“Provided many examples and took time to answer questions”</p></blockquote>
<blockquote><p>“Was always available to help me. Responded very fast to emails.”</p></blockquote>
</div>
</section>'''
    teaching = teaching.replace('<!-- PROFILE TEACHING END -->',
                                feedback + '\n<!-- PROFILE TEACHING END -->', 1)
    return teaching


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

        code_url = entry.get("code_url") or next((r["repository"] for r in releases if r["paper_id"] == paper_id and r.get("repository")), "")
        if code_url:
            row.append(resource_link(code_url, "Code", "paper-resource-link resource-code", "Code for " + title))

        audio = entry.get("audio") or {}
        if audio.get("src"):
            audio_src = escape(resource_url(audio["src"]), quote=True)
            audio_body = f'<audio controls preload="none" aria-label="Audio summary of {escape(title, quote=True)}" src="{audio_src}"></audio>'
            if audio.get("description"):
                audio_body += f'<p class="resource-note">{escape(audio["description"])}</p>'
            if audio.get("transcript_url"):
                audio_body += resource_link(audio["transcript_url"], "Read transcript", "resource-transcript")
            row.append(resource_disclosure(paper_id, "audio", "Audio summary", title, audio_body))

        if 'class="paper-abstract"' in paper:
            abstract = element(paper, "details", 'class="paper-abstract"')
            label = "Overview" if re.search(r'<span>(?:View )?[Oo]verview</span>', abstract) else "Abstract"
            body = re.sub(r'^\s*<summary\b[^>]*>.*?</summary>', '', inner(abstract), count=1, flags=re.S)
            row.append(resource_disclosure(paper_id, "abstract", label, title, body))
            updated = updated.replace(abstract, "")

        role = entry.get("role", "")
        if role:
            role_body = f'<p class="role-text">{escape(role)}</p>'
            row.append(resource_disclosure(paper_id, "role", "My role", title, role_body))

        # The modern resource row replaces the classic code include/link.
        updated = re.sub(r'{%\s*include paper-code\.html\s+paper="[^"]+"\s*%}', '', updated)
        updated = re.sub(r'<a\b[^>]*class="[^"]*project-code[^\"]*"[^>]*>.*?</a>', '', updated, flags=re.S)
        row_html = (f'<div class="paper-resources" role="group" aria-label="Resources for {escape(title, quote=True)}">'
                    + ''.join(row) + '</div>') if row else ""
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
    research = open_conference_groups(research)
    teaching = element(home, "section", 'id="teaching"')
    teaching = re.sub(r'<h2\b[^>]*>Teaching</h2>', '', teaching, count=1)
    teaching = organize_teaching(lower_levels(teaching))
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
        <p class="institution">Virginia Tech</p>
        <div class="portrait-wrap"><img class="portrait" src="{classic}assets/profile.jpg" width="126" height="128" alt="Jamshid Ardalankia speaking at an event"></div>
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
