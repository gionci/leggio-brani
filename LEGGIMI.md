# Leggio · biblioteca dei brani

I brani che il [Leggio](https://gionci.github.io/leggio/) fa leggere, ascoltare e allenare. Una cartella di spartiti
MusicXML più un elenco: niente altro. L'app (repo `leggio`) è separata; legge da qui.

- `brani/` — un file MusicXML per brano;
- `elenco.json` — una riga per brano, nell'ordine in cui compaiono nel menu (raggruppati per autore e opera);
- `strumenti/da_gold_corpus.py` — come sono arrivati qui i brani di oggi (vedi sotto);
- `LICENSE` — CC BY-SA 4.0.

Online: <https://gionci.github.io/leggio-brani/elenco.json>

## Aggiungere un brano
1. Copia il file in `brani/`, per esempio `brani/aguado_op03_no01.musicxml`.
   Va bene un MusicXML «partwise» non compresso (da MuseScore: *Esporta → MusicXML*, estensione `.musicxml`, non `.mxl`).
   Una parte sola (la chitarra), note ad **altezza reale** (Mi cantino = 64, Mi basso = 40, come scrive MuseScore con la chiave 8vb).
2. Aggiungi una riga in `elenco.json`:

```json
{"id": "aguado_op03_no01", "titolo": "Petite pièce n. 1", "autore": "Dionisio Aguado",
 "opera": "8 Petites pièces, op. 3", "file": "aguado_op03_no01.musicxml",
 "fonte": "Mainz, B. Schott Söhne, lastra 2674", "anno": "1830", "trascrittore": "Nome Cognome",
 "licenza": "CC BY-SA 4.0", "licenza_url": "https://creativecommons.org/licenses/by-sa/4.0/",
 "origine": "Mutopia n. 2041", "origine_url": "https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=2041",
 "controllo": "controllato a vista sulla stampa"}
```

3. `git add -A && git commit -m "Aguado op. 3 n. 1" && git push`: in un paio di minuti è nel menu di tutti.
   Prima, se puoi, prova in locale (vedi il LEGGIMI del `leggio`: `node test/browser.js` carica tutti i brani dell'elenco).

Le corde, i tasti e il tempo l'app li ricava da sola dal MusicXML quando il brano si apre: non serve preparare altro.

## Formato di `elenco.json`
`{"brani": [ … ]}`, ogni brano:

| campo | obbligatorio | cosa |
|---|---|---|
| `id` | sì | nome breve, unico, senza spazi; compare nell'indirizzo (`?brano=…`) e tiene i progressi degli alunni: non cambiarlo dopo |
| `titolo` | sì | come appare nel menu |
| `autore` | sì | compositore |
| `opera` | no | raccolta o opera (raggruppa il menu insieme all'autore) |
| `file` | sì | nome del file in `brani/` |
| `fonte` | sì | edizione stampata da cui viene il testo |
| `anno` | no | anno dell'edizione |
| `trascrittore` | sì | chi l'ha inciso/trascritto in digitale |
| `licenza`, `licenza_url` | sì | licenza del file d'origine e link |
| `origine`, `origine_url` | no | da dove viene il file (es. Mutopia n. …) |
| `controllo` | no | come è stato controllato |
| `accordatura` | no | scordatura, corde 1→6 in MIDI, es. `[64,59,55,50,45,38]` (sesta in Re); senza, l'app abbassa la sesta da sola se il brano scende sotto il Mi |
| `tempo_semiminime` | no | tempo in semiminime al minuto, se il file non lo dice |

**Diritti.** Solo brani liberi: pubblico dominio con un'edizione libera (Mutopia, incisioni proprie da stampe antiche).
Niente trascrizioni da edizioni moderne protette (per questo il Rebay del Leggio Sor, dall'edizione Eudora 2014, qui non c'è).

## I brani di oggi (2/11/2026): 58
Tutti da [Mutopia](https://www.mutopiaproject.org), incisi in LilyPond da volontari, convertiti in MusicXML dalla pipeline del
gold corpus (`~/Work/gold_corpus`, controlli: A andata e ritorno, B battute, C MIDI di Mutopia, D rilettura con `musicxml2ly`).
- **Carcassi**, 25 Études op. 60 (25) e **Giuliani**, Le Papillon op. 50 (32): i 57 studi certificati di `gold_corpus/corpus`;
- **Sor**, studio op. 35 n. 7: dalla versione Mutopia (n. 1877, Simrock 1828, inciso da Glen Larsen), scaricata il 2/11 in
  `gold_corpus/fonti/mutopia/1877` e convertita con la stessa pipeline (A, B, C passati).

Licenze dei file d'origine: 32 CC BY 3.0 (Giuliani, Stephen Rhen), 20 CC BY-SA 3.0 (Glen Larsen), 6 pubblico dominio (Jeff Covey).
Tutte permettono di ridistribuire i MusicXML derivati con CC BY-SA 4.0, citando trascrittore e fonte (lo fa la pagina Crediti dell'app).

**Correzione d'ottava.** 20 file del gold corpus (Carcassi e il Sor) erano un'ottava sotto il suono reale (Mi basso = 28):
il sorgente LilyPond li scrive già trasportati per la chiave 8vb. `da_gold_corpus.py` li alza di un'ottava se la nota più grave
sta sotto il Re basso; dopo la correzione il Sor coincide col MIDI di Mutopia senza spostamenti (controllo C). Il controllo D
sul Sor non torna solo perché confronta con gli eventi all'altezza vecchia. **Il gold corpus stesso non è stato toccato**:
il difetto va sistemato là (`events2xml.py`).

Rifare tutto: `~/Work/gold_corpus/venv/bin/python strumenti/da_gold_corpus.py` (riscrive `brani/` e `elenco.json`).
