# paolopecere.it

Personal website of Paolo Pecere (historian of philosophy and writer). Static site, two
languages: English at the site root, Italian under `/it/`.

The owner writes to you in Italian and usually gives minimal information ("aggiungi questo
evento", "metti questo articolo"). Reply in Italian, make the change, publish it, and say in
one or two lines what is now on the site.

## Where things stand

The site was built in November 2026 as a migration from Jimdo, in a different Claude
account from the one you are running in. You have no memory of that work and do not need
it: this file, `NOTE-MIGRAZIONE.md` (what was migrated and what is still open) and
`MESSA-ONLINE.md` (the checklist for hosting and domain) contain everything. If the owner
asks for help with hosting or the domain, follow `MESSA-ONLINE.md` and tick its boxes as
steps are done. When its last box is ticked, delete that file and this paragraph's
reference to it.

## The one rule

All content lives in `content/*.json`. The HTML in `public/` is generated.

1. Edit the JSON in `content/` (and add files under `public/assets/` when needed).
2. Run `python3 build.py` (it validates first and refuses to build if something is wrong).
3. Commit **both** `content/` and the regenerated `public/` in the same commit.
4. Push to `main`. The host publishes `public/` within a minute or two.

Never edit `public/**/*.html` by hand: the next build overwrites it. `public/assets/` is
the exception: it is hand-managed (CSS, JS, fonts, images, documents).

Useful commands:

    python3 build.py --check     # validate only
    python3 build.py --serve     # build and preview at http://localhost:8000
    python3 build.py --local --out preview   # copy that opens from disk, for offline previews

`build.py` needs only the Python standard library. `tools/images.py` needs Pillow
(`python3 -m pip install pillow`).

## Languages

- Every text shown on the site is either a plain string (same in both languages) or an
  object `{"en": "...", "it": "..."}`.
- When the owner gives a text in one language only, write the other one yourself and tell
  him which one you translated. Titles of books, papers, articles and talks are never
  translated: they stay in their original language.
- Interface strings (menu, headings, buttons) are in `content/i18n.json`.
- Italian pages use the same addresses as the English ones with `/it/` in front.

## Recipes

### Add an event (most frequent)

Append an object to `"events"` in `content/events.json`:

    {"date": "2027-01-15", "time": "18:30",
     "title": {"it": "Presentazione di «Il senso della natura»", "en": "Book launch: «Il senso della natura»"},
     "venue": "Libreria Esempio", "city": "Roma",
     "with": "Nome Cognome",
     "description": {"it": "…", "en": "…"},
     "url": "https://…"}

Only `date` (YYYY-MM-DD) and `title` are required. `end_date` makes a multi-day event.
Order in the file does not matter. The Events page sorts them and moves them from
"Upcoming" to "Past" by itself, also between builds (a small script compares the date with
the visitor's clock). Upcoming events also appear on the home page.

### Add a paper

`content/papers.json`, in the right section (`journal`, `chapters`, `reviews`,
`encyclopedia`):

    {"title": "Title of the paper",
     "details": "\"Journal Name\", vol. 12 (2027), pp. 1-20.",
     "year": 2027,
     "url": "https://doi.org/…",
     "links": [{"kind": "pdf", "url": "files/2027-short-name.pdf"},
               {"kind": "preprint", "url": "https://…"}]}

- `title` and `details` may contain `<em>…</em>`; nothing else.
- `url` makes the title a link (journal or publisher page).
- `links[].kind`: `pdf`, `docx`, `link` (publisher's page), `preprint`. Add `"label"` to
  override the button text.
- Documents go in `public/assets/files/` with a lowercase, hyphenated name and are
  referenced as `files/name.pdf`.
- Lists are sorted by `year`, newest first; same-year items keep the order of the file, so
  put a new item above the others of its year. The five newest journal articles and
  chapters appear on the home page automatically.

### Add an essay, a story or a travelogue

`content/essays.json` (`items`) or `content/stories.json` (sections `travelogues`,
`short-stories`):

    {"title": "Title", "outlet": "Il Tascabile", "year": 2027, "url": "https://…",
     "note": "intervista a …"}

Optional: `outlet_url`, and `parts` for pieces in several parts
(`[{"label": "parte seconda", "url": "…"}]`). On the Essays page, outlets with three or
more pieces get their own filter button automatically.

### Add a video or a podcast

`content/media.json`, section `video` or `podcast`:

    {"title": "Title of the talk", "series": "Filosofia in dialogo", "context": "(con …)", "url": "https://…"}

New items go at the top of the section (this list is not sorted by date).

### Add a book

1. Cover: `python3 tools/images.py cover path/to/cover.jpg book-id`
   (creates `public/assets/img/covers/book-id.jpg`).
2. `content/books.json`, in `"books"`, in the position where it should appear:

       {"id": "book-id", "category": "research", "title": "Title",
        "cover": "img/covers/book-id.jpg",
        "desc": {"en": "…", "it": "…"},
        "url": "https://publisher…"}

   Categories: `research`, `fiction`, `textbooks`. `downloads` is an optional list of
   `files/…` (excerpts).
3. To show it on the home page, add its id to `"recent"` (first = leftmost).

### Change a background photograph

Every page has a photograph at the top. They are set in `content/site.json` under
`"photos"`, one entry per page key (`home`, `books`, `books-research`, `books-fiction`,
`books-textbooks`, `papers`, `essays`, `stories`, `events`, `media`, `about`, `privacy`);
`default` is used for pages without an entry, and a `books-*` page without its own entry
uses the `books` one.

1. `python3 tools/images.py photo path/to/photo.jpg short-name`
   (creates `short-name.jpg` and `short-name-sm.jpg` in `public/assets/img/photos/`).
2. In `site.json`: `"media": {"src": "short-name.jpg", "focus": "50% 40%", "caption": {"en": "Place, Country", "it": "Luogo, Paese"}}`.
   `focus` is the CSS `object-position`: which part of the photo stays visible when it is
   cropped (horizontal % then vertical %; a higher second number shows more of the bottom).
   `caption` is optional; add one only when the owner tells you the place.

Use landscape photos, ideally 2000 px wide or more (several current ones are about
1100 px and look soft on large screens). The page title sits on a paper-coloured tab in
the lower-left corner of the photo and the menu is white over its top edge, so keep the
subject away from the lower left and check that the menu stays readable. Look at the
result at desktop width and at about 390 px.

Photos available in `public/assets/img/photos/`: `bromo-wide`, `bromo-mist`, `patagonia`,
`altopiano`, `lago-altopiano`, `lago-vento`, `torres-del-paine`, `fitz-roy-bosco`,
`fitz-roy-strada`, `dune-oasi`, `dune-rosa`, `dune-tramonto` (not used yet),
`terra-crepata`.

### Change the biography, contacts or portrait

`content/site.json`: `lead` (the large first sentence), `bio` (paragraphs, `<em>` allowed),
`contacts`, `social`. Portrait: `python3 tools/images.py portrait path/to/photo.jpg`.

### Add a new section to the menu

In `build.py`: add the page to `PAGES`, its key to `NAV`, write a `page_<key>` method
modelled on `page_stories`, and add `nav.<key>`, `title.<key>` and `desc.<key>` to
`content/i18n.json`. Keep the menu labels to one word.

## Publishing

The host is Cloudflare Pages: `main` is the live site, every other branch gets a preview
at `https://<branch>.<project>.pages.dev` (branch name lowercased, anything that is not a
letter or a digit replaced by a hyphen). The project name is written in `MESSA-ONLINE.md`
once the owner has created it; ask for it the first time if it is still blank and record
it there.

- **Routine additions** (an event, a new paper, essay, video, a corrected link): publish
  straight away. Commit, then get the commit onto `main` and push `main`. Tell the owner
  it will be live in a minute or two.
- **Anything visual or structural** (a new photo, layout or text changes on the home
  page, a new section): push your working branch first, give the owner the preview
  address, and move it to `main` only when he says so.
- If a push to `main` is refused in your environment, open a pull request instead and tell
  the owner to press "Merge pull request" on GitHub.

Before every push:

- `python3 build.py` printed `Built … pages` with no errors.
- For anything visual, look at it: `python3 build.py --serve`, then open the page at
  desktop width and at about 390 px.
- `git status` shows the JSON you edited plus the regenerated HTML (and any new asset).

## Map of the repository

    content/            the site's content (edit here)
      site.json         name, biography, contacts, social links, background photos
      i18n.json         interface strings in both languages, privacy text
      books.json        categories, books, "recent" list for the home page
      papers.json       journal articles, chapters, reviews, encyclopedia entries
      essays.json       essays and journalism
      stories.json      travelogues and short stories
      media.json        video and podcasts
      events.json       events (upcoming and past)
    build.py            the generator
    tools/images.py     prepares covers, photos and the portrait
    public/             what the host publishes
      assets/           css, js, fonts, images, documents (hand-managed)
      **/index.html     generated pages (do not edit)
      _redirects        old Jimdo addresses -> new pages (Cloudflare Pages / Netlify)

## Design

- Palette (from the Bromo photographs): mist `#f4f5f3`, ash `#e5e9e8`, basalt `#17202a`,
  slate `#55606b`, sulphur `#e5ae1b`. Variables at the top of `public/assets/css/site.css`.
- Type: Bricolage Grotesque (titles, menu, buttons) and Newsreader (text), both
  self-hosted in `public/assets/fonts/`.
- The signature element is the title tab: the page's paper colour rises into the
  lower-left corner of the photograph and carries the title in one colour (the owner does
  not want letters cut across two colours). Keep everything else quiet: no cards, no
  shadows, no additional accent colours.
- No cookies, no analytics, no fonts or scripts loaded from other sites. If that ever
  changes, the privacy text in `i18n.json` (`privacy.body`) must change too.

## Hosting

Cloudflare Pages, connected to this repository. Production branch `main`, framework preset
none, build command `exit 0`, build output directory `public`. Nothing is built on the
host: it publishes the committed `public/` folder, which is why the pages must be
regenerated and committed with every content change. The site uses relative links, so
preview addresses work too. `public/_redirects` maps the old Jimdo addresses.
