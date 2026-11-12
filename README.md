# paolopecere.it

Sito personale di Paolo Pecere. Sito statico in due lingue: inglese all'indirizzo
principale, italiano sotto `/it/`.

## Come si aggiorna

I contenuti sono nei file della cartella `content/`. Le pagine in `public/` vengono
generate da `build.py` e sono quelle che l'hosting pubblica.

Il modo normale di aggiornare il sito è chiederlo a Claude Code collegato a questa
repository, per esempio:

- «Aggiungi un evento: 15 gennaio alle 18:30, presentazione alla Libreria X di Roma»
- «Aggiungi questo articolo alla lista dei saggi: titolo, testata, anno, link»
- «Metti questa foto come sfondo della pagina Media»

Claude modifica i file in `content/`, rigenera le pagine e apre una pull request: la
modifica va online quando la pull request viene approvata («Merge pull request» su
GitHub). Le istruzioni che segue sono in `CLAUDE.md`.

## A mano

    python3 build.py           # rigenera le pagine in public/
    python3 build.py --check   # controlla solo i contenuti
    python3 build.py --serve   # anteprima su http://localhost:8000

Serve solo Python 3. Dopo ogni modifica vanno salvati nello stesso commit sia i file di
`content/` sia le pagine rigenerate in `public/`.

## Hosting

Cloudflare Pages, collegato a questa repository. Cartella da pubblicare: `public`.
I passi per la messa online e per il dominio sono in `MESSA-ONLINE.md`.

## Note sulla migrazione da Jimdo

Vedi `NOTE-MIGRAZIONE.md`.
