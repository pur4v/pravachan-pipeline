# References

Two lookup files the skill loads during the **clean** and **structure** stages of
`jain-pravachan-transcript`. They are reference data, not code — read the relevant one
before editing a transcript; don't apply either blindly.

## `corrections.md` — ASR corrections glossary

A curated map of speech-to-text misrecognitions actually observed in Gujarati Jain
pravachan transcripts → their correct Prakrit/Sanskrit spellings. Use it as a
**context-sensitive lookup, not find-and-replace** — the same ASR output can be correct
in one talk and wrong in another (e.g. `ગણી` = the acharya `ગણિ` or the verb "counted").

Organised into seven sections:

1. **Scripture and text names** — agam/payanna/granth titles (e.g. `થાણા સૂત્ર` → `ઠાણાંગ સૂત્ર`).
2. **Monastic conduct and practice** — ogha, muhpatti, kausagga, pratikraman, etc.
3. **Tapas, vows and rituals** — paryushan, paushadh, ayambil, pachchakkhan, sanlekhana.
4. **Cosmology and metaphysics** — graiveyak, tiryanch, kashaya, avadhijnana, etc.
5. **Persons and places** — Trishala, Simandhar Swami, Kurgadu Muni, Palitana, Sametshikhar.
6. **Sutra fragments and gathas** — restore only when the intent is clear (Navkar lines,
   Iriyavahi, "તમેવ સચ્ચં…", the michchhami dukkadam close).
7. **Recurring general slips** — everyday-word mishearings.

Plus a **Numbers written as words** note: ASR drops/splits digits, so check counts against
the standard enumerations (64 indras, 24 tirthankars, 12 devloks, 9 graiveyaks, 5 anuttars,
18 papsthanaks, 17 marans, 72 dreams). If the spoken running total doesn't add up,
reconcile to the standard figure **and say so** in the report.

## `structure.md` — structuring a transcript

How to segment a cleaned discourse into numbered sections.

- **Typical arc** to recognise for fast sectioning: મંગલાચરણ → મૂળ સૂત્રપાઠ → ગ્રંથનો પરિચય →
  મુખ્ય વિષય → દૃષ્ટાંત (stories) → બોધ/ઉપસંહાર → જાહેરાત (announcements) → સમાપન. Not every
  talk has all of these, and they aren't always in order.
- **Headings** name what *happens* in a stretch, not the abstract topic ("કૂરગડુ મુનિ" over
  "તપનું અભિમાન"). Number sequentially; aim for a section every 300–600 words.
- **Q&A**: keep dialogue shape — `<p class="q">` with bold **પ્રશ્ન:** (direct question) or
  **શ્રોતા:** (interjection/partial answer). Keep both turns where the doctrine lands.
- **Announcements**: gather scattered sangh notices into one section near the end and tell
  the user you moved them; keep dates, amounts, timings, visiting acharyas' names.
- **Stories**: give each its own section(s), keep the speaker's character dialogue as quoted
  dialogue.
- **Enumerated material**: set final figures in a `<div class="box">`; if the spoken
  arithmetic doesn't reconcile, use the standard figure and flag the discrepancy.
- **Cut**: unrecoverable garble (say which passage), masked fragments, false starts/filler.
- **Keep** (though tempting to cut): the speaker's jokes/analogies, direct address to named
  people, flagged digressions, and socially conservative passages — render accurately and
  neutrally, don't soften, sharpen, or add commentary.
