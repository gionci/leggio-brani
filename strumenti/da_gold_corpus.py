#!/usr/bin/env python3
"""
da_gold_corpus.py — porta nella biblioteca i brani Mutopia del gold corpus (~/Work/gold_corpus).

1. Gli studi già certificati (gold_corpus/corpus/*.musicxml, esito «certificato» in report/pilota.csv)
   si copiano così come sono.
2. I brani Mutopia in più (EXTRA qui sotto, sorgenti in gold_corpus/fonti/mutopia/<id>/) si convertono
   con le stesse funzioni della pipeline del gold corpus (LilyPond -> eventi -> MusicXML) e gli stessi
   controlli A (andata e ritorno), B (battute), C (MIDI di Mutopia), D (musicxml2ly). Non si scrive
   niente nei report del gold corpus.
3. Si riscrive elenco.json: titolo, autore, opera, file, fonte (edizione stampata), trascrittore
   (chi ha inciso il brano su Mutopia), licenza, link alla pagina Mutopia.

Uso (dalla cartella leggio-brani):
    ~/Work/gold_corpus/venv/bin/python strumenti/da_gold_corpus.py
"""
import csv, json, os, re, shutil, sys

GC = os.path.expanduser("~/Work/gold_corpus")
QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, GC)
os.chdir(GC)
import pipeline, events2xml  # noqa: E402

OPERE = {"Matteo Carcassi": "25 Études mélodiques et progressives, op. 60", "Mauro Giuliani": "Le Papillon, op. 50",
         "Fernando Sor": "24 Exercices très faciles, op. 35"}
EXTRA = {"1877": ("sor_op35_no07", "Fernando Sor")}
LICENZE = {
    "Public Domain": ("Pubblico dominio", "https://creativecommons.org/publicdomain/mark/1.0/"),
    "Creative Commons Attribution-ShareAlike 3.0": ("CC BY-SA 3.0", "https://creativecommons.org/licenses/by-sa/3.0/"),
    "Creative Commons Attribution-ShareAlike 4.0": ("CC BY-SA 4.0", "https://creativecommons.org/licenses/by-sa/4.0/"),
    "Creative Commons Attribution 3.0": ("CC BY 3.0", "https://creativecommons.org/licenses/by/3.0/"),
    "Creative Commons Attribution 4.0": ("CC BY 4.0", "https://creativecommons.org/licenses/by/4.0/"),
}


def testa_ly(id_):
    """maintainer (trascrittore) e titolo dell'opera dall'intestazione del sorgente LilyPond"""
    src = pipeline.main_ly(f"{GC}/fonti/mutopia/{id_}")
    t = open(src, encoding="utf-8", errors="replace").read()
    def campo(k):
        m = re.search(rf'^\s*{k}\s*=\s*"([^"]*)"', t, re.M)
        return m.group(1).strip() if m else ""
    return campo("maintainer"), campo("title"), campo("date")


def sistema_ottava(xml):
    """Alcuni MusicXML del gold corpus sono un'ottava sotto il suono reale (Mi basso = 28 invece di 40):
    succede quando il sorgente LilyPond scrive le note già trasportate per la chiave 8vb. Se la nota più
    bassa è sotto il Mi basso della chitarra, si alza tutto di un'ottava. Ritorna True se ha corretto."""
    t = open(xml, encoding="utf-8").read()
    P = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    note = re.findall(r"<step>(\w)</step>\s*(?:<alter>(-?[\d.]+)</alter>\s*)?<octave>(\d)</octave>", t)
    if not note or min(12 * (int(o) + 1) + P[s] + int(float(a or 0)) for s, a, o in note) >= 38:
        return False
    t = re.sub(r"(<pitch>.*?<octave>)(\d)(</octave>)", lambda m: m.group(1) + str(int(m.group(2)) + 1) + m.group(3), t, flags=re.S)
    open(xml, "w", encoding="utf-8").write(t)
    return True


def pagina_mutopia(r):
    m = re.search(r"/ftp/(.+)/[^/]+$", r["ly"])
    return f"https://www.mutopiaproject.org/cgibin/piece-info.cgi?id={r['id']}" if m else ""


def main():
    tutti = {r["id"]: r for r in csv.DictReader(open(f"{GC}/fonti/mutopia_guitar_all.csv"))}
    rep = list(csv.DictReader(open(f"{GC}/report/pilota.csv")))
    dest = f"{QUI}/brani"
    os.makedirs(dest, exist_ok=True)
    voci = []

    def voce(r, file, autore, esito, controlli):
        trascr, opera, data = testa_ly(r["id"])
        lic, url = LICENZE.get(r["license"], (r["license"], ""))
        num = re.findall(r"\d+", r["opus"] or "")
        nro = re.findall(r"No\.?\s*(\d+)", r["title"] + " " + r["opus"]) or re.findall(r"(\d+)\s*$", r["title"])
        titolo = (f"Studio op. {num[0]} n. {int(nro[-1])}" if num and nro else r["title"])
        return {"id": file[:-9], "titolo": titolo, "autore": autore, "opera": OPERE.get(autore, opera),
                "file": file, "fonte": r["source"] if r["source"] != "Unknown" else "edizione non indicata su Mutopia",
                "anno": data or r["year"], "trascrittore": trascr, "licenza": lic, "licenza_url": url,
                "origine": f"Mutopia n. {r['id']}", "origine_url": pagina_mutopia(r),
                "controllo": f"{esito} ({controlli})"}

    for x in rep:
        if x["esito"] != "certificato":
            continue
        r = tutti[x["id"]]
        file = x["brano"] + ".musicxml"
        shutil.copy(f"{GC}/corpus/{file}", f"{dest}/{file}")
        if sistema_ottava(f"{dest}/{file}"):
            print(file, "alzato di un'ottava")
        autore = "Matteo Carcassi" if "Carcassi" in r["composer"] else "Mauro Giuliani"
        ok = [k for k, c in (("A", "A_andata_ritorno"), ("B", "B_battute"), ("C", "C_ok"), ("D", "D_reimport")) if x[c] == "True"]
        voci.append(voce(r, file, autore, "certificato dal gold corpus", "+".join(ok)))

    for id_, (nome, autore) in EXTRA.items():
        r = tutti[id_]
        ev_path = pipeline.run_lily(r)
        evs = events2xml.read_events(ev_path)
        sc, probs = events2xml.build(evs, f"{r['title']} ({r['opus']})", autore)
        xml = f"{dest}/{nome}.musicxml"
        events2xml.write(sc, xml)
        alzato = sistema_ottava(xml)
        s, xc, attacks = pipeline.note_set_from_xml(xml)
        ec = pipeline.note_set_from_events(evs)
        if alzato:          # il confronto con gli eventi si fa all'altezza degli eventi
            from collections import Counter
            xc = Counter({(k[0], k[1] - 12): v for k, v in xc.items()})
        a_ok = xc == ec
        bad, nbar = pipeline.check_bars(s)
        mc, merr = pipeline.midi_compare(r, attacks)
        c_ok = mc is not None and (mc["mancanti_nel_midi"] == 0 or (
            mc["modo"] == "sequenza" and mc["gruppi_ritrovati"] == mc["gruppi_xml"]))
        d_ok, d_msg = pipeline.reimport_check(xml, ev_path)
        cert = a_ok and not bad and (d_ok or c_ok) and not probs
        ok = [k for k, v in (("A", a_ok), ("B", not bad), ("C", c_ok), ("D", d_ok)) if v]
        print(nome, "A", a_ok, "B", bad[:2], "C", mc or merr, "D", d_ok, d_msg[:200] if d_msg else "", "avvisi", probs[:3])
        if not cert:
            raise SystemExit(f"{nome}: non certificato, non entra nella biblioteca")
        voci.append(voce(r, f"{nome}.musicxml", autore, "certificato con la pipeline del gold corpus", "+".join(ok)))

    voci.sort(key=lambda v: (v["autore"], v["id"]))
    json.dump({"brani": voci}, open(f"{QUI}/elenco.json", "w"), ensure_ascii=False, indent=1)
    print(len(voci), "brani")


if __name__ == "__main__":
    main()
