#!/usr/bin/env python3
"""Generate the static academic site from portable profile/publication data."""
import json
from html import escape
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parents[1]
profile = json.loads((ROOT / 'data/profile.json').read_text())
papers = sorted(json.loads((ROOT / 'data/publications.json').read_text()), key=lambda p: p['year'], reverse=True)
presentation = json.loads((ROOT / 'data/presentation.json').read_text())
for paper in papers:
    is_first = paper['authors'][0].rstrip('*') == profile['name']
    is_cofirst = profile['name'] + '*' in paper['authors']
    paper['selected'] = (is_first or is_cofirst) and bool({'CCF-A', 'THU-A'} & set(paper.get('classifications', [])))
selected_papers = [p for p in papers if p['selected']]
other_papers = [p for p in papers if not p['selected']]
template = Template((ROOT / 'templates/base.html').read_text())
by_id = {p['id']: p for p in papers}
e = escape
name = f'{e(profile["name"])} <span class="chinese-name" lang="zh">({e(profile["chinese_name"])})</span>'
groups = [('ai', 'Large Language Models (LLMs)'), ('network', 'Networking')]
count_note = f'{len(selected_papers)} papers published or accepted at CCF-A / THU-A venues as first or co-first author.'


def authors(paper):
    return ', '.join('<strong class="self-author">' + e(a) + '</strong>' if a.rstrip('*') == profile['name'] else e(a)
                     for a in paper['authors'])


def venue_label(paper):
    distinction = f' ({paper["distinction"]})' if paper.get('distinction') else ''
    return f'{paper["venue"]}, {paper["year"]}{distinction}'


def publication(paper):
    links = ''.join(f'<a href="{e(url, quote=True)}">[{e(label)}]</a>' for label, url in paper['links'].items())
    note = f'<p class="paper-note">{e(paper["note"])}</p>' if paper.get('note') else ''
    return f'''<article class="compact-publication" id="{paper['id']}">
      <h4><strong>[{e(paper['venue'])}]</strong> <a href="{e(paper['url'], quote=True)}">{e(paper['title'])}</a></h4>
      <p class="paper-authors">{authors(paper)}</p>
      <p class="venue">{e(venue_label(paper))}</p>
      <div class="paper-links">{links}</div>{note}
    </article>'''


def entries(key, kind=None):
    out = []
    for row in profile[key]:
        if kind and row.get('kind') != kind:
            continue
        detail = f'<p>{e(row["detail"])}</p>' if row.get('detail') else ''
        out.append(f'''<div class="entry"><p><strong>{e(row['organization'])}</strong>, {e(row['role'])}<br>
          <time>{e(row['dates'])}</time></p>{detail}</div>''')
    return ''.join(out)


def background(for_cv=False):
    awards = ''.join(f'<li><time>{e(a["year"])}</time>{e(a["title"])}</li>' for a in profile['awards'])
    service = ''.join(f'<li>{e(s)}</li>' for s in profile['service'])
    experience = (f'<section class="background-section" id="experience"><h2>Experience</h2>{entries("experience")}</section>' if for_cv else
                  f'<section class="background-section" id="teaching"><h2>Teaching</h2>{entries("experience", kind="teaching")}</section>')
    return f'''<section class="background-section" id="education"><h2>Education</h2>{entries('education')}</section>
    {experience}
    <section class="background-section" id="honors"><h2>Selected Honors</h2><ul class="award-list">{awards}</ul></section>
    <section class="background-section" id="service"><h2>Academic Service</h2><ul class="service-list">{service}</ul></section>'''


def render(file, title, content, page_class=''):
    page = template.substitute(
        title=e(title), description=e('Qilong Shi · Tsinghua University. Research in network measurement, data stream mining, and large language models.'),
        canonical=profile['site_url'] + (file if file != 'index.html' else ''),
        content=content, page_class=page_class,
        home_current=' aria-current="page"' if file == 'index.html' else '',
        publications_current=' aria-current="page"' if file == 'publications.html' else '')
    (ROOT / file).write_text(page)


# The reference homepage uses short research topics rather than full citations.
intro = f'''<header class="intro"><h1>{name}</h1>
  <div class="intro-copy"><p>{e(' '.join(profile['bio']))}</p></div>
  <p class="contact-links">Email: <a href="mailto:{e(profile['email'])}">{e(profile['email'])}</a><br>
    <span class="profile-links">[<a href="cv.html">Resume</a>] [<a href="{e(profile['scholar'])}">Google Scholar</a>] [<a href="{e(profile['github'])}">GitHub</a>]</span>
  </p></header><hr>'''
selected = ''
for domain, title in groups:
    items = []
    for paper in selected_papers:
        if paper['domain'] != domain:
            continue
        topic, short_name = presentation[paper['id']]
        items.append(f'<li id="{paper["id"]}">{e(topic)} [<a href="publications.html#{paper["id"]}">{e(short_name)}, {e(venue_label(paper))}</a>]</li>')
    selected += f'<section class="research-group" aria-labelledby="{domain}-heading"><h3 id="{domain}-heading">{title}</h3><ul class="research-list">{"".join(items)}</ul></section>'
content = intro + f'''<section id="research"><h2>Selected Publications</h2>
<p class="section-note">{count_note}</p>{selected}
<p class="more-link" id="more-publications">[<a href="publications.html">All publications</a>] [<a href="publications.html#more-publications">More publications</a>]</p>
</section><hr>''' + background()
render('index.html', 'Qilong Shi | 史奇龙', content)

highlights = []
for highlight in profile['highlights']:
    paper = by_id[highlight['id']]
    highlights.append(f'<li>{e(highlight["subtitle"])} [<a href="#{paper["id"]}">{e(highlight["title"])}, {e(venue_label(paper))}</a>]</li>')
full_selected = ''
for domain, title in groups:
    full_selected += f'<section class="publication-group"><h3>{title}</h3>' + ''.join(publication(p) for p in selected_papers if p['domain'] == domain) + '</section>'
publications = f'''<header class="publications-header"><h1>Publications</h1>
<p class="section-note">* Equal contribution. <a href="{e(profile['scholar'])}">Google Scholar</a></p></header>
<section id="highlights"><h2>Highlights</h2><ul class="highlights-list">{''.join(highlights)}</ul></section><hr>
<section id="selected-publications"><h2>Selected Publications</h2><p class="section-note">{count_note}</p>{full_selected}</section>
<hr><section id="more-publications"><h2>More Publications</h2>{''.join(publication(p) for p in other_papers)}</section>'''
render('publications.html', 'Publications · Qilong Shi', publications, 'publications-page')

cv = f'''<header class="cv-header">
<a class="portrait-link" href="assets/images/qilong-shi.jpg" aria-label="View photo of Qilong Shi"><img class="portrait" src="assets/images/qilong-shi.jpg" alt="Qilong Shi in graduation robes at a library" width="180" height="220"></a>
<h1>{name}</h1><p>Ph.D. candidate · Department of Computer Science · Tsinghua University</p>
<p><a href="mailto:{e(profile['email'])}">{e(profile['email'])}</a></p>
<p>[<a href="{e(profile['scholar'])}">Google Scholar</a>] [<a href="{e(profile['github'])}">GitHub</a>]</p>
<nav><a href="./">← Homepage</a> · Print this page to save a PDF</nav></header><hr>
<section><h2>Research Interests</h2><p>Sketch-based network measurement and data stream mining; efficient LLM reasoning, model merging, and supervised fine-tuning.</p></section>'''
cv += background(for_cv=True) + '<hr><section><h2>Publications &amp; Preprints</h2><p class="section-note">* Equal contribution.</p>' + ''.join(publication(p) for p in papers) + '</section>'
render('cv.html', 'CV · Qilong Shi', cv, 'cv')
render('404.html', 'Page not found · Qilong Shi', '<h1>Page not found</h1><p>This page may have moved. <a href="/">Return to the homepage</a>.</p>')
(ROOT / '.nojekyll').touch()
(ROOT / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: ' + profile['site_url'] + 'sitemap.xml\n')
(ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{profile["site_url"]}{page}</loc><lastmod>{profile["updated"]}</lastmod></url>' for page in ['', 'publications.html', 'cv.html']) + '</urlset>\n')
print(f'Built homepage, publications, CV and 404 page: {len(selected_papers)} selected + {len(other_papers)} more publications.')
