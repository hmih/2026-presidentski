# Claim extraction schema

Input: one chunk of the speaker-labelled transcript (`data/claims/chunks/chunk_NN.md`),
lines of the form `[MM:SS] speaker: text` (speaker ∈ `moderator|gyurov|iotova`).

Output: JSON `{"claims": [...]}`. One claim = one proposition.

| Field | Type | Rule |
|---|---|---|
| `id` | string | `C-<chunk>-<n>`, e.g. `C-03-07` |
| `t` | string | `MM:SS` of the turn the claim is made in |
| `speaker` | enum | `gyurov` \| `iotova` (never `moderator`) |
| `quote_bg` | string | **verbatim** substring of the chunk text, 5–60 words, no ellipsis edits |
| `claim_en` | string | one-sentence English restatement, no hedging added |
| `topic` | enum | `budget` `energy` `ukraine` `defence` `eu` `judiciary` `media` `pensions` `economy` `campaign` `institutions` `foreign_policy` `other` |
| `type` | enum | `empirical` (fact about the world/record) `causal` (A caused B) `predictive` (will happen) `normative` (ought) `characterization` (motive/competence/character) `procedural` (what was done in a body) |
| `checkable` | enum | `checkable` \| `partly` \| `unverifiable` |
| `decision` | string \| null | the decision the claim is really about, e.g. `"botash contract"`, `"caretaker budget 2023"`; null if none |

## Extraction rules

1. **Atomic.** Split conjunctions: „X направи Y и Z“ → two claims if Y and Z are separately checkable.
2. **Only candidates.** Never attribute to `moderator`; the moderator's statements are questions.
3. **Verbatim.** `quote_bg` must appear character-for-character in the chunk. Copy, never paraphrase.
4. **Skip pure rhetoric**: thanks, greetings, appeals to vote, transitions, insults without
   factual content behind them. If an insult encodes a factual assertion („изградихте кампанията
   си върху лъжи“), keep it as `characterization`.
5. **Numbers and dates are always claims**, even inside an otherwise rhetorical sentence.
6. **Procedural claims matter**: „свикахме КСНС“, „внесохме бюджета“, „гласувахме“ — they are
   checkable against the record and often the crux of the debate.
7. **Normative claims** (`type=normative`) are kept but marked `checkable=unverifiable` unless
   they contain a factual premise, in which case extract the premise separately.
8. **No duplication**: if the same claim recurs later, extract it at first occurrence only and
   note the repetition in `claim_en` as "(repeated)".

## Examples

```json
{"id":"C-01-01","t":"01:47","speaker":"gyurov",
 "quote_bg":"Ниската избирателна активност е следствие на това, че през цялата кампания хората биваха плашени с война, с измислени врагове.",
 "claim_en":"The low turnout was caused by the campaign scaring voters with war and invented enemies.",
 "topic":"campaign","type":"causal","checkable":"partly","decision":null}

{"id":"C-01-02","t":"05:06","speaker":"iotova",
 "quote_bg":"Застанаха колегите от ВМРО, от НДСВ, от партията на доктор Дертлиев",
 "claim_en":"VMRO, NDSV and Dr. Dertliev's party endorsed Iotova's candidacy.",
 "topic":"campaign","type":"empirical","checkable":"checkable","decision":null}

{"id":"C-01-03","t":"07:24","speaker":"gyurov",
 "quote_bg":"Когато сме на масата в Европейския съвет, там има 27 души.",
 "claim_en":"The European Council table has 27 members.",
 "topic":"eu","type":"empirical","checkable":"checkable","decision":null}
```
