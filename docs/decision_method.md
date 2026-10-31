# Decision-quality method (stage 6)

The point of this stage is to answer a different question from the fact-check: not *was the
statement true*, but *was the decision sound given what was knowable when it was taken*.

Two decisions can be equally defensible and produce opposite outcomes; two can share an
outcome and differ wildly in quality. The method keeps those axes apart on purpose.

## What gets audited

The twelve decisions both candidates argue about (see `data/claims/decisions.md`), in
descending order of salience:

1. the 2026/2027 budget and the labour-code provision
2. the Kyiv framework agreement (signature, mandate, ratification path)
3. the French proposal on North Macedonia (2022)
4. the Botash contract
5. the NATO counter-drone programme
6. the BDP/BDB capital withdrawal
7. the pardons and the medical commission
8. the caretaker cabinet's appointment and its 78 days
9. the Consultative Council on the Black Sea
10. the UN resolution vote
11. the coalition-of-the-willing posture
12. the campaign's conduct and the government press centre

## Six dimensions, scored 0-3

| dimension | question | 0 | 3 |
|---|---|---|---|
| **Information** | Did the decision-maker have, and use, the facts available at the time? | ignored available warning signs | acted on the best information then available |
| **Authority** | Was the decision within their legal and constitutional power, properly exercised? | acted beyond or against the rules | clearly within power, procedure followed |
| **Alternatives** | Were better options genuinely on the table? | a superior option was available and discarded without reason | no materially better option existed |
| **Reversibility** | How hard was the decision to undo, and how large the downside? | one-way door with severe downside, chosen casually | reversible, bounded downside |
| **Design** | Was there a mechanism to implement, monitor and correct it? | no owner, no review, no correction path | clear owner, milestones, review |
| **Candour** | Did the decision-maker describe the decision accurately afterwards? | misdescribed it to the public | described it accurately, including costs |

`Candour` is where this stage borrows from the fact-check: the dossiers in
`data/factcheck/verdicts.json` are the evidence for whether the later account of the decision
was accurate. A defensible decision described dishonestly is still a candour failure, and a
bad decision described honestly is not.

## Grades

| grade | rule |
|---|---|
| `sound` | no dimension below 2, at least four at 3 |
| `defensible` | no dimension at 0, average ≥ 2 |
| `weak` | one dimension at 0, or average < 2 |
| `indefensible` | two or more dimensions at 0 |

Any dimension scored `unknown` caps the grade at `defensible` and must be listed as an
evidence gap.

## The outcome axis (scored separately, never folded in)

`outcome`: `good` · `mixed` · `bad` · `too_early`, with a one-line factual basis.

The report then classifies each case into the 2×2 that gives the stage its point:

| | good outcome | bad outcome |
|---|---|---|
| **sound process** | deserved success | **bad luck** — the case against outcome bias |
| **weak process** | **luck** — the case against "it worked, so it was right" | deserved failure |

## Bias controls

1. **Information cutoff.** Every dimension is assessed as of the decision date. Sources dated
   after it may describe the outcome but may not be used to argue the decision was wrong.
2. **Two assessors, then adjudication.** Each decision is scored twice, independently, with
   the same rubric; disagreements of more than one point on any dimension are written up, not
   averaged away.
3. **Symmetry.** Every decision gets all six dimensions, whoever took it. No decision is
   exempted because its author is the more sympathetic figure.
4. **No invented alternatives.** "A better option existed" must point to a documented option
   that was actually proposed or available, not one constructed with hindsight.
5. **Sensitivity line.** Each dossier ends with: what single fact, if different, would flip
   the grade.

## Output

`data/decisions/<slug>.json` — dimensions with citations, grade, outcome, 2×2 cell,
sensitivity line, and the evidence gaps. Rendered into `data/decisions/README.md`.
