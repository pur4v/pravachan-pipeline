# Structuring a pravachan transcript

## The shape of a typical talk

Most discourses in this genre follow a recognisable arc. Recognising it makes
sectioning much faster:

1. **મંગલાચરણ** — Navkar, a Gautamswami doha, a guru shloka. Sometimes pachchakkhan
   for the tapasvis if it is a tapas day.
2. **મૂળ સૂત્રપાઠ** — the Prakrit gathas of the text being read.
3. **ગ્રંથનો પરિચય** — name of the agam, what it means, who composed it, where it sits
   among the 45.
4. **મુખ્ય વિષય** — the doctrinal body. This is where most of the sectioning work is.
5. **દૃષ્ટાંત** — one or more stories. Usually the longest single stretch and the part
   the audience remembers. Give each story its own section, named for its protagonist.
6. **બોધ / ઉપસંહાર** — the application to the listener's life.
7. **જાહેરાત** — sangh announcements: upcoming programmes, names to register, nakro
   amounts, timings.
8. **સમાપન** — મિચ્છા મિ દુક્કડમ્.

Not every talk has all of these, and they are not always in order — announcements in
particular get dropped in wherever the speaker pauses.

## Section headings

Name the section for what happens in it, not for its abstract topic. "કૂરગડુ મુનિ"
beats "તપનું અભિમાન". "ચાર પ્રકારની માલિશ" beats "શારીરિક ચર્યા". A reader scanning
the contents should be able to find the bit they half-remember.

Number them. Sequential numbering helps the reader hold position in a long document.

Aim for a section every 300–600 words. Longer and the reader loses the thread; shorter
and the page turns into a list of headings.

## Handling Q&A

Some discourses — especially the Payanna vachanas — are largely dialogue with the
audience. Preserve that. A question flattened into prose loses the teaching rhythm and
the sense of a room full of people working something out.

```html
<p class="q"><b>પ્રશ્ન:</b> ચોમાસામાં વસ્ત્ર કેમ ન વહોરાવાય?</p>
<p>એનું કારણ છે...</p>
```

Use **પ્રશ્ન:** for a direct question, **શ્રોતા:** for an interjection or a partial
answer shouted from the hall. Where the speaker asks the audience and someone answers
correctly, keep both turns — that exchange is often where the doctrine lands.

## Handling announcements

Sangh announcements are scattered through the talk and interrupt the doctrinal thread.
Gather them into a single section near the end unless the user says otherwise, and
tell the user you moved them. Keep the specifics — dates, amounts, timings, names of
visiting acharyas — people rely on those.

## Handling stories

Give a story its own section, or several if it is long (the Akbar/Hirsuri narrative
easily fills five). Keep the speaker's dialogue as dialogue with quotation marks. He
voices the characters and the drama is doing real teaching work.

## Enumerated material

The speaker counts things out loud and the running total often wobbles. Set the final
figures in a `<div class="box">`:

```html
<div class="box">
<p style="margin:0"><b>ચોસઠ ઇન્દ્રની ગણતરી —</b><br>
ભવનપતિ ૧૦ × ૨ = <b>૨૦</b><br>
વ્યંતર ૮ × ૨ + વાણવ્યંતર ૮ × ૨ = <b>૩૨</b><br>
...<br>
<b>કુલ = ૬૪</b></p>
</div>
```

If the spoken arithmetic does not reconcile, use the standard figure in the box and
mention the discrepancy in your report to the user.

## What to cut

- Mid-sentence garble with no recoverable meaning. Say which passage you dropped.
- Masked or corrupted fragments from the transcription (`ભ****`, `સ******`).
- Repeated false starts and filler.

## What to keep even though it is tempting to cut

- The speaker's jokes and analogies, including the commercial ones (share market,
  hotels, mobile screen time). They are how he reaches this particular audience.
- Direct address to named people in the hall, where it does not break a sentence.
- Digressions he flags as digressions ("આ વિષયની બહારની વાત છે, પણ ઉપયોગી છે").
- Passages that read as socially conservative or that criticise contemporary habits.
  This is a record of what was said. Render it accurately and neutrally; do not soften
  it, sharpen it, or add commentary.
