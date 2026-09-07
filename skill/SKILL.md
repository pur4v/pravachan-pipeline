---
name: jain-pravachan-transcript
description: Turn raw Gujarati (or Hindi) Jain pravachan / vyakhyan speech-to-text transcripts into clean, readable, sectioned documents and typeset them as PDF or DOCX. Use this whenever the user supplies a discourse transcript — Kalpasutra, Agam or Payanna vachana, Paryushan lectures, katha, or any recorded sermon — and asks to "convert to readable paragraphs", "clean this up", "make it a PDF/doc", or "format this". Also use it when they ask for magazine-style two-column layouts, landscape output, or larger font sizes for Gujarati religious material, and when they ask to fix garbled ASR spellings of Jain technical terms.
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

Write the structured content as an HTML fragment, then run the build script.

The fragment uses only these elements — the script styles them all:

```html
<h1>શીર્ષક</h1>
<p class="sub">ઉપશીર્ષક</p>
<p class="note">(સંપાદકીય નોંધ)</p>
<h2>૧. વિભાગનું નામ</h2>
<p>સામાન્ય ફકરો</p>
<p class="q"><b>પ્રશ્ન:</b> શ્રોતાનો પ્રશ્ન</p>
<div class="verse">ગાથા<br>બીજી પંક્તિ</div>
<div class="box"><p>યાદી કે કોષ્ટક</p></div>
<p class="end">॥ મિચ્છા મિ દુક્કડમ્ ॥</p>
```

Then build:

```bash
python3 scripts/build_doc.py content.html --out NAME
```

The defaults are the approved house layout — **A4 landscape, two equal columns,
18pt** — so most of the time no flags are needed. Override only when asked.

Flags:

| flag | default | notes |
|---|---|---|
| `--format` | `both` | `pdf`, `docx`, or `both` |
| `--size` | `18` | body point size |
| `--columns` | `2` | the 50/50 magazine split. See "Choosing the layout" below |
| `--portrait` | off | A4 vertical; landscape is the default |
| `--out` | required | base filename, no extension |

Run `scripts/setup.sh` once first — it installs the Gujarati fonts and the two Python
libraries. Without `fonts-noto-*` the Gujarati renders as empty boxes.

## Choosing the layout

**Two columns is the default choice for anything long.** A pravachan runs 3,000–6,000
words. Set full width at a readable point size, the lines get so long the eye loses
its place returning to the next one. Splitting the page 50/50 halves the line length
and the document reads like a magazine or a patrika instead of a wall of text.

The script handles this automatically:

- The two columns are **equal width**, with a 9mm gutter and a thin vertical rule
  between them.
- The **masthead spans the full page width** above the columns — title, subtitle,
  editorial note, then a double rule. Text flows into the columns only below that.
  (In DOCX this is done with a continuous section break, which is what makes the
  columns survive the conversion into Google Docs.)
- Headings sit inside the column flow and never strand at the foot of one.
- Verse blocks and boxes never split across a column break.

Picking the numbers:

| situation | flags |
|---|---|
| **standard reading copy** (the approved house layout) | none — defaults do it |
| wants to print and bind vertically | `--portrait` |
| wants more on each page at large type | `--columns 3` |
| short handout, or a plain single flow | `--portrait --columns 1 --size 14` |

**Watch the interaction between size and column width.** Landscape A4 with two columns
gives roughly 13cm per column — comfortable at 18–22pt. Switching to `--portrait`
narrows that to about 85mm, which is about 25 Gujarati characters per line at 18pt:
still readable, but push past 22pt there and lines start breaking mid-compound. At
that point go back to landscape or drop to one column.

**Landscape does not automatically mean fewer pages.** Two wide columns hold roughly
what two narrow portrait columns hold, so the page count barely moves. If the point is
genuinely fitting more on each sheet, use `--columns 3`.

If the user says nothing about layout, just build the default — it is the layout they
already approved. Ask only when they signal something unusual (printing, binding,
projecting, a reader with poor eyesight).

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

1. Page count and layout.
2. The significant term corrections you made (`ASR spelling → correct spelling`),
   grouped, not exhaustive — the notable ones.
3. Anything you dropped, guessed at, or think needs a human eye: garbled proper nouns,
   suspect numbers, gathas you reconstructed loosely. Be specific about which passage.

That third point matters most. The user usually knows this material far better than
you do and can fix a bad guess in seconds — but only if you flag it.
