# EPUB Bundel Builder

Zet tekstbestanden automatisch om naar één EPUB-bestand, klaar om te lezen in de Boeken-app op iPad of iPhone.

---

## Vereisten

- Python 3.8 of nieuwer
- `pip` (meegeleverd met Python)

De benodigde pakketten (`ebooklib` en `beautifulsoup4`) worden automatisch geïnstalleerd als ze nog niet aanwezig zijn.

---

## Bestandsstructuur

```
epub-bundel/
├── input/          ← Plaats hier je .txt-bestanden
├── output/         ← De gegenereerde bundel.epub verschijnt hier
└── build_epub.py   ← Het script
```

---

## Formaat van de tekstbestanden

Elk `.txt`-bestand in `input/` volgt dit formaat:

```
TITEL: Titel van het artikel
DATUM: 2025-06-01
CATEGORIE: Tools
---
De eigenlijke tekst van het artikel begint hier.

Alinea's worden gescheiden door een lege regel.

- Bullet één
- Bullet twee
```

**Regels:**

| Veld | Verplicht | Uitleg |
|------|-----------|--------|
| `TITEL` | Aanbevolen | Titel zoals die in de EPUB verschijnt. Standaard: bestandsnaam. |
| `DATUM` | Optioneel | Datum in willekeurig formaat (bijv. `2025-06-01`). |
| `CATEGORIE` | Optioneel | Groepeert artikelen in de inhoudsopgave. Standaard: `Algemeen`. |

- Alinea's worden gescheiden door **een lege regel**.
- Regels die beginnen met `- ` worden omgezet naar een opsommingslijst.
- De volgorde in de EPUB is alfabetisch op bestandsnaam — gebruik nummers als voorvoegsel om de volgorde te bepalen (bijv. `01_intro.txt`, `02_deel1.txt`).

---

## Gebruik

```bash
cd epub-bundel
python build_epub.py
```

De EPUB wordt opgeslagen als `output/bundel.epub`.

---

## EPUB naar iPad sturen

### Methode 1 — AirDrop (snel, draadloos)

1. Zorg dat AirDrop ingeschakeld is op de iPad: **Instellingen → Algemeen → AirDrop → Iedereen (10 minuten)**.
2. Klik op de Mac met de rechtermuisknop op `output/bundel.epub`.
3. Kies **Deel → AirDrop** en selecteer je iPad.
4. Accepteer het bestand op de iPad. Het wordt automatisch geopend in de **Boeken**-app.

### Methode 2 — Bestanden-app via iCloud Drive

1. Zet `bundel.epub` in je **iCloud Drive**-map (bijv. via de Finder op Mac).
2. Open op de iPad de **Bestanden**-app en navigeer naar iCloud Drive.
3. Tik op `bundel.epub` — de iPad vraagt met welke app je het wilt openen.
4. Kies **Boeken**. Het boek wordt direct toegevoegd aan je bibliotheek.

### Methode 3 — E-mail of berichtendienst

1. Stuur `bundel.epub` als bijlage naar jezelf (Mail, WhatsApp, Telegram, etc.).
2. Open de bijlage op de iPad en tik op het deel-icoon.
3. Kies **Kopieer naar Boeken**.

---

## Tips

- Wil je meerdere categorieën? Geef elk bestand een andere `CATEGORIE:`-waarde. De inhoudsopgave groepeert ze automatisch.
- De bundel krijgt automatisch de huidige datum als aanmaakdatum.
- De EPUB is geoptimaliseerd voor serif-lettertype en ruime regelafstand — prettig leesbaar op een iPad-scherm.
