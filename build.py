#!/usr/bin/env python3
"""Build paolopecere.it: content/*.json -> public/**/*.html

    python3 build.py            build the site into public/
    python3 build.py --check    only validate the content, write nothing
    python3 build.py --serve    build, then preview at http://localhost:8000
    python3 build.py --local --out DIR
                                build a copy that opens straight from disk
                                (double-click index.html), for offline previews

Needs only the Python standard library (3.8+). See CLAUDE.md for how the
content files are organised.
"""
import argparse
import datetime as dt
import hashlib
import html
import json
import re
import shutil
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / 'content'
PUBLIC = ROOT / 'public'
LANGS = ['en', 'it']          # the first one lives at the site root, the others under /<lang>/
HTML_LANG = {'en': 'en', 'it': 'it'}

# page key -> path inside a language (always ends with "/" except the home page)
PAGES = {
    'home': '',
    'books': 'books/',
    'books-research': 'books/research/',
    'books-fiction': 'books/fiction-and-narrative-non-fiction/',
    'books-textbooks': 'books/textbooks/',
    'papers': 'papers/',
    'essays': 'essays-and-journalism/',
    'stories': 'short-stories-and-travelogues/',
    'events': 'events/',
    'media': 'media/',
    'about': 'about/',
    'privacy': 'privacy/',
}
NAV = ['books', 'papers', 'essays', 'stories', 'events', 'media', 'about']
OLD_URLS = {  # addresses of the previous (Jimdo) site that no longer exist
    '/informazioni-legali/': '/privacy/',
    '/dichiarazione-privacy/': '/privacy/',
    '/impostazioni-dei-cookie/': '/privacy/',
    '/recesso/': '/',
}

MONTHS = {
    'en': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
    'it': ['gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno', 'luglio', 'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre'],
}
WEEKDAYS = {
    'en': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
    'it': ['lunedì', 'martedì', 'mercoledì', 'giovedì', 'venerdì', 'sabato', 'domenica'],
}

ICONS = {
    'download': '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 1.5v8.2M4.4 6.6 8 10.2l3.6-3.6M2.5 13.5h11" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    'video': '<svg class="entry__icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10.2" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M10 8.2v7.6l6-3.8z" fill="currentColor"/></svg>',
    'podcast': '<svg class="entry__icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 10v4M8 6.5v11M12 3.5v17M16 6.5v11M20 10v4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
}


# --------------------------------------------------------------------------- helpers
def load(name):
    with open(CONTENT / f'{name}.json', encoding='utf-8') as fh:
        return json.load(fh)


def e(text):
    return html.escape(str(text), quote=True)


def image_size(path):
    """Width and height of a JPEG or PNG, without external libraries."""
    with open(path, 'rb') as fh:
        head = fh.read(26)
        if head[:8] == b'\x89PNG\r\n\x1a\n':
            return struct.unpack('>II', head[16:24])
        if head[:2] == b'\xff\xd8':
            fh.seek(2)
            while True:
                marker = fh.read(2)
                if len(marker) < 2:
                    break
                while marker[1] == 0xFF:
                    marker = bytes([0xFF]) + fh.read(1)
                code = marker[1]
                if code in (0xD8, 0x01) or 0xD0 <= code <= 0xD7:
                    continue
                size = struct.unpack('>H', fh.read(2))[0]
                if code in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                    data = fh.read(5)
                    height, width = struct.unpack('>HH', data[1:5])
                    return width, height
                fh.seek(size - 2, 1)
    return None


class Site:
    def __init__(self, out, local=False, today=None):
        self.out = out
        self.local = local
        self.today = today or dt.date.today()
        self.site = load('site')
        self.strings = load('i18n')
        self.books = load('books')
        self.papers = load('papers')
        self.essays = load('essays')
        self.stories = load('stories')
        self.media = load('media')
        self.events = load('events')
        self.errors = []
        css = PUBLIC / 'assets' / 'css' / 'site.css'
        js = PUBLIC / 'assets' / 'js' / 'site.js'
        self.version = hashlib.sha1(css.read_bytes() + js.read_bytes()).hexdigest()[:8]

    # ----------------------------------------------------------------- checks
    def asset_exists(self, rel, where):
        if not (PUBLIC / 'assets' / rel).is_file():
            self.errors.append(f'{where}: missing file public/assets/{rel}')
            return False
        return True

    def validate(self):
        ids = set()
        cats = {c['id'] for c in self.books['categories']}
        for b in self.books['books']:
            where = f'books.json "{b.get("title", "?")}"'
            for key in ('id', 'category', 'title'):
                if not b.get(key):
                    self.errors.append(f'{where}: "{key}" is required')
            if b.get('id') in ids:
                self.errors.append(f'{where}: id "{b["id"]}" is used twice')
            ids.add(b.get('id'))
            if b.get('category') not in cats:
                self.errors.append(f'{where}: unknown category "{b.get("category")}"')
            if b.get('cover'):
                self.asset_exists(b['cover'], where)
            for f in b.get('downloads', []):
                self.asset_exists(f, where)
        for rid in self.books.get('recent', []):
            if rid not in ids:
                self.errors.append(f'books.json "recent": no book with id "{rid}"')

        def check_links(item, where):
            for key in ('url', 'outlet_url'):
                u = item.get(key)
                if u and u.startswith('files/'):
                    self.asset_exists(u, where)
            for l in item.get('links', []) + item.get('parts', []):
                if not l.get('url'):
                    self.errors.append(f'{where}: a link has no "url"')
                elif l['url'].startswith('files/'):
                    self.asset_exists(l['url'], where)

        for s in self.papers['sections']:
            for it in s['items']:
                if not it.get('title'):
                    self.errors.append(f'papers.json section "{s["id"]}": an item has no title')
                check_links(it, f'papers.json "{it.get("title", "?")[:50]}"')
        for it in self.essays['items']:
            if not it.get('title'):
                self.errors.append('essays.json: an item has no title')
            check_links(it, f'essays.json "{it.get("title", "?")[:50]}"')
        for name, data in (('stories.json', self.stories), ('media.json', self.media)):
            for s in data['sections']:
                for it in s['items']:
                    if not it.get('title'):
                        self.errors.append(f'{name} section "{s["id"]}": an item has no title')
                    check_links(it, f'{name} "{it.get("title", "?")[:50]}"')
        for ev in self.events.get('events', []):
            where = f'events.json "{self.pick(ev.get("title"), "it") or "?"}"'
            if not ev.get('title'):
                self.errors.append('events.json: an event has no title')
            for key in ('date', 'end_date'):
                if key == 'end_date' and not ev.get(key):
                    continue
                try:
                    dt.date.fromisoformat(str(ev.get(key)))
                except ValueError:
                    self.errors.append(f'{where}: "{key}" must look like 2027-01-31')
            if ev.get('time') and not re.match(r'^\d{1,2}:\d{2}$', str(ev['time'])):
                self.errors.append(f'{where}: "time" must look like 18:30')
        for key, ph in self.site['photos'].items():
            if key.startswith('_'):
                continue
            self.asset_exists('img/photos/' + ph['src'], f'site.json photos.{key}')
        if self.site.get('portrait'):
            self.asset_exists(self.site['portrait'], 'site.json portrait')
        for c in self.site['contacts']:
            if c.get('url', '').startswith('files/'):
                self.asset_exists(c['url'], 'site.json contacts')
        return not self.errors

    # ----------------------------------------------------------------- language helpers
    @staticmethod
    def pick(value, lang):
        """A value is either plain text (same in every language) or {"en": ..., "it": ...}."""
        if isinstance(value, dict):
            return value.get(lang) or value.get(LANGS[0]) or next(iter(value.values()), '')
        return value or ''

    def t(self, key, lang, **kw):
        if key not in self.strings:
            raise KeyError(f'i18n.json has no entry "{key}"')
        text = self.pick(self.strings[key], lang)
        for k, v in kw.items():
            text = text.replace('{' + k + '}', str(v))
        return text

    # ----------------------------------------------------------------- output
    def write(self, rel_path, text):
        target = self.out / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8', newline='\n')

    def build(self):
        if self.out != PUBLIC:
            self.out.mkdir(parents=True, exist_ok=True)
            if (self.out / 'assets').exists():
                shutil.rmtree(self.out / 'assets')
            shutil.copytree(PUBLIC / 'assets', self.out / 'assets')
        for old in list(self.out.rglob('*.html')):
            if 'assets' not in old.relative_to(self.out).parts:
                old.unlink()
        count = 0
        for lang in LANGS:
            for key in PAGES:
                page = Page(self, lang, key)
                self.write(page.file, page.render())
                count += 1
        self.write('404.html', Page(self, LANGS[0], '404').render())
        self.write('sitemap.xml', self.sitemap())
        self.write('robots.txt', f'User-agent: *\nAllow: /\n\nSitemap: {self.site["base_url"]}/sitemap.xml\n')
        self.write('_redirects', ''.join(f'{old} {new} 301\n' for old, new in OLD_URLS.items()))
        for d in sorted((p for p in self.out.rglob('*') if p.is_dir()), reverse=True):
            if not any(d.iterdir()):
                d.rmdir()
        return count + 1

    def sitemap(self):
        base = self.site['base_url']
        rows = []
        for key, path in PAGES.items():
            for lang in LANGS:
                loc = f'{base}/{lang_prefix(lang)}{path}'
                alts = ''.join(f'<xhtml:link rel="alternate" hreflang="{HTML_LANG[l]}" href="{base}/{lang_prefix(l)}{path}"/>' for l in LANGS)
                rows.append(f'  <url><loc>{loc}</loc>{alts}</url>')
        return ('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
                + '\n'.join(rows) + '\n</urlset>\n')


def lang_prefix(lang):
    return '' if lang == LANGS[0] else f'{lang}/'


def by_year(items):
    """Newest first; items of the same year keep the order they have in the file."""
    return sorted(items, key=lambda it: -(it.get('year') or 0))


# --------------------------------------------------------------------------- pages
class Page:
    def __init__(self, site, lang, key):
        self.s = site
        self.lang = lang
        self.key = key
        self.absolute = key == '404'            # the 404 page is served from any address
        self.dir = '' if key == '404' else lang_prefix(lang) + PAGES[key]
        self.file = '404.html' if key == '404' else self.dir + 'index.html'

    # --- addresses
    def _rel(self, target):
        if self.absolute:
            return '/' + target
        return '../' * self.dir.count('/') + target

    def url(self, key, lang=None, anchor=''):
        target = lang_prefix(lang or self.lang) + PAGES[key]
        if self.s.local:
            target += 'index.html'
        href = self._rel(target) or './'
        return href + (f'#{anchor}' if anchor else '')

    def asset(self, rel):
        return self._rel('assets/' + rel)

    def href(self, url):
        """Links in the content: 'files/...' are documents stored on this site."""
        return self.asset(url) if url.startswith('files/') else url

    def t(self, key, **kw):
        return self.s.t(key, self.lang, **kw)

    def pick(self, value):
        return self.s.pick(value, self.lang)

    # --- shared pieces
    def photo(self):
        photos = self.s.site['photos']
        base = self.key.split('-')[0]
        return photos.get(self.key) or photos.get(base) or photos['default']

    def img(self, rel, alt='', cls='', lazy=True, extra=''):
        size = image_size(PUBLIC / 'assets' / rel)
        dims = f' width="{size[0]}" height="{size[1]}"' if size else ''
        loading = ' loading="lazy" decoding="async"' if lazy else ''
        klass = f' class="{cls}"' if cls else ''
        return f'<img src="{e(self.asset(rel))}" alt="{e(alt)}"{dims}{loading}{klass}{extra}>'

    def head(self, title, description):
        s = self.s
        base = s.site['base_url']
        full = title if self.key == 'home' else f'{title} | {s.site["name"]}'
        out = [
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            f'<title>{e(full)}</title>',
            f'<meta name="description" content="{e(description)}">',
        ]
        if self.key == '404':
            out.append('<meta name="robots" content="noindex">')
        else:
            path = PAGES[self.key]
            out.append(f'<link rel="canonical" href="{base}/{lang_prefix(self.lang)}{path}">')
            for l in LANGS:
                out.append(f'<link rel="alternate" hreflang="{HTML_LANG[l]}" href="{base}/{lang_prefix(l)}{path}">')
            out.append(f'<link rel="alternate" hreflang="x-default" href="{base}/{path}">')
            og_img = f'{base}/assets/img/photos/{self.photo()["src"].replace(".jpg", "-sm.jpg")}'
            out += [
                '<meta property="og:type" content="website">',
                f'<meta property="og:site_name" content="{e(s.site["name"])}">',
                f'<meta property="og:title" content="{e(full)}">',
                f'<meta property="og:description" content="{e(description)}">',
                f'<meta property="og:url" content="{base}/{lang_prefix(self.lang)}{path}">',
                f'<meta property="og:image" content="{og_img}">',
                '<meta name="twitter:card" content="summary_large_image">',
            ]
        out += [
            f'<link rel="preload" href="{self.asset("fonts/bricolage-grotesque-latin.woff2")}" as="font" type="font/woff2" crossorigin>',
            f'<link rel="preload" href="{self.asset("fonts/newsreader-latin.woff2")}" as="font" type="font/woff2" crossorigin>',
            f'<link rel="stylesheet" href="{self.asset("css/site.css")}?v={s.version}">',
            f'<link rel="icon" href="{self.asset("img/favicon.svg")}" type="image/svg+xml">',
            '<script>document.documentElement.classList.add("js")</script>',
        ]
        stats = s.site.get('analytics') or {}
        if stats.get('goatcounter') and not s.local:
            # GoatCounter (no cookies). Visits count only on the addresses in "count_on",
            # so branch previews and local copies leave the statistics alone.
            hosts = json.dumps(stats.get('count_on', []))
            out += [
                f'<script>window.goatcounter={{no_onload:{hosts}.indexOf(location.hostname)<0}}</script>',
                f'<script data-goatcounter="{e(stats["goatcounter"])}" async src="https://gc.zgo.at/count.js"></script>',
            ]
        if self.key in ('home', 'about'):
            person = {
                '@context': 'https://schema.org', '@type': 'Person', 'name': s.site['name'], 'url': base + '/',
                'jobTitle': self.pick(s.site['role']), 'image': f'{base}/assets/{s.site["portrait"]}',
                'affiliation': {'@type': 'CollegeOrUniversity', 'name': 'Università degli Studi Roma Tre'},
                'sameAs': [x['url'] for x in s.site['social']],
            }
            out.append('<script type="application/ld+json">' + json.dumps(person, ensure_ascii=False) + '</script>')
        return '\n'.join(out)

    def header(self):
        current = self.key.split('-')[0]
        links = []
        for key in NAV:
            cur = ' aria-current="page"' if key == self.key else (' aria-current="true"' if key == current else '')
            links.append(f'<li><a class="nav__link" href="{self.url(key)}"{cur}>{e(self.t("nav." + key))}</a></li>')
        langs = []
        for l in LANGS:
            if l == self.lang:
                langs.append(f'<span class="lang__item" aria-current="true">{l.upper()}</span>')
            else:
                target = self.url(self.key if self.key != '404' else 'home', l)
                label = self.t('lang.switch')
                langs.append(f'<a class="lang__item" href="{target}" lang="{HTML_LANG[l]}" hreflang="{HTML_LANG[l]}" aria-label="{e(label)}">{l.upper()}</a>')
        return f'''<a class="skip" href="#content">{e(self.t('nav.skip'))}</a>
<header class="site-header">
<div class="wrap site-header__bar">
<a class="site-header__name" href="{self.url('home')}">{e(self.s.site['name'])}</a>
<nav class="nav" id="nav" aria-label="{e(self.t('nav.label'))}"><ul class="nav__list">{''.join(links)}</ul></nav>
<div class="lang" role="group" aria-label="{e(self.t('lang.label'))}">{''.join(langs)}</div>
<button class="menu-toggle" type="button" aria-expanded="false" aria-controls="nav" data-open="{e(self.t('nav.menu'))}" data-close="{e(self.t('nav.close'))}">{e(self.t('nav.menu'))}</button>
</div>
</header>'''

    def masthead(self, title):
        ph = self.photo()
        src = 'img/photos/' + ph['src']
        small = src.replace('.jpg', '-sm.jpg')
        srcset = ''
        if (PUBLIC / 'assets' / small).is_file():
            w_small = image_size(PUBLIC / 'assets' / small)[0]
            w_full = image_size(PUBLIC / 'assets' / src)[0]
            if w_full > w_small:
                srcset = f' srcset="{e(self.asset(small))} {w_small}w, {e(self.asset(src))} {w_full}w" sizes="100vw"'
        focus = f' style="object-position:{e(ph.get("focus", "50% 50%"))}"'
        image = self.img(src, lazy=False, extra=srcset + focus + ' fetchpriority="high"')
        caption = self.pick(ph.get('caption'))
        cap = f'<p class="masthead__caption">{e(caption)}</p>' if caption else ''
        home = ' masthead--home' if self.key == 'home' else ''
        return f'''<div class="masthead{home}">
<div class="masthead__photo">{image}{cap}</div>
<div class="masthead__tab"><h1 class="masthead__title">{e(title)}</h1></div>
</div>'''

    def footer(self):
        s = self.s.site
        contacts = ''.join(f'<li><a href="{e(self.href(c["url"]))}">{e(self.pick(c["text"]))}</a></li>' for c in s['contacts'][:3])
        sections = ''.join(f'<li><a href="{self.url(k)}">{e(self.t("title." + k))}</a></li>' for k in NAV)
        social = ''.join(f'<li><a href="{e(x["url"])}" rel="me">{e(x["name"])}</a></li>' for x in s['social'])
        return f'''<footer class="site-footer">
<div class="wrap">
<p class="site-footer__name">{e(s['name'])}</p>
<p class="site-footer__role">{e(self.pick(s['role']))}</p>
<div class="site-footer__grid">
<div><h2>{e(self.t('footer.contact'))}</h2><ul>{contacts}</ul></div>
<div><h2>{e(self.t('footer.sections'))}</h2><ul>{sections}</ul></div>
<div><h2>{e(self.t('footer.follow'))}</h2><ul>{social}</ul></div>
</div>
<div class="site-footer__base"><span>© {self.s.today.year} {e(s['name'])}</span><a href="{self.url('privacy')}">{e(self.t('footer.privacy'))}</a></div>
</div>
</footer>'''

    def render(self):
        builder = getattr(self, 'page_' + self.key.replace('-', '_').replace('404', 'notfound'), None)
        if self.key.startswith('books-'):
            builder = self.page_books_category
        title, description, body = builder()
        return f'''<!doctype html>
<html lang="{HTML_LANG[self.lang]}">
<head>
{self.head(title, description)}
</head>
<body class="page-{self.key}">
{self.header()}
{self.masthead(self.s.site['name'] if self.key == 'home' else title)}
<main id="content">
{body}
</main>
{self.footer()}
<script src="{self.asset('js/site.js')}?v={self.s.version}" defer></script>
</body>
</html>
'''

    # --- small renderers
    def chip(self, label, url, download=False):
        icon = ICONS['download'] if download else ''
        return f'<a class="chip" href="{e(self.href(url))}">{icon}{e(label)}</a>'

    def link_chips(self, item):
        chips = []
        for l in item.get('links', []):
            kind = l.get('kind', 'link')
            label = l.get('label') or self.t('link.' + kind)
            chips.append(self.chip(label, l['url'], download=l['url'].startswith('files/')))
        for i, part in enumerate(item.get('parts', [])):
            label = self.t('link.part3') if 'terza' in part.get('label', '') else self.t('link.part2')
            chips.append(self.chip(label, part['url'], download=part['url'].startswith('files/')))
        return f'<p class="entry__actions">{"".join(chips)}</p>' if chips else ''

    def paper_entry(self, it):
        title = it['title']                     # may contain <em>
        if it.get('url'):
            title = f'<a href="{e(self.href(it["url"]))}">{title}</a>'
        details = it.get('details', '')
        if it.get('with'):
            details = self.t('list.with', name=e(it['with'])) + ('. ' if details else '') + details
        det = f'<p class="entry__details">{details}</p>' if details else ''
        return f'''<li class="entry" data-entry>
<span class="entry__year">{it.get('year') or ''}</span>
<div class="entry__body"><p class="entry__title">{title}</p>{det}{self.link_chips(it)}</div>
</li>'''

    def piece_entry(self, it, outlet_key=''):
        title = e(it['title'])
        url = it.get('url')
        main_is_file = bool(url and url.startswith('files/'))
        if url:
            title = f'<a href="{e(self.href(url))}">{title}</a>'
        outlet = e(it.get('outlet', ''))
        if it.get('outlet_url'):
            outlet = f'<a href="{e(self.href(it["outlet_url"]))}">{outlet}</a>'
        bits = [b for b in [outlet, e(it['note']) if it.get('note') else ''] if b]
        det = f'<p class="entry__details">{", ".join(bits)}</p>' if bits else ''
        chips = []
        if main_is_file:                         # the piece is a document stored on this site
            ext = url.rsplit('.', 1)[-1].lower()
            label = self.t('link.' + ext) if ('link.' + ext) in self.s.strings else ext.upper()
            chips.append(self.chip(label, url, download=True))
        for part in it.get('parts', []):
            label = self.t('link.part3') if 'terza' in part.get('label', '') else self.t('link.part2')
            chips.append(self.chip(label, part['url'], download=part['url'].startswith('files/')))
        actions = f'<p class="entry__actions">{"".join(chips)}</p>' if chips else ''
        data = f' data-outlet="{e(outlet_key)}"' if outlet_key else ''
        return f'''<li class="entry" data-entry{data}>
<span class="entry__year">{it.get('year') or ''}</span>
<div class="entry__body"><p class="entry__title">{title}</p>{det}{actions}</div>
</li>'''

    def tools(self, total, label_key, outlets=None):
        buttons = ''
        if outlets:
            pills = [f'<button class="pill" type="button" data-filter-outlet="" aria-pressed="true">{e(self.t("list.all"))} <span class="pill__n">{total}</span></button>']
            for name, key, n in outlets:
                pills.append(f'<button class="pill" type="button" data-filter-outlet="{e(key)}" aria-pressed="false">{e(name)} <span class="pill__n">{n}</span></button>')
            buttons = f'<div class="subnav" data-needs-js>{"".join(pills)}</div>'
        template = self.t('list.count', n='{n}')
        return f'''<div class="tools">
<label class="search" data-needs-js><span class="search__label">{e(self.t(label_key))}</span>
<input class="search__input" type="search" data-filter-input autocomplete="off" spellcheck="false"></label>
{buttons}
<p class="tools__count" data-needs-js data-filter-count data-template="{e(template)}" aria-live="polite">{e(template.replace('{n}', str(total)))}</p>
</div>'''

    def shelf(self, books, wrap=False):
        items = []
        for b in books:
            cat = next(c for c in self.s.books['categories'] if c['id'] == b['category'])
            href = self.url('books-' + cat['id'], anchor=b['id'])
            cover = self.img(b['cover'], alt='') if b.get('cover') else ''
            items.append(f'<a class="shelf__item" href="{href}"><span class="shelf__cover">{cover}</span><span class="shelf__title">{e(b["title"])}</span></a>')
        return f'<div class="shelf{" shelf--wrap" if wrap else ""}">{"".join(items)}</div>'

    # --- events
    def fmt_date(self, start, end=None):
        m = MONTHS[self.lang]
        if end and end != start:
            if (start.year, start.month) == (end.year, end.month):
                return f'{start.day}–{end.day} {m[start.month - 1]} {start.year}'
            if start.year == end.year:
                return f'{start.day} {m[start.month - 1]} – {end.day} {m[end.month - 1]} {end.year}'
            return f'{start.day} {m[start.month - 1]} {start.year} – {end.day} {m[end.month - 1]} {end.year}'
        return f'{start.day} {m[start.month - 1]} {start.year}'

    def event_item(self, ev, tag='li'):
        start = dt.date.fromisoformat(ev['date'])
        end = dt.date.fromisoformat(ev['end_date']) if ev.get('end_date') else start
        small = [] if end != start else [WEEKDAYS[self.lang][start.weekday()]]
        if ev.get('time'):
            small.append(self.t('events.at', time=ev['time']))
        stamp = ev['date'] + (f'T{ev["time"].zfill(5)}' if ev.get('time') else '')
        small_html = f'<small>{e(", ".join(small))}</small>' if small else ''
        place = ', '.join(x for x in [self.pick(ev.get('venue')), self.pick(ev.get('city'))] if x)
        meta_html = f'<p class="event__meta">{e(place)}</p>' if place else ''
        if ev.get('with'):
            meta_html += f'<p class="event__meta">{e(self.t("events.with", name=self.pick(ev["with"])))}</p>'
        desc = self.pick(ev.get('description'))
        desc_html = f'<p class="event__desc">{e(desc)}</p>' if desc else ''
        link = ''
        if ev.get('url'):
            label = self.pick(ev.get('link_label')) or self.t('events.details')
            link = f'<p class="event__links">{self.chip(label, ev["url"])}</p>'
        return f'''<{tag} class="event" data-event-start="{ev['date']}" data-event-end="{end.isoformat()}">
<p class="event__date"><time datetime="{stamp}">{e(self.fmt_date(start, end))}</time>{small_html}</p>
<div><p class="event__title">{e(self.pick(ev['title']))}</p>{meta_html}{desc_html}{link}</div>
</{tag}>'''

    def split_events(self):
        events = self.s.events.get('events', [])
        end = lambda ev: ev.get('end_date') or ev['date']
        upcoming = sorted((ev for ev in events if end(ev) >= self.s.today.isoformat()), key=lambda ev: ev['date'])
        past = sorted((ev for ev in events if end(ev) < self.s.today.isoformat()), key=lambda ev: ev['date'], reverse=True)
        return upcoming, past

    # --- the pages
    def page_home(self):
        s = self.s
        site = s.site
        bio = ''.join(f'<p>{p}</p>' for p in self.pick(site['bio']))
        portrait = self.img(site['portrait'], alt=self.t('about.portrait_alt'), lazy=False)
        recent = [b for rid in s.books.get('recent', []) for b in s.books['books'] if b['id'] == rid]

        upcoming, _ = self.split_events()
        events_html = ''
        if upcoming:
            rows = ''.join(self.event_item(ev) for ev in upcoming[:6])
            events_html = f'''<section class="section section--ash" data-events-teaser>
<div class="wrap">
<div class="section__head"><h2 class="h2">{e(self.t('home.next_events'))}</h2><a class="more" href="{self.url('events')}">{e(self.t('home.all_events'))}</a></div>
<ul class="events events--upcoming">{rows}</ul>
</div>
</section>'''

        latest = by_year([it for sec in s.papers['sections'] if sec['id'] in ('journal', 'chapters') for it in sec['items']])[:5]
        papers = ''.join(self.paper_entry(it) for it in latest)

        essays = by_year(s.essays['items'])
        stories = by_year([it for sec in s.stories['sections'] for it in sec['items']])
        media = [it for sec in s.media['sections'] for it in sec['items']]

        def digest(title_key, page, items, total, sub):
            rows = ''
            for it in items[:3]:
                label = e(it['title'])
                if it.get('url'):
                    label = f'<a href="{e(self.href(it["url"]))}">{label}</a>'
                rows += f'<li class="digest__item">{label}<small>{e(sub(it))}</small></li>'
            return f'''<div>
<h3 class="h3">{e(self.t(title_key))}</h3>
<ul class="digest__list">{rows}</ul>
<p class="digest__more"><a href="{self.url(page)}">{e(self.t('home.see_all', n=total))}</a></p>
</div>'''

        piece_sub = lambda it: ', '.join(str(x) for x in [it.get('outlet'), it.get('year')] if x)
        media_sub = lambda it: ' '.join(x for x in [it.get('series', ''), it.get('context', '')] if x).strip('() ')
        body = f'''<section class="section">
<div class="wrap intro">
<div class="intro__text">
<p class="lead">{e(self.pick(site['lead']))}</p>
<div class="prose">{bio}</div>
<p class="intro__more"><a href="{self.url('about')}">{e(self.t('home.more_about'))}</a></p>
</div>
<figure class="intro__portrait">{portrait}</figure>
</div>
</section>
{events_html}
<section class="section section--tight">
<div class="wrap">
<div class="section__head"><h2 class="h2">{e(self.t('home.recent_books'))}</h2><a class="more" href="{self.url('books')}">{e(self.t('home.all_books'))}</a></div>
{self.shelf(recent)}
</div>
</section>
<section class="section section--tight">
<div class="wrap">
<div class="section__head"><h2 class="h2">{e(self.t('home.recent_papers'))}</h2><a class="more" href="{self.url('papers')}">{e(self.t('home.all_papers'))}</a></div>
<ul class="entries">{papers}</ul>
</div>
</section>
<section class="section section--ash">
<div class="wrap">
<h2 class="visually-hidden">{e(self.t('home.writing'))}</h2>
<div class="digest">
{digest('title.essays', 'essays', essays, len(essays), piece_sub)}
{digest('title.stories', 'stories', stories, len(stories), piece_sub)}
{digest('title.media', 'media', media, len(media), media_sub)}
</div>
</div>
</section>'''
        title = f'{site["name"]} | {self.pick(site["role"])}'
        return title, self.t('desc.home'), body

    def books_subnav(self, current):
        pills = [f'<a class="pill" href="{self.url("books")}"{' aria-current="page"' if current == "books" else ""}>{e(self.t("books.all"))}</a>']
        for c in self.s.books['categories']:
            key = 'books-' + c['id']
            cur = ' aria-current="page"' if current == key else ''
            n = sum(1 for b in self.s.books['books'] if b['category'] == c['id'])
            pills.append(f'<a class="pill" href="{self.url(key)}"{cur}>{e(self.pick(c["title"]))} <span class="pill__n">{n}</span></a>')
        return f'<nav class="subnav" aria-label="{e(self.t("title.books"))}">{"".join(pills)}</nav>'

    def page_books(self):
        groups = ''
        for c in self.s.books['categories']:
            books = [b for b in self.s.books['books'] if b['category'] == c['id']]
            groups += f'''<section class="books-group">
<div class="section__head"><h2 class="h2">{e(self.pick(c['title']))}</h2><a class="more" href="{self.url('books-' + c['id'])}">{e(self.t('books.view_category'))}</a></div>
{self.shelf(books, wrap=True)}
</section>'''
        body = f'''<section class="section">
<div class="wrap">
<div class="tools">{self.books_subnav('books')}</div>
{groups}
</div>
</section>'''
        return self.t('title.books'), self.t('desc.books'), body

    def page_books_category(self):
        cid = self.key.split('-', 1)[1]
        cat = next(c for c in self.s.books['categories'] if c['id'] == cid)
        rows = ''
        for b in (b for b in self.s.books['books'] if b['category'] == cid):
            cover = self.img(b['cover'], alt='') if b.get('cover') else ''
            if b.get('url') and cover:
                cover = f'<a class="book__cover" href="{e(self.href(b["url"]))}" tabindex="-1" aria-hidden="true">{cover}</a>'
            else:
                cover = f'<div class="book__cover">{cover}</div>'
            desc = self.pick(b.get('desc')) if b.get('desc') else ''
            links = []
            if b.get('url'):
                links.append(f'<a class="pill" href="{e(self.href(b["url"]))}">{e(self.t("books.publisher_page"))}</a>')
            for f in b.get('downloads', []):
                links.append(f'<a class="pill" href="{e(self.href(f))}">{e(self.t("books.download_excerpt"))}</a>')
            rows += f'''<article class="book" id="{e(b['id'])}">
{cover}
<div>
<h2 class="h3">{e(b['title'])}</h2>
{f'<p class="book__desc">{e(desc)}</p>' if desc else ''}
{f'<p class="book__links">{"".join(links)}</p>' if links else ''}
</div>
</article>'''
        body = f'''<section class="section">
<div class="wrap">
<div class="tools">{self.books_subnav(self.key)}</div>
{rows}
</div>
</section>'''
        title = self.pick(cat['title'])
        return title, f'{self.t("title.books")}: {title}. {self.t("desc.books")}', body

    def page_papers(self):
        total = sum(len(sec['items']) for sec in self.s.papers['sections'])
        jump = ''.join(f'<a class="pill" href="#{e(sec["id"])}">{e(self.pick(sec["title"]))} <span class="pill__n">{len(sec["items"])}</span></a>' for sec in self.s.papers['sections'])
        groups = ''
        for sec in self.s.papers['sections']:
            rows = ''.join(self.paper_entry(it) for it in by_year(sec['items']))
            groups += f'''<section class="group" id="{e(sec['id'])}" data-group>
<div class="group__head"><h2 class="h2">{e(self.pick(sec['title']))}</h2></div>
<ul class="entries">{rows}</ul>
</section>'''
        body = f'''<section class="section" data-filter>
<div class="wrap">
{self.tools(total, 'list.filter_label')}
<nav class="subnav" aria-label="{e(self.t('list.jump'))}" style="margin-bottom:2.5rem">{jump}</nav>
{groups}
<p class="empty" data-filter-empty hidden>{e(self.t('list.none'))}</p>
</div>
</section>'''
        return self.t('title.papers'), self.t('desc.papers'), body

    def page_essays(self):
        items = by_year(self.s.essays['items'])
        counts = {}
        for it in items:
            counts[it.get('outlet', '')] = counts.get(it.get('outlet', ''), 0) + 1
        major = [name for name, n in sorted(counts.items(), key=lambda kv: -kv[1]) if n >= 3 and name]
        slug = lambda name: re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
        outlets = [(name, slug(name), counts[name]) for name in major]
        other = sum(n for name, n in counts.items() if name not in major)
        if other:
            outlets.append((self.t('list.other'), 'other', other))
        rows = ''.join(self.piece_entry(it, slug(it['outlet']) if it.get('outlet') in major else 'other') for it in items)
        body = f'''<section class="section" data-filter>
<div class="wrap">
{self.tools(len(items), 'list.filter_label_essays', outlets)}
<ul class="entries">{rows}</ul>
<p class="empty" data-filter-empty hidden>{e(self.t('list.none'))}</p>
</div>
</section>'''
        return self.t('title.essays'), self.t('desc.essays'), body

    def page_stories(self):
        total = sum(len(sec['items']) for sec in self.s.stories['sections'])
        outlets = [(self.pick(sec['title']), sec['id'], len(sec['items'])) for sec in self.s.stories['sections']]
        groups = ''
        for sec in self.s.stories['sections']:
            rows = ''.join(self.piece_entry(it, sec['id']) for it in by_year(sec['items']))
            groups += f'''<section class="group" id="{e(sec['id'])}" data-group>
<div class="group__head"><h2 class="h2">{e(self.pick(sec['title']))}</h2><span class="group__n">{len(sec['items'])}</span></div>
<ul class="entries">{rows}</ul>
</section>'''
        body = f'''<section class="section" data-filter>
<div class="wrap">
{self.tools(total, 'list.filter_label_essays', outlets)}
{groups}
<p class="empty" data-filter-empty hidden>{e(self.t('list.none'))}</p>
</div>
</section>'''
        return self.t('title.stories'), self.t('desc.stories'), body

    def page_media(self):
        total = sum(len(sec['items']) for sec in self.s.media['sections'])
        outlets = [(self.pick(sec['title']), sec['id'], len(sec['items'])) for sec in self.s.media['sections']]
        groups = ''
        for sec in self.s.media['sections']:
            icon = ICONS['podcast'] if sec['id'] == 'podcast' else ICONS['video']
            rows = ''
            for it in sec['items']:
                title = e(it['title'])
                if it.get('url'):
                    title = f'<a href="{e(self.href(it["url"]))}">{title}</a>'
                series = f'<span class="entry__series">{e(it["series"])}</span>' if it.get('series') else ''
                ctx = f'<p class="entry__details">{e(it["context"].strip("()"))}</p>' if it.get('context') else ''
                rows += f'<li class="entry entry--media" data-entry data-outlet="{e(sec["id"])}">{icon}<div class="entry__body">{series}<p class="entry__title">{title}</p>{ctx}</div></li>'
            groups += f'''<section class="group" id="{e(sec['id'])}" data-group>
<div class="group__head"><h2 class="h2">{e(self.pick(sec['title']))}</h2><span class="group__n">{len(sec['items'])}</span></div>
<ul class="entries">{rows}</ul>
</section>'''
        body = f'''<section class="section" data-filter>
<div class="wrap">
{self.tools(total, 'list.filter_label_media', outlets)}
{groups}
<p class="empty" data-filter-empty hidden>{e(self.t('list.none'))}</p>
</div>
</section>'''
        return self.t('title.media'), self.t('desc.media'), body

    def page_events(self):
        upcoming, past = self.split_events()
        up = ''.join(self.event_item(ev) for ev in upcoming)
        pa = ''.join(self.event_item(ev) for ev in past)
        body = f'''<section class="section" data-events>
<div class="wrap">
<section class="group">
<div class="group__head"><h2 class="h2">{e(self.t('events.upcoming'))}</h2></div>
<ul class="events events--upcoming" data-events-upcoming>{up}</ul>
<p class="empty" data-events-none{'' if not upcoming else ' hidden'}>{e(self.t('events.none_upcoming'))}</p>
</section>
<section class="group" data-events-past-section{'' if past else ' hidden'}>
<div class="group__head"><h2 class="h2">{e(self.t('events.past'))}</h2></div>
<ul class="events" data-events-past>{pa}</ul>
</section>
</div>
</section>'''
        return self.t('title.events'), self.t('desc.events'), body

    def page_about(self):
        site = self.s.site
        bio = ''.join(f'<p>{p}</p>' for p in self.pick(site['bio']))
        rows = ''
        for c in site['contacts']:
            rows += f'<div class="facts__row"><dt>{e(self.pick(c["label"]))}</dt><dd><a href="{e(self.href(c["url"]))}">{e(self.pick(c["text"]))}</a></dd></div>'
        social = ', '.join(f'<a href="{e(x["url"])}" rel="me">{e(x["name"])}</a>' for x in site['social'])
        rows += f'<div class="facts__row"><dt>{e(self.t("about.elsewhere"))}</dt><dd>{social}</dd></div>'
        portrait = self.img(site['portrait'], alt=self.t('about.portrait_alt'), lazy=False)
        body = f'''<section class="section">
<div class="wrap about">
<div>
<p class="lead">{e(self.pick(site['lead']))}</p>
<div class="prose" style="margin-top:1.5rem">{bio}</div>
<h2 class="visually-hidden">{e(self.t('about.contacts'))}</h2>
<dl class="facts">{rows}</dl>
</div>
<figure class="about__portrait">{portrait}</figure>
</div>
</section>'''
        return self.t('title.about'), self.t('desc.about'), body

    def page_privacy(self):
        paras = ''.join(f'<p>{e(p)}</p>' for p in self.pick(self.s.strings['privacy.body']))
        body = f'<section class="section"><div class="wrap"><div class="prose">{paras}</div></div></section>'
        return self.t('title.privacy'), self.t('title.privacy') + ' | ' + self.s.site['name'], body

    def page_notfound(self):
        body = f'''<section class="section"><div class="wrap"><div class="prose">
<p class="lead">{e(self.t('404.body'))}</p>
<p style="margin-top:1.5rem"><a href="{self.url('home')}">{e(self.t('404.home'))}</a></p>
</div></div></section>'''
        return self.t('title.404'), self.t('404.body'), body


# --------------------------------------------------------------------------- command line
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--check', action='store_true', help='validate the content and stop')
    ap.add_argument('--serve', nargs='?', const=8000, type=int, metavar='PORT', help='build, then serve public/ locally')
    ap.add_argument('--local', action='store_true', help='links end in index.html, so the pages open from disk')
    ap.add_argument('--out', type=Path, default=PUBLIC, help='output folder (default: public/)')
    args = ap.parse_args()

    try:
        site = Site(args.out.resolve(), local=args.local)
    except (json.JSONDecodeError, FileNotFoundError) as err:
        sys.exit(f'ERROR reading the content files: {err}')
    if not site.validate():
        print('The content has problems, nothing was built:\n  - ' + '\n  - '.join(site.errors), file=sys.stderr)
        sys.exit(1)
    if args.check:
        print('Content OK.')
        return
    n = site.build()
    print(f'Built {n} pages into {args.out}')
    if args.serve:
        import functools
        import http.server
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(args.out))
        print(f'Preview: http://localhost:{args.serve}  (Ctrl+C to stop)')
        http.server.ThreadingHTTPServer(('127.0.0.1', args.serve), handler).serve_forever()


if __name__ == '__main__':
    main()
