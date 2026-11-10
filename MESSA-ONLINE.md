# Messa online: cosa resta da fare

Stato a novembre 2026: il sito è costruito e sta in questa repository. Il vecchio sito su
Jimdo è ancora quello pubblico su `www.paolopecere.it`. Questa è la lista dei passi per
arrivare al nuovo sito sul dominio, nell'ordine in cui vanno fatti. Spuntare le caselle
man mano.

Regola generale: **Jimdo si disdice per ultimo**, quando il nuovo sito risponde già sul
dominio.

## 1. Hosting su Cloudflare Pages (gratuito)

- [ ] Creare un account gratuito su cloudflare.com.
- [ ] Nel pannello: **Workers & Pages**, poi **Create application**, **Pages**,
      **Connect to Git**.
- [ ] Scegliere **GitHub**, accedere come `adrianopecere` e dare accesso alla sola
      repository `Sito-Pap-` (**Install & Authorize**, poi **Begin setup**).
- [ ] Impostazioni di build:
      - Project name: un nome breve, per esempio `paolopecere` (diventa
        `paolopecere.pages.dev`)
      - Production branch: `main`
      - Framework preset: `None`
      - Build command: `exit 0`
      - Build output directory: `public`
- [ ] **Save and Deploy**. Dopo un minuto il sito è visibile su `NOME.pages.dev`.
- [ ] Scrivere qui l'indirizzo: `https://__________.pages.dev`

Da questo momento ogni push su `main` pubblica il sito, e ogni altro branch ha una sua
anteprima su `NOME-DEL-BRANCH.NOME.pages.dev` (il nome del branch in minuscolo, con i
trattini al posto di `/` e degli altri simboli).

## 2. Claude per la gestione quotidiana

- [ ] Sull'account Claude che gestirà il sito, aprire claude.ai/code e collegare GitHub
      accedendo come `adrianopecere`.
- [ ] Installare la Claude GitHub App sull'account GitHub, limitandola alla repository
      `Sito-Pap-` (github.com/apps/claude).
- [ ] Aprire una sessione scegliendo la repository `Sito-Pap-` e fare una prima modifica
      di prova (per esempio aggiungere un evento).

Claude trova le istruzioni in `CLAUDE.md` a ogni sessione: non serve rispiegargli il sito.

## 3. Dominio

Il dominio `paolopecere.it` oggi è registrato tramite Jimdo. Jimdo non lo tiene senza
abbonamento, quindi va spostato presso un altro registrar e poi puntato su Cloudflare.

- [ ] Controllare se esistono caselle email `@paolopecere.it` su Jimdo. Se sì, salvare
      prima posta e contatti: Jimdo avvisa che con il trasferimento non sono più
      accessibili e che le caselle vanno ricreate altrove.
- [ ] Scegliere un registrar che gestisca i domini `.it` e permetta di impostare
      nameserver esterni (il rinnovo costa in genere 10-15 euro l'anno).
- [ ] Su Jimdo, nelle impostazioni del dominio, richiedere il codice di trasferimento
      (AuthCode). Arriva per email all'indirizzo del titolare del dominio.
- [ ] Sul nuovo registrar avviare il trasferimento del dominio con l'AuthCode. Di solito
      richiede qualche giorno. Nel frattempo il vecchio sito resta visibile.
- [ ] Su Cloudflare aggiungere il dominio (**Add a domain**, piano Free). Cloudflare
      indica due nameserver. Farlo prima del passo successivo.
- [ ] Appena il trasferimento è completato, sul nuovo registrar impostare i due
      nameserver di Cloudflare.
- [ ] Su Cloudflare, nel progetto Pages: **Custom domains**, **Set up a domain**.
      Aggiungere prima `www.paolopecere.it`, poi `paolopecere.it`.
- [ ] Quando Cloudflare segna i due domini come attivi, aprire
      `https://www.paolopecere.it/` e controllare: home, una pagina interna, un PDF, la
      versione italiana `/it/`, un vecchio indirizzo come `/books/research/`.

## 4. Chiusura

- [ ] Disdire l'abbonamento Jimdo (controllare prima la data di rinnovo).
- [ ] Sistemare i punti aperti in `NOTE-MIGRAZIONE.md` (tre link mancanti, didascalie,
      traduzioni da rileggere).
- [ ] Quando tutto funziona, cancellare questo file o segnarlo come completato.
