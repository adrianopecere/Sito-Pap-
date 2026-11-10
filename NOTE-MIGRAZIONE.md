# Note sulla migrazione da Jimdo (novembre 2026)

Cosa è stato riportato dal vecchio sito, cosa è cambiato e cosa resta da controllare.

## Riportato

- Tutti i testi delle dieci pagine del vecchio sito.
- 23 libri con copertina, descrizione e link all'editore.
- 54 articoli accademici (23 su rivista, 23 capitoli, 4 recensioni, 4 voci enciclopediche).
- 84 saggi e articoli giornalistici, 14 reportage, 7 racconti, 22 video, 5 podcast.
- 63 documenti scaricabili (PDF, DOCX, scansioni), ora ospitati sul sito in
  `public/assets/files/`.
- Tutti i 170 link esterni del vecchio sito, tranne quello rotto indicato sotto.
- Le due fotografie del Bromo, la fotografia della pagina About e il ritratto, più dieci
  fotografie di viaggio aggiunte dopo (una per pagina; `dune-tramonto` è di scorta).

## Da sistemare: link che mancavano già sul vecchio sito

1. **«Review of T. Pearce, Pragmatism's Evolution»** (Articoli, 2022): il link del vecchio
   sito puntava a un file sul computer dell'autore (`file:///Users/paolo/Downloads/…`), quindi
   non funzionava per nessuno. Serve il PDF o il link alla rivista.
2. **«Storia del libro e storia della filosofia»** (con L. Del Corso, 2011): sul vecchio
   sito c'era la scritta «download» senza alcun link. Serve il PDF.
3. **«Friedman e l'unità della filosofia»** (Recensioni, 2005): nessun link, come prima.
4. Racconti **«Il dio a venire»** e **«Immersione»**: nessun link, come prima.

## Da confermare

- **Didascalie delle foto**: ho indicato «Monte Bromo, Giava», «Fitz Roy, Patagonia» e
  «Torres del Paine, Patagonia» dove ho riconosciuto il luogo. Le altre foto (altopiano,
  laghi, dune, lago glaciale, terra crepata) sono senza didascalia: basta dire il luogo e
  si aggiunge. Le didascalie sono in `content/site.json`.
- **Risoluzione delle foto**: quasi tutte le foto di viaggio sono larghe circa 1100 pixel
  e sugli schermi grandi risultano un po' morbide. Con gli originali verrebbero più nitide.
- **Biografia**: testo invariato. Dice che l'ultimo libro accademico è del 2020, ma in
  elenco ci sono titoli più recenti: forse va aggiornata.
- **Traduzioni fatte in migrazione, da rileggere**:
  - descrizioni in inglese di 17 libri (l'originale era in italiano);
  - descrizioni in italiano di 4 libri (l'originale era in inglese);
  - descrizione in inglese e in italiano di «El sentido de la naturaleza» (l'originale era
    in spagnolo);
  - biografia in italiano e tutte le voci di menu, titoli e pulsanti.
  Le descrizioni sono in `content/books.json`, il resto in `content/site.json` e
  `content/i18n.json`.
- **Pagina Privacy**: testo nuovo e breve, perché il nuovo sito non usa cookie né
  statistiche. Il vecchio testo parlava di Google Analytics tramite Jimdo e non vale più.

## Cambiato rispetto al vecchio sito

- **Home**: gli «articoli recenti» ora sono i cinque più recenti della pagina Articoli e si
  aggiornano da soli (la vecchia lista era ferma al 2023).
- **Ordine delle liste**: saggi, racconti e articoli sono ordinati per anno, dal più recente.
- **Titoli di libri uniformati**: «La natura della mente. Da Cartesio alle scienze
  cognitive», «Il libro della natura, vol. I» e «vol. II», «Quaestio. Il libro filosofico
  dall'antichità al XXI secolo», «Meccanica quantistica, rappresentazione, realtà»,
  «Demonstrative and Non-demonstrative Reasoning in Mathematics and Natural Science».
- **Doppio PDF**: per «L'io senza soggetto e il soggetto senza io» il vecchio sito collegava
  due file diversi, uno dal titolo e uno dalla scritta «download». È rimasto quello di
  «download»; l'altro non è stato riportato.
- **Link ai social**: tolti i parametri di tracciamento in coda agli indirizzi.
- **Pagine legali di Jimdo** (`/informazioni-legali/`, `/dichiarazione-privacy/`,
  `/impostazioni-dei-cookie/`, `/recesso/`): non esistono più; i vecchi indirizzi
  rimandano alla pagina Privacy o alla home (file `public/_redirects`).
- **Nuova sezione Eventi**, per ora vuota.

## Lasciato com'era

Refusi presenti nei testi originali non sono stati corretti, per esempio «Kant' Construcion
of Nature» e «Zur Ubersetzung» nella pagina Articoli.
