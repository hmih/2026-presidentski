# Transcript notes

## Source

| Field | Value |
|---|---|
| Video | `vZzeuZMG8yo` — „БНТ организира единствения дебат между Илияна Йотова и Андрей Гюров“ |
| Channel | Българска Национална Телевизия БНТ |
| Uploaded | 2026-10-29 |
| Duration | 7162 s (1:59:22) |
| Retrieved | 2026-10-30 |
| Audio SHA-256 | `4062fab0a4fe9c76d8844d49344f200a23a3909a1d131d538f0bb2ee2ed80157` (bestaudio m4a, 110.5 MB) |
| Moderator | Поли Златарева (BNT) |

The media itself is not committed (see `.gitignore`); rebuild with:

```bash
.venv/bin/yt-dlp -f bestaudio -o data/raw/debate.%(ext)s "https://www.youtube.com/watch?v=vZzeuZMG8yo"
.venv/bin/python scripts/decode_audio.py data/raw/debate.m4a data/raw/debate.16k.wav
```

## Coverage

**`00:00`–`08:20` of the video is not transcribed.** It is the intro montage/music bed
(YouTube's own auto-captions also start at 08:20). A first ASR pass over the full file
produced repetition loops there ("Екатерина Екатерина…", "Абонирайте се!"), so the audio
was trimmed to 08:00. All transcript timestamps are relative to **08:00 of the video**;
add 8:00 to map onto the YouTube timeline.

## ASR

`whisper.cpp` built from source, model `ggml-large-v3-turbo-q5_0` (547 MB), Bulgarian,
beam 5, `-mc 0 -sns`, Silero VAD, glossary prompt (candidate names, БНТ, ЦИК, балотаж).
4 cores, RTF ≈ 0.55 (≈70 min for 111 min of audio).

Audio preparation now uses **ffmpeg** (`scripts/prepare_audio.sh`): `-ss 480 -ac 1 -ar 16000`.
A `loudnorm` variant was tested and rejected — it raises the noise floor, so Silero VAD passes
far more audio and the ASR RTF degrades from 0.55 to 1.36 (≈2.4× slower) for no measurable
word-accuracy gain.

Raw output: `raw_asr.json` / `.srt` / `.vtt` (unmodified, before diarization).

## Speaker assignment

Two attempts:

1. **Window-level k-means** (`scripts/diarize.py`, 1.5 s windows, MFCC + Viterbi) worked on
   a 20-minute slice but collapsed on the full file — every cluster came out at ~180 Hz,
   i.e. it had split on acoustic conditions, not voices.
2. **Utterance-level nearest-centroid** (`scripts/assign_speakers.py`) — the version used.
   Features: mean/std of 19 MFCCs per segment + YIN f0 (weight 3×). Anchors taken from long
   single-speaker stretches of the opening round:

   | Anchor | Window | Basis |
   |---|---|---|
   | moderator | 60–78 s | greeting + first question |
   | gyurov | 90–155 s | first answer (moderator: „Първи е господин Гюров“) |
   | iotova | 178–225 s | second answer (starts „Госпожо Златарева, позволете ми…“) |

Verification is independent of the classifier: YIN f0 medians after assignment are
**219 Hz** (moderator), **120 Hz** (Gyurov), **189 Hz** (Iotova); only 18 of 1909 segments
sit on the wrong side of the 155 Hz male/female boundary.

**Caveat:** anchors are assumed, not adjudicated. If Gyurov/Iotova were swapped, every
turn label would be wrong while the text stayed the same.

A second pass added a **pitch gate** (f0 < 155 Hz ⇒ Gyurov) plus two EM iterations that
re-estimate the three centroids from confident segments. Agreement with the first pass is
95 %; low-margin segments fall from 262 to 208.

Totals: moderator 17.9 min, Gyurov 41.2 min, Iotova 43.1 min (of 111 min).

## Turns

1909 ASR segments → 381 turns (merge same speaker, gap < 1.5 s). A turn is flagged `⚠`
when more than 40 % of its segments are low-confidence (centroid margin < 0.12 or f0 on
the wrong side of 155 Hz). **78 of 381 turns are flagged**, concentrated in cross-talk.

## Corrections applied

Automatic, conservative, names and terms only (see `FIX` in `scripts/merge_turns.py`):

| Wrong | Fixed |
|---|---|
| Слатарева | Златарева |
| Иллена / Илена / Иляна / Елена Йотова | Илияна Йотова |
| Ятова, госпожо Йото | Йотова |
| господин Дюров / Гиров / Георс / Геров / Геов / Гио / Волч / Григо / Бюров | господин Гюров |
| Балутаж / Болотаж | балотаж |
| Ботъш | Боташ |
| Сен Василев | Асен Василев |
| Изривове | Взривове |
| Русула Фон Дерлайн | Урсула фон дер Лайен |
| даначна, удобрили, Заговядайте, Имато, Госпожото, Бърс отговор, жреби и | данъчна, одобрили, Заповядайте, Имате, Госпожо, Бърз отговор, жребий |

The single dominant error pattern was the moderator addressing „господин Гюров“.

## Proper-noun sweep

All mid-sentence capitalised tokens with a rare lowercase form were extracted
(`scripts/proper_nouns.py`) and adjudicated against the debate context. 12 name/term
errors were fixed beyond the earlier list:

| Wrong | Fixed | Basis |
|---|---|---|
| Гиро, Григо, Андрей Гиров, Гилов | Гюров | address forms + BTA |
| Лиотова, Ляна, Елена | Йотова, Илияна | address forms |
| ОНЕ, ООНЕ | ООН | „Общото събрание на ООН“ |
| Европейския СИОС / СИУС | Европейския съюз | collocation |
| ДПСНО възначало | ДПС в началото | party name |
| ББ за развитие | ББР | bank name |
| с първите ВИО отговори | с първите ви отговори | large-v3 agreed |
| Скопия | Скопие | city name |

Fixes are case-insensitive because the ASR capitalises sentence-initially („Господин
Гиров“ vs „господин Гиров“).

**Left unresolved** — context insufficient, deliberately not guessed:
„Дудингиов“, „Некова“, „Сен Валериан“, „РЕС“, „Ано“.

## Number verification (large-v3 cross-check)

Seven passages carrying checkable figures were re-transcribed with `ggml-large-v3-q5_0`
(slower, higher-capacity model) on ffmpeg-sliced clips:

| Claim | Timestamp | Second model |
|---|---|---|
| „цена от 220 хиляди евро“ (NATO drone veto) | 19:41 | confirmed verbatim |
| „400 милиона долара“ owed under the Botash contract | 32:21 | confirmed verbatim |
| „20 дни преди изборите“ (agreement signed) | 27:49 | confirmed verbatim |
| „издържим 24 часа“ (Warsaw Pact strategy) | 35:14 | confirmed verbatim |
| „за 13 години“ (Botash term) | 28:59 | model heard „за 10 години“ — **conflict, unresolved** |
| moderator addressing „господин Гюров“ | 07:21 | also mangles it („Гиров“), confirming the error class |

Residual risk is concentrated in numbers spoken quickly or under crosstalk. The 13-vs-10
year conflict should be resolved against the published Botash contract before use.

## Consensus check (turbo vs large-v3)

All 68 uncertain turns (11.8 min of audio) were re-transcribed with `large-v3-q5_0` on
ffmpeg-sliced clips; output is kept in `v3_spans.txt`.

Findings:

- **No systematic text defect surfaced.** Where the two models differ it is mostly a
  window artefact (v3 transcribes the padded ±3 s and the neighbouring speaker), not one
  model being right and the other wrong.
- **Both models mangle the same proper names.** large-v3 also hears „Слатарева“ and
  „Господин Гилов/Гиров“. The name corrections therefore rest on **external sources**
  (BTA, marica.bg), not on acoustics — that is the honest provenance.
- **The 8-minute intro is hallucination-prone in both models**; large-v3 invented
  „Абонирайте се на нашия канал!“ exactly where turbo looped. Keeping it out of the
  transcript was correct.

A word-level consensus would need token timestamps from both models; that was not worth
the extra hours given how little the two disagree on content.

## Known issues

- Overlapping speech is assigned to one speaker; interjections under ~1 s are unreliable.
- Numbers, dates and sums are **not** verified against audio — treat them as provisional
  until checked against sources.
- Party and institution names are only partly normalised (e.g. „ДПСНО“ left as-is).
- Punctuation is the ASR's, not a faithful rendering of speech.
- The first ~8 minutes (intro) are outside the transcript.
- Speaker mapping is corroborated externally: BTA's headline „Излезте и гласувайте,
  заведете някой с вас, призова Андрей Гюров“ matches the line the transcript attributes
  to Gyurov at 02:48."

## Regenerating

```bash
.venv/bin/python scripts/assign_speakers.py data/transcripts/raw_asr.json data/raw/debate.trim.16k.wav data/transcripts/turns
.venv/bin/python scripts/merge_turns.py data/transcripts/turns.json data/transcripts/transcript
```
