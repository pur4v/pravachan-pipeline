# Jain scripture verifier reference

Use this to **verify** a cleaned transcript / typeset fragment against canonical Jain
sources before it is finalized. Pair it with `corrections.md` (term-level ASR fixes).
Goal: catch factual and canonical errors the ASR + first pass may have introduced —
NOT to rewrite the speaker's own teaching. Flag, correct where certain, note where unsure.

## What to check (in priority order)

1. **Gathas / sutras quoted as verse** — when the speaker recites a known Prakrit/Sanskrit
   text, it must match the standard mula-patha. Verify against the canonical forms:
   - **Navkar (Namaskar) Mantra**: `નમો અરિહંતાણં / નમો સિદ્ધાણં / નમો આયરિયાણં /
     નમો ઉવજ્ઝાયાણં / નમો લોએ સવ્વસાહૂણં` … `પઢમં હવઈ મંગલં`.
   - **Karemi Bhante**: `કરેમિ ભંતે! સામાઇયં, સાવજ્જં જોગં પચ્ચક્ખામિ …`.
   - **Namutthunam (Shakrastava)**: `નમુત્થુ ણં અરિહંતાણં ભગવંતાણં …`.
   - **Tikhutto, Iriyavahiyam, Logassa, Dashvaikalik gathas** — restore to standard form;
     if the ASR is too garbled to be sure, keep the recognizable fragment + a `note`.
   - **Tattvartha Sutra**: `સમ્યગ્દર્શનજ્ઞાનચારિત્રાણિ મોક્ષમાર્ગઃ` (1.1).
   Do NOT invent a full gatha from a garbled fragment — reconstruct only to the known
   canonical text, and mark loose reconstructions with `<p class="note">`.

2. **Proper nouns — Tirthankaras & canon**:
   - 24 Tirthankaras in order: ઋષભ(આદિનાથ), અજિત, સંભવ, અભિનંદન, સુમતિ, પદ્મપ્રભ, સુપાર્શ્વ,
     ચંદ્રપ્રભ, સુવિધિ, શીતલ, શ્રેયાંસ, વાસુપૂજ્ય, વિમલ, અનંત, ધર્મ, શાંતિ, કુંથુ, અર, મલ્લિ,
     મુનિસુવ્રત, નમિ, નેમિ(અરિષ્ટનેમિ), પાર્શ્વ, મહાવીર. Fix mis-ordered/misheard names.
   - Ganadharas, Agams (દ્વાદશાંગી; the 45 આગમ), gacchas, acharyas — check spellings against
     `corrections.md`; if a name is unrecoverable, render the role (e.g. "પધારેલા મહાત્મા")
     rather than guessing.

3. **Canonical numbers** — verify the standard figures and flag deviations (keep as spoken
   but add a `note` if they differ):
   - Panch kalyanak (5), 14 svapna (Digambara 16), 34 atishaya, 8 pratiharya, 12 anga /
     14 purva, 18000 shilanga, 22 parishaha, 24 Tirthankaras, 63 shalaka-purush,
     Mahavir: 30 yrs grihasth → 12.5 yrs sadhana → 30 yrs kevali (nirvana age 72),
     chyavan→janma standard gestation, etc. When the speaker's number differs from the
     canonical figure, keep his but add `<p class="note">` noting the standard.

4. **Doctrinal terms** — samyaktva, ratnatrayi, nav-tattva, shad-dravya, leshya, gunasthanak,
   nikshepa, saptabhangi/anekant, kashaya, etc. must be spelled and used correctly.

5. **Transcript integrity** — no foreign discourse bleeding in, no NotebookLM UI text
   ("Create an Audio Overview…"), no duplicated paragraphs, no dropped closing (michhami
   dukkadam / mangalik) if the speaker gave one.

## Verifier verdict format
Return: `VERDICT: clean` OR `VERDICT: fixed` (list the corrections applied) OR
`VERDICT: flagged` (list issues you could not safely fix, for a human). Never change the
speaker's opinions, stories, asides, jokes, or code-switching — only canonical/factual errors.
