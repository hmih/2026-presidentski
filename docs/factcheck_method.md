# Fact-check method

## Verdict scale

| verdict | meaning |
|---|---|
| `true` | every element of the steelmanned claim holds against the record |
| `mostly_true` | substance holds, a detail is off |
| `mixed` | one element true, another false or unsupported |
| `mostly_false` | the central assertion fails, a fragment survives |
| `false` | contradicted by the record |
| `unverified` | no accessible primary source; state what would settle it |

`deception` is recorded separately and only where the *direction* of a statement is
contradicted by the speaker's own record — e.g. claiming credit for a vote they opposed,
or omitting the fact that changes the meaning of a true statement.

## Rules

1. **Steelman first.** State the strongest reading the speaker could defend, then test that.
2. **Primary over secondary.** Parliament record, law text, official decision, court ruling,
   statistics. News is used to locate primary sources and for chronology.
3. **Every claim gets its best evidence and its best counter-evidence**, both cited.
4. **No both-sidesing.** Asymmetry is reported as asymmetry.
5. **The ex-ante test** (for decisions): judge the decision against what was knowable when
   it was taken, not against the outcome.
6. **Archived links** wherever a live page might change or vanish.
7. **Confidence** per verdict: high / medium / low, with the reason.

## Dossier format

```json
{
  "claim_id": "C-03-03",
  "verdict": "mixed",
  "confidence": "medium",
  "steelman": "the strongest reading of the claim",
  "finding": "what the record shows",
  "evidence": [{"quote": "...", "source": "...", "url": "...", "archive": "...", "date": "..."}],
  "counter_evidence": [...],
  "deception": "none | omission | misdirection | false_credit",
  "notes": "..."
}
```
