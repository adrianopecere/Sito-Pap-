# paolopecere.it

Sito personale di Paolo Pecere (storico della filosofia e scrittore). Sito statico in due
lingue: inglese all'indirizzo principale, italiano sotto `/it/`.

## A chi serve questo file

Il proprietario del sito non è un programmatore: aggiunge contenuti, non scrive codice.
Scrive in italiano e di solito dà poche informazioni («aggiungi questo evento», «metti
questo articolo»). Il tuo compito è inserire il contenuto nel file giusto, rigenerare le
pagine, aprire una pull request e dirgli in parole semplici che cosa comparirà e dove.

Non hai memoria delle sessioni precedenti e non ti serve: tutto è in questo file, in
`NOTE-MIGRAZIONE.md` (che cosa è stato migrato da Jimdo e che cosa resta aperto) e in
`MESSA-ONLINE.md` (i passi per hosting e dominio). Se il proprietario chiede aiuto per il
dominio, segui `MESSA-ONLINE.md` e spunta le caselle man mano; quando l'ultima è spuntata,
cancella quel file e i riferimenti a esso qui sopra.

## Come funziona il sito

I contenuti sono nei file `content/*.json`. Le pagine HTML in `public/` sono generate da
`build.py`.

1. Modifica il JSON in `content/` (e aggiungi file in `public/assets/` se servono:
   copertine, PDF).
2. Esegui `python3 build.py`: prima controlla i contenuti e, se qualcosa non va, non
   genera nulla.
3. Metti nello stesso commit **sia** `content/` **sia** le pagine rigenerate in `public/`.

Non modificare mai a mano `public/**/*.html`: la generazione successiva le sovrascrive.

    python3 build.py --check     # controlla soltanto
    python3 build.py             # controlla e rigenera public/
    python3 build.py --serve     # rigenera e mostra l'anteprima su http://localhost:8000

`build.py` usa solo la libreria standard di Python. `tools/images.py` richiede Pillow
(`python3 -m pip install pillow`).

## Regole

1. **Solo contenuti.** Sono ammesse aggiunte e correzioni di contenuto: voci nei file
   `content/*.json`, copertine in `public/assets/img/covers/`, documenti in
   `public/assets/files/`.
2. **Mai toccare senza conferma esplicita**: layout, CSS e script
   (`public/assets/css/`, `public/assets/js/`, i font), `build.py`, `tools/`, le voci di
   menu e i testi dell'interfaccia in `content/i18n.json`, le fotografie di sfondo e la
   struttura di `content/site.json`, la configurazione di pubblicazione
   (`public/_redirects`, impostazioni di Cloudflare Pages, branch `main`). Se una
   richiesta lo richiede, spiega in una frase che cosa cambierebbe e aspetta un «sì».
3. **Mai inventare dati.** Se manca un dato obbligatorio, chiedilo. Non inventare e non
   «completare a memoria» DOI, ISBN, date, orari, numeri di pagina, volumi, nomi di
   persone o link. Se il proprietario dà un link o un DOI, copialo così com'è. Se un dato
   facoltativo manca, lascia fuori il campo.
4. **Una richiesta = un branch = una pull request**, con titolo in italiano che dice che
   cosa è stato aggiunto (per esempio «Aggiunto evento: presentazione a Roma, 15 gennaio
   2027»). Non mescolare nella stessa pull request cose non richieste. Se l'ambiente ti
   assegna già un branch di lavoro usa quello, altrimenti creane uno da `main` aggiornato
   con un nome come `contenuti/evento-roma-gennaio`.
5. **Non fare push diretto su `main`** e non fare il merge di tua iniziativa: `main` è il
   sito pubblico.
6. Non correggere refusi o stile dei testi esistenti se non è stato chiesto: segnalali
   nella risposta.

## Lingue

- Ogni testo è una stringa semplice (uguale nelle due lingue) oppure un oggetto
  `{"en": "...", "it": "..."}`.
- Se il proprietario dà un testo in una sola lingua, scrivi tu l'altra versione e digli
  quale hai tradotto, così può rileggerla.
- I titoli di libri, articoli, saggi e interventi non si traducono mai: restano nella
  lingua originale.

## Sezioni principali

### Articoli accademici (papers)

**File**: `content/papers.json`. La voce va nella lista `items` della sezione giusta:
`journal` (articoli su rivista), `chapters` (capitoli di libro), `reviews` (recensioni),
`encyclopedia` (voci enciclopediche). Se non è chiaro quale, chiedi.

**Compare in**: pagina Papers (`/papers/` e `/it/papers/`). I cinque più recenti fra
`journal` e `chapters` compaiono da soli anche in home.

| Campo | | Contenuto |
|---|---|---|
| `title` | obbligatorio | Titolo, in lingua originale. Può contenere `<em>…</em>`, nient'altro. |
| `year` | obbligatorio | Anno di pubblicazione, numero di quattro cifre senza virgolette (`2027`). |
| `details` | obbligatorio | Rivista o volume, numero, anno, pagine, nello stile delle voci esistenti. Può contenere `<em>…</em>`. |
| `url` | facoltativo | Rende il titolo un link (di norma il DOI nella forma `https://doi.org/…`, o la pagina dell'editore). |
| `links` | facoltativo | Pulsanti sotto la voce. Ognuno ha `kind` (`pdf`, `docx`, `link` = pagina dell'editore, `preprint`), `url` e, se serve, `label` per cambiare la scritta. |
| `with` | facoltativo | Coautore («con …»). |

`build.py` blocca solo la mancanza di `title` o un file inesistente; `year` e `details`
sono obbligatori per regola nostra, perché senza anno la voce finisce in fondo alla lista.

**Date**: solo l'anno, nel campo `year`.

**Ordinamento**: per `year`, dal più recente. A parità di anno vale l'ordine del file:
una voce nuova va messa **sopra** le altre dello stesso anno.

**Documenti**: i PDF vanno in `public/assets/files/` con nome in minuscolo, senza spazi né
accenti, con trattini (per esempio `2027-nome-breve.pdf`), e si indicano come
`files/2027-nome-breve.pdf`.

**Esempio** (voce esistente, sezione `journal`):

    {
     "title": "Monads, Solidity and the Metaphysics of Bodies: Kant’s Non-Newtonian theory of material substance and its sources",
     "details": "\"Kant-Studien\", vol. 116, no. 2, 2025, pp. 208-229.",
     "year": 2025,
     "url": "https://doi.org/10.1515/kant-2025-2014",
     "links": [
      {
       "kind": "link",
       "url": "https://www.degruyterbrill.com/document/doi/10.1515/kant-2025-2014/html"
      },
      {
       "kind": "preprint",
       "url": "https://acrobat.adobe.com/id/urn:aaid:sc:EU:112dcc48-df11-417c-8092-675b1e489179"
      }
     ]
    }

### Libri (books)

**File**: `content/books.json`, lista `"books"`.

**Compare in**: pagina Books (`/books/`) e nella pagina della sua categoria
(`/books/research/`, `/books/fiction-and-narrative-non-fiction/`, `/books/textbooks/`).
In home compare solo se il suo `id` è aggiunto alla lista `"recent"`.

| Campo | | Contenuto |
|---|---|---|
| `id` | obbligatorio | Identificativo unico: titolo abbreviato in minuscolo con trattini, senza accenti (`il-senso-della-natura`). |
| `category` | obbligatorio | `research`, `fiction` oppure `textbooks`. |
| `title` | obbligatorio | Titolo completo, in lingua originale. |
| `cover` | obbligatorio per regola nostra | `img/covers/<id>.jpg`. Senza copertina la pagina si genera ma resta un riquadro vuoto: chiedi l'immagine. |
| `desc` | facoltativo | Descrizione `{"it": "…", "en": "…"}`, solo testo. |
| `original_language` | facoltativo | Lingua in cui è stata scritta la descrizione originale (`it`, `en`, `es`): è un promemoria, non compare sul sito. |
| `url` | facoltativo | Pagina dell'editore. |
| `downloads` | facoltativo | Lista di estratti scaricabili, `["files/nome.pdf"]`. |

Non esiste un campo per ISBN, editore o anno: se il proprietario li vuole visibili, vanno
scritti dentro `desc`.

**Date**: nessuna.

**Ordinamento**: nessun ordinamento automatico. I libri compaiono nell'ordine del file,
raggruppati per categoria: metti la voce nella posizione in cui deve comparire fra quelli
della sua categoria (di norma in cima, se è il più recente). In home l'ordine è quello
della lista `"recent"` (il primo è quello più a sinistra).

**Copertina**: `python3 tools/images.py cover percorso/copertina.jpg id-del-libro` crea
`public/assets/img/covers/id-del-libro.jpg`.

**Esempio** (voce esistente):

    {
     "id": "la-filosofia-della-natura-in-kant",
     "category": "research",
     "title": "La filosofia della natura in Kant",
     "cover": "img/covers/la-filosofia-della-natura-in-kant.jpg",
     "original_language": "it",
     "desc": {
      "it": "Una ricostruzione complessiva della filosofia della natura kantiana, dalle opere giovanili fino agli ultimi manoscritti.",
      "en": "A comprehensive reconstruction of Kant's philosophy of nature, from the early works to the last manuscripts."
     },
     "url": "https://www.paginasc.it/articolo_desc.php?id_art=630&t=la-filosofia-della-natura-in-kant"
    }

### Eventi (events)

**File**: `content/events.json`, lista `"events"`.

**Compare in**: pagina Events (`/events/` e `/it/events/`); gli eventi futuri compaiono
anche in home (al massimo tre, i più vicini).

| Campo | | Contenuto |
|---|---|---|
| `date` | obbligatorio | Giorno dell'evento (o primo giorno), `AAAA-MM-GG`. |
| `title` | obbligatorio | Titolo. Il titolo di un libro o di un intervento resta in originale; la parte descrittiva («Presentazione di…») va nelle due lingue. |
| `end_date` | facoltativo | Ultimo giorno, `AAAA-MM-GG`, per eventi di più giorni. |
| `time` | facoltativo | Ora locale, `HH:MM` su 24 ore (`18:30`). |
| `venue` | facoltativo | Luogo (libreria, università, festival). |
| `city` | facoltativo | Città. |
| `with` | facoltativo | Altri partecipanti. |
| `description` | facoltativo | Una o due frasi, solo testo. |
| `url` | facoltativo | Link alla pagina dell'evento. |
| `link_label` | facoltativo | Scritta del pulsante del link, se diversa da quella normale. |

`title`, `venue`, `city`, `with`, `description` e `link_label` possono essere testo
semplice oppure `{"en": "…", "it": "…"}`.

**Date**: sempre `AAAA-MM-GG` (per esempio `2027-01-15`); il sito le scrive poi per esteso
nelle due lingue, con il giorno della settimana. Se il proprietario non dice l'anno o il
giorno esatto, chiedilo.

**Ordinamento**: automatico, l'ordine nel file non conta. Gli eventi futuri sono elencati
dal più vicino al più lontano, quelli passati dal più recente. Il passaggio da «Prossimi»
a «Passati» avviene da solo il giorno dopo la fine dell'evento, anche senza rigenerare il
sito. Gli eventi passati non vanno cancellati.

**Esempio**: la lista è ancora vuota, quindi non c'è una voce reale da copiare. Questo è
il modello che si trova in `content/events.json` alla voce `_example` (i dati sono finti):

    {
     "date": "2027-01-15",
     "time": "18:30",
     "title": {
      "it": "Presentazione di «Il senso della natura»",
      "en": "Book launch: «Il senso della natura»"
     },
     "venue": "Libreria Esempio",
     "city": "Roma",
     "with": "Nome Cognome",
     "url": "https://example.org/evento"
    }

Quando esisterà il primo evento reale, sostituisci questo esempio con quello.

## Altre sezioni

Valgono le stesse regole. In tutti i casi `title` è obbligatorio e, per saggi e racconti,
l'ordinamento è per `year` dal più recente (a parità di anno, ordine del file: la voce
nuova va sopra).

- **Saggi e articoli giornalistici**: `content/essays.json`, lista `items`. Pagina
  Essays.

      {"title": "Titolo", "outlet": "Il Tascabile", "year": 2027, "url": "https://…",
       "note": "intervista a …"}

  Facoltativi: `outlet_url`, `note`, e `parts` per i pezzi in più puntate
  (`[{"label": "parte seconda", "url": "…"}]`). Le testate con tre o più pezzi ottengono
  da sole un pulsante di filtro.
- **Reportage e racconti**: `content/stories.json`, sezioni `travelogues` e
  `short-stories`, stessi campi dei saggi. Pagina Stories.
- **Video e podcast**: `content/media.json`, sezione `video` o `podcast`. Pagina Media.

      {"title": "Titolo dell'intervento", "series": "Filosofia in dialogo", "context": "(con …)", "url": "https://…"}

  Questa lista **non** è ordinata per data: la voce nuova va in cima alla sezione.
- **Biografia, contatti, ritratto**: `content/site.json` (`lead`, `bio`, `contacts`,
  `social`); ritratto con `python3 tools/images.py portrait percorso/foto.jpg`. Sono
  testi della home: mostra l'anteprima prima di chiedere il merge.

## Modifiche che richiedono conferma esplicita

Si fanno solo se il proprietario le chiede in modo chiaro, e si descrivono prima di
eseguirle (regola 2).

- **Fotografia di sfondo di una pagina**: `python3 tools/images.py photo percorso/foto.jpg
  nome-breve` crea `nome-breve.jpg` e `nome-breve-sm.jpg` in
  `public/assets/img/photos/`; poi in `content/site.json`, sotto `"photos"`, alla chiave
  della pagina: `"media": {"src": "nome-breve.jpg", "focus": "50% 40%", "caption": {"en":
  "Place, Country", "it": "Luogo, Paese"}}`. `focus` decide quale parte resta visibile
  quando la foto è tagliata; `caption` solo se il proprietario dice il luogo. Servono foto
  orizzontali, meglio se larghe 2000 px o più. Il titolo sta in basso a sinistra e il menu
  è bianco in alto: controlla il risultato a larghezza desktop e a circa 390 px.
- **Nuova sezione nel menu**: richiede modifiche a `build.py` (`PAGES`, `NAV`, un metodo
  `page_<chiave>`) e a `content/i18n.json`.
- **Aspetto**: palette, caratteri e la «linguetta» del titolo sono definiti in
  `public/assets/css/site.css`. Il sito non usa cookie, statistiche né risorse caricate da
  altri siti; se questo cambiasse, andrebbe cambiato anche il testo della pagina Privacy.

## Verifica prima di dichiarare finito

Non dire «fatto» finché tutti questi punti non sono veri.

1. `python3 build.py` ha stampato `Built 25 pages into …` senza errori (il numero cambia
   solo se si aggiunge una pagina).
2. La voce nuova è davvero nelle pagine generate, in entrambe le lingue. Cerca una parte
   del titolo:

       grep -rl "parte del titolo" public --include=index.html

   Devono comparire la pagina inglese e quella sotto `public/it/` (per un articolo
   recente o un evento futuro, anche le due home).
3. `git status` mostra soltanto: il file JSON modificato, le pagine rigenerate in
   `public/`, gli eventuali nuovi file in `public/assets/`. Se compare altro (CSS, script,
   `build.py`), fermati: non doveva cambiare.
4. I dati inseriti coincidono carattere per carattere con quelli forniti dal proprietario
   (date, link, DOI, pagine). Nessun campo è stato inventato.
5. Per qualsiasi cosa che cambi l'aspetto: guardala con `python3 build.py --serve` a
   larghezza desktop e a circa 390 px.

## Come una modifica va online

L'hosting è Cloudflare Pages, collegato a questa repository (progetto `paolopecere`,
oggi su `https://paolopecere.pages.dev`; il dominio `paolopecere.it` verrà collegato
seguendo `MESSA-ONLINE.md`). Cloudflare non esegue nulla: pubblica la cartella `public/`
così com'è nel commit. Per questo le pagine rigenerate vanno sempre nel commit.

1. Parti da `main` aggiornato e lavora sul branch della richiesta.
2. Modifica `content/`, esegui `python3 build.py`, fai la verifica qui sopra.
3. Un commit con `content/` e `public/` insieme, messaggio in italiano.
4. Push del branch (mai di `main`).
5. Apri una pull request verso `main`, titolo e descrizione in italiano: che cosa è stato
   aggiunto, in quale pagina compare, quali testi hai tradotto tu.
6. Dopo qualche minuto Cloudflare prepara l'anteprima del branch e ne scrive l'indirizzo
   in un commento o nei controlli della pull request (di solito
   `https://<nome-del-branch>.paolopecere.pages.dev`, con il nome in minuscolo e i
   trattini al posto degli altri simboli). Se lo vedi, dallo al proprietario.
7. **La modifica è online solo dopo il merge.** Il proprietario preme «Merge pull
   request» su GitHub, oppure ti scrive in chiaro di pubblicare e allora fai tu il merge.
   Uno o due minuti dopo il sito pubblico è aggiornato.

Finché la pull request è aperta, di' sempre che la modifica **non è ancora sul sito
pubblico**.

## Stile delle risposte

- Italiano semplice, frasi brevi, niente gergo (non «commit», «build», «JSON»: di'
  «ho salvato la modifica», «ho rigenerato le pagine»).
- Chiudi sempre con un riepilogo: che cosa hai aggiunto (con i dati principali, così può
  controllarli), in quale pagina comparirà, il link alla pull request e che cosa deve
  fare lui per pubblicarla.
- Se hai tradotto un testo, di' quale. Se hai lasciato fuori qualcosa perché mancava un
  dato, di' quale dato serve.
- Se qualcosa non ha funzionato, dillo chiaramente invece di presentarlo come fatto.

Esempio: «Ho aggiunto l'evento del 15 gennaio 2027 alle 18:30, Libreria X, Roma.
Comparirà nella pagina Eventi, fra i prossimi, e in home. Ho tradotto io il titolo in
inglese. Non è ancora online: per pubblicarlo premi "Merge pull request" qui: …»

## Mappa della repository

    content/            i contenuti del sito (si lavora qui)
      papers.json       articoli su rivista, capitoli, recensioni, voci enciclopediche
      books.json        categorie, libri, lista "recent" per la home
      events.json       eventi futuri e passati
      essays.json       saggi e articoli giornalistici
      stories.json      reportage e racconti
      media.json        video e podcast
      site.json         nome, biografia, contatti, social, fotografie di sfondo
      i18n.json         testi dell'interfaccia nelle due lingue, testo della privacy
    build.py            il generatore (non toccare senza conferma)
    tools/images.py     prepara copertine, fotografie e ritratto
    public/             ciò che l'hosting pubblica
      assets/           css, js, font, immagini, documenti (gestiti a mano)
      **/index.html     pagine generate (non modificare)
      _redirects        vecchi indirizzi Jimdo -> nuove pagine
