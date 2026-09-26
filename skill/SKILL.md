---
name: jain-pravachan-transcript
description: Turn raw Gujarati (or Hindi) Jain pravachan / vyakhyan speech-to-text transcripts into clean, readable, sectioned documents and typeset them as a print-ready A5 book (PDF + DOCX). Use this whenever the user supplies a discourse transcript — Kalpasutra, Agam or Payanna vachana, Paryushan lectures, katha, or any recorded sermon — and asks to "convert to readable paragraphs", "clean this up", "make it a PDF/doc", "make an A5 book", or "format this". The default output is an A5 print book with an index, a સારાંશ summary and a વિચારનકશો mindmap. Also use it when they ask for magazine-style two-column layouts, landscape output, or larger font sizes for Gujarati religious material, and when they ask to fix garbled ASR spellings of Jain technical terms.
---

# Jain Pravachan Transcript → Readable Document

Raw speech-to-text of a Jain discourse arrives as one enormous unpunctuated block.
It is full of misrecognised Prakrit and Sanskrit terms, audience interjections, and
mid-sentence topic jumps. This skill turns that into a document a person can actually
sit and read, then typesets it.

The work has three stages: **clean → structure → typeset**. Do them in order.

## Stage 1: Clean the text

The transcript is a record of something a real teacher said to a real audience. The
goal is readability, not rewriting. Preserve the speaker's voice, his asides, his
jokes, his direct addresses to people in the hall.

Fix these:

- **Punctuation and sentence breaks.** The single biggest readability win.
- **Garbled technical terms.** ASR mangles Prakrit/Sanskrit badly and consistently.
  Read `references/corrections.md` — it has a large glossary of observed
  misrecognitions mapped to correct spellings, plus the reasoning for the harder ones.
- **Prakrit gathas and sutra fragments.** Restore to standard form when the intent is
  unmistakable (Navkar, Iriyavahi, Jay Viyaray, well-known stavans). Present them as
  verse blocks. If a gatha is too garbled to reconstruct confidently, render it
  approximately and add a small note that it is "as spoken in the vachana".
- **Repeated false starts.** "એ... એ... એ છે ને" collapses to one clean phrase.

Do NOT fix these:

- Colloquialisms, English loanwords ("ટૉપમાં ટૉપ", "સ્ટ્રૉંગ", "બાય ડિફૉલ્ટ"). The
  speaker code-switches constantly and it is part of how he teaches.
- Audience members' names where he addresses them directly — those anchor the talk in
  the room. Drop them only where they interrupt a sentence mid-flow.
- His arithmetic or doctrinal claims. If a number looks wrong, keep it as spoken and
  flag it to the user afterwards rather than silently correcting.

When a passage is too garbled to reconstruct, **leave it out rather than invent it**,
and tell the user which passage you dropped and why. Never guess at a proper noun.

## Stage 2: Structure

Segment the discourse into numbered sections with Gujarati headings that name what
actually happens in that stretch. Read `references/structure.md` for the section
patterns that recur in this genre and how to handle Q&A, announcements, and stories.

Two format decisions:

- **Q&A discourses**: keep the dialogue shape. Mark audience turns with a
  `<p class="q">` paragraph led by a bold **પ્રશ્ન:** or **શ્રોતા:** label. Flattening
  a dialogue into prose loses the teaching rhythm.
- **Enumerated material** (lists of vows, counts of indras, tapas schedules,
  precedence chains) goes in a `<div class="box">`, not inline prose. The speaker
  counts these out loud; on the page they read far better as a small table.

Open with a **મૂળ સૂત્રપાઠ** verse block if the talk begins with a gatha, and close
with `॥ જિનાજ્ઞા વિરુદ્ધ કંઈ પણ કહેવાયું હોય તો મિચ્છા મિ દુક્કડમ્ ॥` if the speaker
ends that way (he usually does).

Add a small italic note under the title stating that paragraphs, punctuation and
headings were added for readability — the reader should know the shaping is editorial.

## Stage 3: Typeset

Write the structured content as an HTML fragment, then run the build script. **The
default output is a print-ready A5 book** — see "A5 book format" below for the full
layout spec. The old magazine layout is still available with `--layout magazine`.

The fragment uses only these elements — the script styles them all:

```html
<h1>વિષયનું નામ</h1>                         <!-- the topic; the number is added -->
<h2>૧. વિભાગનું નામ</h2>                       <!-- numbered section heading -->
<p>સામાન્ય ફકરો</p>
<p class="q"><b>પ્રશ્ન:</b> શ્રોતાનો પ્રશ્ન</p>
<div class="verse">ગાથા<br>બીજી પંક્તિ</div>
<div class="box"><p>યાદી કે કોષ્ટક</p></div>
<p class="end">॥ મિચ્છા મિ દુક્કડમ્ ॥</p>
```

In A5 the book prints only the **"number. topic"** title — never a subtitle, date line
or transcription note — so `p.sub` / `p.note` are ignored. Then author two more parts
**from the talk itself** (see "Authoring સારાંશ and વિચારનકશો"):

```html
<div class="summary">
  <p>…</p> <p>…</p>   <!-- ~5 paragraphs following the talk's arc -->
  <div class="stats"><p><b>એક નજરે મુખ્ય આંકડા</b><br>
      figure<br>figure<br>figure</p></div>
</div>
<div class="mindmap">
  <div class="branch" data-range="વિભાગ ૧–૩">થીમનું નામ
    <div class="leaf" data-sec="૧">એક પંક્તિ</div>
    <div class="leaf" data-sec="૨">એક પંક્તિ</div>
    <div class="leaf" data-sec="૩">એક પંક્તિ</div>
  </div>
  <!-- exactly 5 branches, 3 leaves each, covering every section -->
</div>
```

Then build:

```bash
python3 scripts/build_doc.py content.html --out NAME --number 17
```

Flags:

| flag | default | notes |
|---|---|---|
| `--out` | required | base filename, no extension |
| `--format` | `both` | `pdf`, `docx`, or `both` |
| `--layout` | `a5` | `a5` print book (default) or `magazine` (old A4) |
| `--number` | — | A5: the vyakhyan number for the title |
| `--src-name` | — | A5: original filename; the leading digits become the number |
| `--size` / `--columns` / `--portrait` | 18 / 2 / off | **magazine layout only** |

The number is the leading digits of the source file name
(`9_સમાધિ શતક_23_7_24.docx` → ૯), written in Gujarati numerals. Pass it with
`--number`, or pass `--src-name` and let the script derive it. **If the file name has
no leading number, stop and ask the user for it** — don't guess.

Run `scripts/setup.sh` once first — it installs the Gujarati fonts and Python
libraries. No other tools are needed: the index page numbers for **both** the PDF and
the DOCX are read directly from the WeasyPrint layout (the same layout that produces
the PDF), so the DOCX index numbers match the print master and require no LibreOffice
or Word round-trip.

## A5 book format

This is the default and the approved format. `build_doc.py` implements all of it; the
rules below are the contract.

**Content.** Never remove, shorten or reword the vyakhyan text. The script verifies the
DOCX body is character-for-character identical to the source (whitespace-stripped) and
reports PASS/FAIL — do not verify via PDF text extraction, because Gujarati pre-base
matras like િ extract out of order and give false alarms.

**Output.** Always produce both PDF (print master, WeasyPrint — it shapes Gujarati
conjuncts and supports `target-counter()` for index numbers) and DOCX.

**Page & type.** A5 portrait, single column. Body: Noto Serif Gujarati **14pt fixed**,
line-height 1.35, justified — never drop below 14pt to save pages. Section headings
15pt; index 13pt; સારાંશ 13pt; stats boxes and verses 13pt. Title, headings and mindmap
use Noto Sans Gujarati Bold. Mirrored binding margins: inner 14mm, outer 9mm, top 10mm,
bottom 10mm. Page number on the outer bottom corner (right on odd, left on even).
Running head — the "number. topic" title, 7.5pt grey #9a8a7a, centred — on every page
except page 1.

**Structure, in order:** (1) page 1: title (centred 20pt brown #7A2E00, thin beige rule)
then the અનુક્રમણિકા directly beneath — no separate title page; (2) index: every section
heading with dot leaders and real computed page numbers, plus સારાંશ and વિચારનકશો as
the last two entries; (3) body starts directly under the index, same page, no break;
(4) સારાંશ on a fresh page after the body; (5) વિચારનકશો always the last page, fits on
one page. Never insert blank pages.

**Spacing.** Paragraph gap 3pt. Headings 4mm above / 1.5mm below, brown-gold #D9A066
left bar, kept with next. Stats/figure boxes and verses are tight (each figure on its
own line, no gap; collapse `<br><br>` to `<br>`; never split across pages). Q/listener
lines: italic, small indent, bold brown label.

**Mindmap.** Dark-brown #7A2E00 banner with "number. topic" (white bold 12pt) and
વિચારનકશો (8.5pt). 5 theme branches, each a full-width colour bar (theme white bold
10.5pt left, "વિભાગ ૧–૩" range 7.5pt right). Under each: 3 white leaf boxes with beige
#DDD0C0 border on a 1.2mm coloured spine; each leaf a bold section-number chip + one
line 9pt. Group sections into themes by meaning; 5×3 leaves must cover every section (a
chip may span two, e.g. "૧૫–૧૬"). Branch colours in order: #8C3B12, #1F5673, #7A5C1E,
#3F6B4A, #8A2E5B. Footer: "રંગીન અંક = વ્યાખ્યાનના વિભાગનો ક્રમાંક."

**Delivery.** Name outputs `<NN>_<topic-in-latin>_<date>_A5_book.pdf/.docx`. Report the
page count for both files, which pages સારાંશ and વિચારનકશો land on, and the
text-integrity result. To cut pages, tighten box air / paragraph / heading spacing —
never the text, never below 14pt. Tell the printer: A5 at 100%, no scaling.

## Authoring સારાંશ and વિચારનકશો

These two parts are written by you, from the talk — the script only lays them out.

- **સારાંશ**: about 5 paragraphs following the talk's arc, drawn from the talk itself
  (not invented), plus an "એક નજરે મુખ્ય આંકડા" box of the key figures actually
  mentioned (counts, measures, years, amounts).
- **વિચારનકશો**: group the numbered sections into 5 themes *by meaning*, not by order.
  Each theme gets 3 leaves; every section must be covered. Keep each leaf to one short
  line so it stays on a single line in the box.

## Magazine layout (`--layout magazine`)

The older A4 layout is preserved for when the user explicitly wants a magazine/patrika
look: `--layout magazine` with `--columns` (default 2, equal width, 9mm gutter, thin
rule), `--size` (default 18), and `--portrait` (default is landscape). The masthead
(title/subtitle/note + double rule) spans the full width above the columns; in DOCX
this uses a continuous section break so the columns survive conversion to Google Docs.
Use it only when asked — otherwise build the A5 book.

## Things that will bite you

**Font.** Gujarati needs a shaping-aware renderer. The script uses WeasyPrint (via
HarfBuzz) for PDF, not wkhtmltopdf — wkhtmltopdf's old WebKit silently ignores CSS
columns and shapes Indic conjuncts poorly. Do not swap it back.

**Justification.** In a narrow column, justified Gujarati opens ugly rivers of
whitespace because there is no hyphenation. The script sets ragged-right for
multi-column and justified for single-column. That is deliberate.

**Markdown is not an option** when the user wants the styled look. Markdown cannot
express columns, shading, or centred verse blocks. If someone asks for "a doc" or a
Google Doc, give them the **DOCX** — it converts to Google Docs with the columns and
shaded boxes intact. Markdown only if they explicitly want plain text.

**Do exactly what was asked.** If the user asks for one file, produce one file. This
material comes in long series and it is tempting to batch — don't, unless asked.

## Report back

After building, tell the user in a few lines:

1. Page count for both files, and which pages the સારાંશ and વિચારનકશો land on.
2. The text-integrity result the script reports (PASS/FAIL).
3. The significant term corrections you made (`ASR spelling → correct spelling`),
   grouped, not exhaustive — the notable ones.
4. Anything you dropped, guessed at, or think needs a human eye: garbled proper nouns,
   suspect numbers, gathas you reconstructed loosely. Be specific about which passage.

That third point matters most. The user usually knows this material far better than
you do and can fix a bad guess in seconds — but only if you flag it.
