# 2026-presidentski

Research repository for the **2026 Bulgarian presidential election debate** between
**Andrey Gyurov** and **Iliana Iotova**: what they said, what they claimed, which
narratives they competed over, whether the claims hold up against the record, and —
separately — whether the decisions behind those claims were *good decisions* given what
was knowable at the time they were made.

> **Status:** scaffold. The methodology, data model, and source list are defined here;
> artefacts are being produced stage by stage. See [Roadmap](#roadmap).

---

## Why this repository exists

Election debates are usually scored on two things that get mixed together: whether a
statement was **true**, and whether the speaker's **record was good**. Both matter, and
they are not the same question. A decision taken with the information, legal constraints,
and coalition arithmetic available at the time can produce a bad outcome and still be a
sound decision — and vice versa. Judging decisions only by how they turned out is
*outcome bias*; it rewards luck and punishes defensible choices made under uncertainty.

This project therefore runs **two independent tracks** over the same debate:

1. **Fact track** — what is checkably true or false in each candidate's claims, measured
   against primary sources (parliamentary votes, budgets, statistics, court rulings,
   official records).
2. **Process track** — for the decisions those claims refer to, what the decision-maker
   knew, what they were empowered to do, what alternatives existed, and how the choice
   looked *ex ante*.

The two tracks are reported side by side and never collapsed into a single score. A claim
can be **true** while the underlying decision was **poorly reasoned**, and a decision can
be **well reasoned** while its outcome was **bad**.

## Subjects

| Candidate | Public record used for verification |
|---|---|
| **Andrey Gyurov** (Андрей Гюров) | Deputy PM & Finance Minister (2021–2022); caretaker Prime Minister (2022–2023); parliamentary votes and government decisions in that period |
| **Iliana Iotova** (Илияна Йотова) | Vice President of Bulgaria (2017– ); re-elected 2021; EU and foreign-policy portfolio; public statements and votes in that role |

Roles and dates are recorded here as a working profile and are themselves verified against
primary sources in `data/subjects/`.

## Research questions

1. What **atomic claims** does each candidate make, and which of them are checkable?
2. Which **narratives** (causal stories, villains, achievements, warnings) does each
   candidate advance, and how do those narratives **evolve** across the debate — what is
   set up early, reinforced, abandoned, or reversed?
3. What does the **primary record** say about each checkable claim?
4. For claims about decisions: what was the **decision situation** — information set,
   legal and constitutional constraints, time pressure, coalition arithmetic, available
   alternatives?
5. Where the two candidates **disagree about facts**, is the disagreement empirical,
   definitional, or normative?
6. Which claims are **unfalsifiable or unfalsifiable-as-stated**, and how should that be
   labelled rather than scored?

## Pipeline

Each stage writes a versioned artefact under `data/` so any conclusion can be traced back
to a timestamp in the video and a source URL.

### 0. Source capture and provenance
- Acquire the debate video with `yt-dlp`, preserving metadata (channel, upload date,
  duration, video ID) and a content hash.
- Record the exact URL, retrieval time, and — where possible — a Web Archive snapshot.
- The video itself is **not redistributed** in this repository; only metadata, hashes,
  and derived transcripts/quotations under fair use.

### 1. Transcription and speaker segmentation
- Bulgarian ASR (Whisper-class model, `large-v3` or better), followed by **human
  correction** of a sample plus all passages that will be quoted.
- Speaker diarization, then manual reconciliation against known speakers (two
  candidates plus moderator/panel).
- Output: time-aligned turns — `speaker`, `start`, `end`, `text_bg`, `confidence`,
  `needs_review`.

### 2. Claim extraction
Split turns into **atomic claims**, one proposition each, with:
- verbatim Bulgarian quote, timestamp range, speaker;
- working English translation (marked as translation, not source);
- type: `empirical` · `causal` · `predictive` · `normative` · `characterization` ·
  `procedural` (what was said/done in a body);
- checkability: `checkable` · `partly` · `unverifiable`;
- the decision, if any, the claim is really about.

### 3. Narrative trajectory analysis
- Identify narrative units: problem definition, culprit, remedy, achievement, warning.
- Track salience and framing over debate time: which narratives are opened, escalated,
  conceded, or dropped.
- Note **rhetorical moves** — whataboutism, false dilemma, appeal to fear, credit
  claiming, unfalsifiable hedging.
- Output: a per-candidate narrative map plus a timeline of shifts.

### 4. Evidence gathering
Primary sources first, commentary second.

- **Parliamentary record:** National Assembly open data (`parliament.bg`) — bills,
  committee reports, plenary voting records (by name/group), attendance, quorum;
  coalition and group composition over time.
- **Government and budget:** Council of Ministers decisions, decrees, official gazette
  (*Държавен вестник*), budget laws and executions, audit reports (Сметна палата).
- **Statistics:** NSI (НСИ), Eurostat, BNB, employment and inflation series.
- **Legal:** Constitutional Court decisions, court judgments, EU infringement and
  Commission documents.
- **Media:** established Bulgarian outlets plus international coverage, used for context
  and for checking what was publicly known *at the time*.

For every source: title, publisher, date, author, URL, **archived URL**
(`web.archive.org` preferred, `archive.ph` secondary), access date, and a one-line note on
why it is authoritative for this claim.

### 5. Fact-checking
- Verdict scale: `true` · `mostly true` · `mixed` · `mostly false` · `false` ·
  `unverifiable` · `not a factual claim`.
- Every verdict states: the claim as checkable, the evidence, the strongest
  counter-evidence, the reasoning, and the residual uncertainty.
- **Steelman rule:** the most defensible reading of the claim is checked, not the
  weakest.
- Source-reliability tier recorded per source; no verdict rests on a single secondary
  outlet.

### 6. Decision-quality analysis (separate from outcomes)
For each decision referenced in a checkable claim:
- **Information set at the time** — what was known, what was unknowable, what was
  suppressed or ignored.
- **Authority and constraints** — constitutional powers, coalition agreements, EU and
  fiscal rules, court orders, deadlines.
- **Alternatives** — what else was genuinely available, and their costs.
- **Reversibility and downside** — how bad the worst case was, and whether the choice
  could be undone.
- **Process score** — `sound` · `defensible` · `weak` · `indefensible`, justified
  independently of the observed result.

The realised outcome is recorded on a **separate axis** and is explicitly excluded from
the process score.

### 7. Reporting
- Per-claim dossiers (`data/claims/`).
- Per-candidate narrative trajectories (`data/narratives/`).
- Cross-candidate disagreement map: empirical vs. definitional vs. normative.
- A final report with tables, source appendix, and method notes.

## Planned repository layout

```
data/
  raw/           video metadata, hashes, source manifests
  transcripts/   time-aligned turns (BG) + review flags
  claims/        atomic claims, one file per claim or per debate segment
  narratives/    narrative units, trajectories, timelines
  evidence/      per-claim source bundles, with archived URLs
  votes/         parliamentary voting extracts used as evidence
  subjects/      candidate profiles, verified roles and dates
docs/
  method.md      detailed method, verdict rubric, decision-quality rubric
  sources.md     master source list with reliability tiers
  findings/      report drafts
```

## Methodological commitments

- **Separate fact from evaluation.** Verdicts are about checkability, not about who
  "won".
- **No outcome bias.** Decision quality is assessed on the ex-ante situation; results are
  reported but not used to grade the decision.
- **No false balance.** Where the record is one-sided, the report says so.
- **Traceability.** Every quoted line maps to a timestamp; every verdict maps to archived
  sources.
- **Charity where ambiguous.** Ambiguous claims get the reading their author would
  endorse, and the ambiguity itself is reported.
- **Uncertainty is stated, not hidden.** `unverifiable` is a legitimate outcome.

## Threats to validity

- Bulgarian ASR and diarization errors, especially on overlapping speech and names.
- Translation loss between Bulgarian and English; the Bulgarian text is authoritative.
- Web sources decay; archived copies may be partial or post-edited.
- Parliamentary data is often messy (group changes, re-votes, procedural votes that do
  not express policy preference).
- The debate is one artefact; it is not treated as a full account of either record.

## Tooling

- `yt-dlp` for video/metadata capture.
- Whisper-class ASR (Bulgarian) + `pyannote`-style diarization.
- Plain text/Markdown + CSV/JSON artefacts; scripts kept small and readable.
- Archive.org and archive.today for source permanence.

## Roadmap

- [ ] Capture debate video, metadata, and archived source URL
- [ ] Produce and human-correct the transcript with speaker turns
- [ ] Extract and classify atomic claims
- [ ] Build narrative trajectory map for both candidates
- [ ] Assemble parliamentary voting dataset for the referenced period
- [ ] Collect and archive primary sources per claim
- [ ] Fact-check all `checkable` claims
- [ ] Run decision-quality analysis on referenced decisions
- [ ] Publish final report + source appendix

## Contributing

Corrections are welcome, especially: transcript fixes with timestamps, better or more
authoritative sources, archived links that outlive live pages, and challenges to a verdict
that come with counter-evidence. Open an issue with the claim ID and the source.

## License

[AGPL-3.0](LICENSE). Quotations from the debate and from third-party sources remain the
property of their respective rights holders and are used for criticism, review, and
research.
