#!/usr/bin/env python3
"""Generate the static academic site from portable profile/publication data."""
import json
import re
from html import escape
from pathlib import Path
from string import Template

from update_scholar_stats import get_scholar_id, validate_snapshot

ROOT = Path(__file__).resolve().parents[1]
profile = json.loads((ROOT / 'data/profile.json').read_text())
papers = sorted(json.loads((ROOT / 'data/publications.json').read_text()), key=lambda p: p['year'], reverse=True)
presentation = json.loads((ROOT / 'data/presentation.json').read_text())
visitors = json.loads((ROOT / 'data/visitors.json').read_text())
scholar_config = json.loads((ROOT / 'data/scholar.json').read_text())
for paper in papers:
    is_first = paper['authors'][0].rstrip('*') == profile['name']
    is_cofirst = profile['name'] + '*' in paper['authors']
    paper['selected'] = paper.get('selected_override', False) or ((is_first or is_cofirst) and bool({'CCF-A', 'THU-A'} & set(paper.get('classifications', []))))
selected_papers = [p for p in papers if p['selected']]
other_papers = [p for p in papers if not p['selected']]
template = Template((ROOT / 'templates/base.html').read_text())
by_id = {p['id']: p for p in papers}
e = escape
name = f'{e(profile["name"])} <span class="chinese-name" lang="zh">({e(profile["chinese_name"])})</span>'
count_note = f'{len(selected_papers)} selected papers at CCF-A / THU-A venues.'


def visitor_globe():
    if not visitors['enabled']:
        return ''
    if visitors['provider'] != 'RevolverMaps2' or not re.fullmatch(r'[a-z0-9]{12}', visitors['site_key']):
        raise ValueError('Use the RevolverMaps2 site key issued for this website.')
    size = int(visitors['size'])
    if not 150 <= size <= 400:
        raise ValueError('Keep the visitor globe between 150 and 400 pixels wide.')
    if not re.fullmatch(r'[a-z0-9-]{1,24}', visitors['theme']) or not re.fullmatch(r'[0-9a-fA-F]{6}', visitors['marker_color']):
        raise ValueError('Use a valid globe theme and six-digit marker color.')
    return f'''<section class="visitors-section" id="visitors" aria-label="Worldwide visitors">
<div class="visitor-globe" style="width: {size}px">
<script src="https://revolvermaps2.com/embed.js" data-site="{visitors['site_key']}" data-size="{size}" data-theme="{visitors['theme']}" data-color="{visitors['marker_color']}" async></script>
</div>
<p class="visitor-total" aria-live="polite" aria-atomic="true">Total visitors: <span id="visitor-total" data-site="{visitors['site_key']}">—</span></p>
<script src="assets/visitors.js?v=20261107-total" defer></script>
</section>'''


def scholar_statistics():
    if not scholar_config['enabled']:
        return ''
    scholar_id = get_scholar_id(profile)
    snapshot = validate_snapshot(json.loads((ROOT / 'data/scholar-stats.json').read_text()), scholar_id)
    metrics = []
    for key, label in [('citations', 'Citations'), ('h_index', 'h-index'), ('i10_index', 'i10-index')]:
        value = format(snapshot['metrics'][key], ',')
        metrics.append(f'<a class="scholar-stat" href="{e(profile["scholar"], quote=True)}"><span class="scholar-label"><img src="assets/images/google-scholar.svg" alt="" width="14" height="14">{label}</span><span class="scholar-value" data-metric="{key}">{value}</span></a>')
    return f''' <span class="scholar-metrics" id="scholar-metrics" role="group" aria-label="Google Scholar statistics" aria-live="polite" aria-atomic="true" data-scholar-id="{e(scholar_id)}" data-fetched-at="{e(snapshot['fetched_at'])}" data-snapshot-url="{e(scholar_config['snapshot_url'], quote=True)}">{' '.join(metrics)}</span>'''


def authors(paper):
    return ', '.join('<strong class="self-author">' + e(a) + '</strong>' if a.rstrip('*') == profile['name'] else e(a)
                     for a in paper['authors'])


def venue_label(paper, short_year=False):
    abbreviations = {'IEEE TKDE': 'TKDE', 'IEEE/ACM ToN': 'ToN',
                     'IEEE TPDS': 'TPDS', 'arXiv preprint': 'arXiv'}
    venue = abbreviations.get(paper['venue'], paper['venue'])
    return f"{venue}'{paper['year'] % 100:02d}" if short_year else f"{venue} {paper['year']}"


def publication(paper):
    pdf = paper.get('pdf')
    if pdf:
        if not (ROOT / pdf).is_file():
            raise FileNotFoundError(f'Missing PDF for {paper["id"]}: {pdf}')
        title = f'<a href="{e(pdf, quote=True)}">{e(paper["title"])}</a>'
    else:
        title = e(paper['title'])
    links = ''.join(f'<a href="{e(url, quote=True)}">[{e(label)}]</a>' for label, url in paper['links'].items() if label not in ('Paper', 'PDF'))
    resources = f'<div class="paper-links">{links}</div>' if links else ''
    note = f'<p class="paper-note">{e(paper["note"])}</p>' if paper.get('note') else ''
    return f'''<article class="compact-publication" id="{paper['id']}">
      <h4><strong>[{e(venue_label(paper))}]</strong> {title}</h4>
      <p class="paper-authors">{authors(paper)}</p>
{resources}{note}
    </article>'''


def entries(key, kind=None):
    out = []
    for row in profile[key]:
        if kind and row.get('kind') != kind:
            continue
        detail = f'<p>{e(row["detail"])}</p>' if row.get('detail') else ''
        separator = '<br>' if key == 'education' else ', '
        out.append(f'''<div class="entry"><p><strong>{e(row['organization'])}</strong>{separator}{e(row['role'])}<br>
          <time>{e(row['dates'])}</time></p>{detail}</div>''')
    return ''.join(out)


def award(row):
    title = e(row['title'])
    if row.get('url'):
        title = f'<a href="{e(row["url"], quote=True)}">{title}</a>'
    note = f' ({e(row["note"])})' if row.get('note') else ''
    return f'<li><time>{e(row["year"])}</time>{title}{note}</li>'


def background(for_cv=False):
    awards = ''.join(award(a) for a in profile['awards'] if not for_cv or a.get('show_in_cv', True))
    service = profile['service']
    committee = ''.join(f'<li>Program Committee, {e(s)}</li>' for s in service['program_committee'])
    reviewing = ''.join(
        f'<section aria-labelledby="{key}-heading"><h3 id="{key}-heading">{title}</h3>'
        f'<ul class="service-list">{"".join(f"<li>{e(s)}</li>" for s in service[key])}</ul></section>'
        for key, title in [('conference_reviewing', 'Conference Reviewer'), ('journal_reviewing', 'Journal Reviewer')]
    )
    experience = f'<section class="overview-card" id="teaching"><h2>Teaching</h2>{entries("experience", kind="teaching")}</section>'
    return f'''<section class="overview-card" id="education"><h2>Education</h2>{entries('education')}</section>
    {experience}
    <section class="overview-card" id="honors"><h2>Selected Honors</h2><ul class="award-list">{awards}</ul></section>
    <section class="overview-card" id="service"><h2>Academic Service</h2><ul class="service-list">{committee}</ul><div class="service-columns">{reviewing}</div></section>'''


def render(file, title, content, page_class=''):
    page = template.substitute(
        title=e(title), description=e('Qilong Shi · Tsinghua University. Research in network measurement, data stream mining, and large language models.'),
        canonical=profile['site_url'] + (file if file != 'index.html' else ''),
        content=content, page_class=page_class,
        footer='' if file == 'index.html' else '<footer><p>© 2026 Qilong Shi · Updated November 2026</p><p>Style inspired by <a href="https://yindazhang.github.io/">Yinda Zhang</a> · <a href="https://github.com/stallone0000/stallone0000.github.io">Source</a></p></footer>',
        home_current=' aria-current="page"' if file == 'index.html' else '',
        cv_current=' aria-current="page"' if file == 'cv.html' else '')
    (ROOT / file).write_text(page)


# The reference homepage uses short research topics rather than full citations.
bio = e(' '.join(profile['bio']))
for label, url in profile.get('bio_links', {}).items():
    bio = bio.replace(e(label), f'<a href="{e(url, quote=True)}">{e(label)}</a>')
intro = f'''<header class="intro{' has-globe' if visitors['enabled'] else ''}" style="--visitor-size: {int(visitors['size'])}px"><div class="intro-heading"><h1>{name}</h1>
  <img class="university-logo" src="assets/images/tsinghua-university.svg" alt="Tsinghua University" width="151" height="48"><img class="university-logo" src="assets/images/peking-university.svg" alt="Peking University" width="171" height="48"></div>
  <div class="intro-layout{' with-globe' if visitors['enabled'] else ''}"><div class="intro-copy"><p>{bio}</p></div>{visitor_globe()}</div>
  <p class="contact-links">Email: <a href="mailto:{e(profile['email'])}">{e(profile['email'])}</a><br>
    <span class="profile-links">[<a href="cv.html">Full CV</a>] [<a href="{e(profile['scholar'])}">Google Scholar</a>]{scholar_statistics()}</span>
  </p>{'<script src="assets/scholar.js?v=20261108-badges" defer></script>' if scholar_config['enabled'] else ''}</header><hr>'''
selected = ''
for group in presentation['groups']:
    items = []
    for topic in group['topics']:
        citations = []
        for paper in sorted((by_id[pid] for pid in topic['papers']), key=lambda p: p['year'], reverse=True):
            short_name = presentation['short_names'][paper['id']]
            label = short_name if paper['id'] in presentation.get('hide_venue', []) else f'{short_name}, {venue_label(paper, short_year=True)}'
            override = topic.get('citation_overrides', {}).get(paper['id'], {})
            label = override.get('label', label)
            citation_id = override.get('id', paper['id'])
            citations.append(f'<span class="paper-citation" id="{e(citation_id, quote=True)}">[<a href="cv.html#{paper["id"]}">{e(label)}</a>]</span>')
        links = ' '.join(f'[<a href="{e(url, quote=True)}">{e(label)}</a>]' for label, url in topic.get('links', {}).items())
        items.append(f'<li>{e(topic["label"])} {" ".join(citations)}{(" " + links) if links else ""}</li>')
    selected += f'<section class="research-group" aria-labelledby="{group["id"]}-heading"><h3 id="{group["id"]}-heading">{e(group["title"])}</h3><ul class="research-list">{"".join(items)}</ul></section>'
content = intro + f'<section id="research"><h2>Selected Publications</h2>{selected}</section><hr>'
render('index.html', 'Qilong Shi | 史奇龙', content)

full_selected = ''.join(publication(p) for p in selected_papers)
publication_sections = f'''<section id="publications"><h2>Publications</h2>
<p class="section-note">* Equal contribution.</p>
<section id="selected-publications"><h2>Selected Publications</h2><p class="section-note">{count_note}</p>{full_selected}</section>
<hr><section id="more-publications"><h2>More Publications</h2>{''.join(publication(p) for p in other_papers)}</section></section>'''

cv = f'''<header class="cv-header">
<a class="portrait-link" href="assets/images/qilong-shi.jpg" aria-label="View photo of Qilong Shi"><img class="portrait" src="assets/images/qilong-shi.jpg" alt="Qilong Shi in graduation robes at a library" width="160" height="196"></a>
<h1>{name}</h1><p>Ph.D. candidate · Department of Computer Science · Tsinghua University</p>
<p><a href="mailto:{e(profile['email'])}">{e(profile['email'])}</a></p>
<p>[<a href="{e(profile['scholar'])}">Google Scholar</a>]{scholar_statistics()}</p>
<nav><a href="./">← Homepage</a></nav>{'<script src="assets/scholar.js?v=20261108-badges" defer></script>' if scholar_config['enabled'] else ''}</header><hr>
<div class="cv-overview"><section class="overview-card" id="research-interests"><h2>Research Interests</h2><p>Sketch-based network measurement and data stream mining; efficient LLM reasoning, model merging, and supervised fine-tuning.</p></section>'''
cv += background(for_cv=True) + '</div><hr>' + publication_sections
render('cv.html', 'Full CV · Qilong Shi', cv, 'cv publications-page')
# Preserve old publication deep links without keeping a duplicate content page.
(ROOT / 'publications.html').write_text('''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Full CV · Qilong Shi</title><link rel="canonical" href="https://stallone0000.github.io/cv.html">
<meta name="robots" content="noindex"><script src="assets/publications-redirect.js"></script>
<noscript><meta http-equiv="refresh" content="0; url=cv.html"></noscript></head>
<body><p><a href="cv.html">Continue to the full CV</a>.</p></body></html>''')
render('404.html', 'Page not found · Qilong Shi', '<h1>Page not found</h1><p>This page may have moved. <a href="/">Return to the homepage</a>.</p>')
(ROOT / '.nojekyll').touch()
(ROOT / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: ' + profile['site_url'] + 'sitemap.xml\n')
(ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{profile["site_url"]}{page}</loc><lastmod>{profile["updated"]}</lastmod></url>' for page in ['', 'cv.html']) + '</urlset>\n')
print(f'Built homepage, Full CV, legacy redirect and 404 page: {len(selected_papers)} selected + {len(other_papers)} more publications.')
