#!/usr/bin/env python3
"""Generate a dependency-free GitHub Pages site from portable profile data."""
import json
from html import escape
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parents[1]
profile = json.loads((ROOT / 'data/profile.json').read_text())
papers = sorted(json.loads((ROOT / 'data/publications.json').read_text()), key=lambda p: p['year'], reverse=True)
for paper in papers:
    is_first = paper['authors'][0].rstrip('*') == profile['name']
    is_cofirst = profile['name'] + '*' in paper['authors']
    paper['selected'] = (is_first or is_cofirst) and bool({'CCF-A', 'THU-A'} & set(paper.get('classifications', [])))
template = Template((ROOT / 'templates/base.html').read_text())
by_id = {p['id']: p for p in papers}
e = escape


def authors(paper):
    return ', '.join('<strong class="self-author">' + e(a) + '</strong>' if a.rstrip('*') == profile['name'] else e(a)
                     for a in paper['authors'])


def venue_label(paper):
    distinction = f' ({paper["distinction"]})' if paper.get('distinction') else ''
    return f'{paper["venue"]}, {paper["year"]}{distinction}'


def publication(paper, illustrated=False):
    links = ''.join(f'<a href="{e(url, quote=True)}">{e(label)}</a>' for label, url in paper['links'].items())
    content = f'''<h3><a href="{e(paper['url'], quote=True)}">{e(paper['title'])}</a></h3>
      <p class="paper-authors">{authors(paper)}</p>
      <p class="venue">{e(venue_label(paper))}</p>
      <div class="paper-links">{links}</div>'''
    if illustrated:
        content += f'<p class="paper-description">{e(paper["description"])}</p>'
    if paper.get('note'):
        content += f'<p class="paper-note">{e(paper["note"])}</p>'
    if illustrated and paper.get('image'):
        image = f'''<a class="paper-image" href="{e(paper['url'], quote=True)}" aria-label="Read {e(paper['title'], quote=True)}">
          <img src="{e(paper['image'], quote=True)}" alt="{e(paper.get('image_alt', paper['title'] + ' — paper figure'), quote=True)}" loading="lazy" width="{paper['image_width']}" height="{paper['image_height']}">
        </a>'''
        return f'<article class="publication" id="{paper["id"]}">{image}<div>{content}</div></article>'
    return f'<article class="compact-publication" id="{paper["id"]}">{content}</article>'


def entries(key, kind=None):
    out = []
    for row in profile[key]:
        if kind and row.get('kind') != kind:
            continue
        detail = f'<p class="detail">{e(row["detail"])}</p>' if row.get('detail') else ''
        out.append(f'''<div class="entry"><div><h3>{e(row['organization'])}</h3><p>{e(row['role'])}</p></div>
          <time>{e(row['dates'])}</time>{detail}</div>''')
    return ''.join(out)


def background(for_cv=False):
    awards = ''.join(f'<li><time>{e(a["year"])}</time>{e(a["title"])}</li>' for a in profile['awards'])
    service = ''.join(f'<li>{e(s)}</li>' for s in profile['service'])
    experience = (f'<section id="experience"><h2>Experience</h2>{entries("experience")}</section>' if for_cv else
                  f'<section id="teaching"><h2>Teaching</h2>{entries("experience", kind="teaching")}</section>')
    return f'''<section id="education"><h2>Education</h2>{entries('education')}</section>
    {experience}
    <section id="honors"><h2>Selected Honors</h2><ul class="award-list">{awards}</ul></section>
    <section id="service"><h2>Academic Service</h2><ul class="service-list">{service}</ul></section>'''


def render(file, title, content, page_class=''):
    page = template.substitute(title=e(title), description=e('Qilong Shi · Tsinghua University. Research in network measurement, data stream mining, and large language models.'),
        canonical=profile['site_url'] + (file if file != 'index.html' else ''), content=content, page_class=page_class)
    (ROOT / file).write_text(page)


bio = ''.join('<p>' + e(p) + '</p>' for p in profile['bio'])
highlights = []
for h in profile['highlights']:
    paper = by_id[h['id']]
    img = f'<img src="{e(paper["image"], quote=True)}" alt="" width="320" height="224" loading="lazy">' if paper.get('image') else ''
    highlights.append(f'<a class="highlight" href="#{paper["id"]}">{img}<strong>{e(h["title"])}</strong><span>{e(venue_label(paper))}</span><span>{e(h["subtitle"])}</span></a>')
selected_papers = [p for p in papers if p['selected']]
selected = ''
for domain, title in [('network', 'Networking'), ('ai', 'Large Language Models (LLMs)')]:
    group = ''.join(publication(p, illustrated=True) for p in selected_papers if p['domain'] == domain)
    selected += f'<section class="publication-group" aria-labelledby="{domain}-heading"><h2 id="{domain}-heading">{title}</h2>{group}</section>'
other = ''.join(publication(p) for p in papers if not p['selected'])
intro = f'''<header class="intro">
  <div class="intro-copy"><h1>{e(profile['name'])} <span class="chinese-name" lang="zh">{e(profile['chinese_name'])}</span></h1>
    {bio}
    <nav class="contact-links" aria-label="Contact and profiles">
      <a href="mailto:{e(profile['email'])}">Email</a><a href="cv.html">CV</a>
      <a href="{e(profile['scholar'])}">Google Scholar</a><a href="{e(profile['github'])}">GitHub</a>
    </nav>
  </div>
  <a class="portrait-link" href="assets/images/qilong-shi.jpg" aria-label="View photo of Qilong Shi">
    <img class="portrait" src="assets/images/qilong-shi.jpg" alt="Qilong Shi in graduation robes at a library" width="260" height="320" fetchpriority="high">
  </a>
</header>
<nav class="section-nav" aria-label="On this page"><a href="#research">Publications</a><a href="#more-publications">More Publications</a><a href="#education">Education</a><a href="#teaching">Teaching</a><a href="#service">Service</a></nav>'''
content = intro + f'''<section aria-labelledby="highlights-heading"><h2 id="highlights-heading">Highlights</h2><div class="highlights">{''.join(highlights)}</div></section>
<section id="research"><h2>Selected Publications</h2><p class="section-note">{len(selected_papers)} papers published or accepted at CCF-A / THU-A venues as first or co-first author.<br>* Equal contribution.</p>{selected}</section>
<section id="more-publications"><h2>More Publications</h2>{other}</section>''' + background()
render('index.html', 'Qilong Shi | 史奇龙', content)
cv = f'''<header class="cv-header"><nav><a href="./">← Homepage</a> · Print this page to save a PDF</nav>
<h1>{e(profile['name'])} <span class="chinese-name" lang="zh">{e(profile['chinese_name'])}</span></h1>
<p>Ph.D. candidate · Department of Computer Science · Tsinghua University</p>
<p><a href="mailto:{e(profile['email'])}">{e(profile['email'])}</a> · <a href="{e(profile['scholar'])}">Google Scholar</a> · <a href="{e(profile['github'])}">GitHub</a></p></header>
<section><h2>Research Interests</h2><p>Sketch-based network measurement and data stream mining; efficient LLM reasoning, model merging, and supervised fine-tuning.</p></section>'''
cv += background(for_cv=True) + '<section><h2>Publications &amp; Preprints</h2><p class="section-note">* Equal contribution.</p>' + ''.join(publication(p) for p in papers) + '</section>'
render('cv.html', 'CV · Qilong Shi', cv, 'cv')
render('404.html', 'Page not found · Qilong Shi', '<h1>Page not found</h1><p>This page may have moved. <a href="/">Return to the homepage</a>.</p>')
(ROOT / '.nojekyll').touch()
(ROOT / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: ' + profile['site_url'] + 'sitemap.xml\n')
(ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{profile["site_url"]}{page}</loc><lastmod>{profile["updated"]}</lastmod></url>' for page in ['', 'cv.html']) + '</urlset>\n')
print(f'Built homepage, CV and 404 page with {len(papers)} publications.')
