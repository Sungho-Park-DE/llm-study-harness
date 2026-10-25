---
description: End-of-session review — generate <unit>_review.md, update syllabus progress grid, chain /makeremnote
allowed-tools: Read, Write, Bash
---

You are now in `/makereview` mode (Sprint Stage 7: STORE, end-of-session invocation).

## Workflow

### 1. Identify unit and course
- Course: I2DL / CBDP / FFM / IDA (ask if ambiguous)
- Unit: **naming per course CLAUDE.md** — default week `W{xx}`; **IDA = chapter `C{NN}`** (e.g. `C01`, user-confirmed 2026-06-09). Ask if ambiguous.

### 2. Read previous unit's review (cross-reference)
- Path: `<course>/Reviews/<previous-unit>_review.md`
- If exists: identify 1–2 cross-reference points to this unit's concepts.
- If not exists: skip cross-reference section.

### 3. Check for an existing review file
- Path: `<course>/Reviews/<unit>_review.md`
- If it already exists → **ask the user**: "A review already exists. Overwrite / append / new version (`_v2.md`)?" — never overwrite silently. Proceed per the answer.
- **On overwrite or new-version: carry over the existing `## Review Log` section unchanged** — it is the §3.3 iteration record (written by review sessions, not by this command) and is never regenerated.

### 4. Generate review markdown

Template (constant; LLM uses subset dynamically based on review iteration per Faded Scaffolding, master doc §3.3):

```markdown
# {Unit} Review — {Course}

## Chapter Structure
1. {Topic A}
2. {Topic B}
3. {Topic C}

## Key Concepts (5–7)
- {Keyword 1}
- {Keyword 2}
- ...

## Core derivations & procedures (math-heavy units — names only, NO solutions)
- {e.g. "derive the soft-thresholding operator from the prox definition"}
- ...

## Self-Test Questions

### {Topic A}
1. {question — NO ANSWER}
2. {question}

### {Topic B}
1. {question}

### {Topic C}
1. {question}

## Cross-reference (previous unit, if applicable)
- {previous unit} {concept} ↔ this unit's {linked concept}
```

**Rules**:
- Self-test questions have **NO answers** (Generation Effect protection). Answer key = on explicit request only ("make an answer key" → separated `<unit>_review_answers.md`, 1–3-line skeletons, "open only after an attempt" — master doc §3.2 note 2026-06-13; never by default, never auto-read)
- **Core derivations & procedures**: names only, NO solutions (generation-safe) — populate for math-heavy units (IDA; math parts of I2DL/FFM), omit the section for non-math units. This list is the re-derivation target inventory for §2.7.1 review plans.
- Key Concepts: 5–7 items, English terms
- Questions cover all Chapter Structure topics

### 5. Save the review file
- Path: `<course>/Reviews/<unit>_review.md`
- Use Write tool. Create `Reviews/` directory if not exists.
- **Update progress grid**: in `<course>/syllabus.md`, set the **Lecture** cell to `O` for this unit's row (X → O). See `$STUDY_ROOT/CLAUDE.md` "Progress Tracking". If the row mapping is ambiguous (e.g. FFM slide↔week mismatch), ask the user which row.

> **Review timing is user-managed** (2026-06-11 decision — the former `review_schedule.md` auto-registration and `/morning` briefing are retired): do NOT register concepts to any schedule and do NOT propose review dates. The Self-Test Questions above are the user's self-managed review material; when the user later asks to review a week/concept, run a review session per master doc §2.7.1 plan-first defaults (technique by unit type; material exposure per §3.3). RemNote FSRS card review stays automatic as a separate micro-layer.

### 6. User confirmation
After the review md is saved, wait for user confirmation: "review checked" or similar.

### 7. Auto-chain /makeremnote
**Skip for IDA** — no RemNote there (math course = handwritten GoodNotes; the review md's Self-Test Questions are the review material). For other courses, on user confirmation:
- Generate integrated card drafts across the **entire unit's concepts**, deduplicated: cover only concepts NOT already covered by per-cycle `/makeremnote` invocations in this session (master doc §2.7 duplicate handling).
- Apply `/makeremnote` format (cloze + Q&A mixed, atomic, registration-ready — no rewrite reminder; rewrite optional per master §1.5, 2026-06-12).

Append `[Stage: 7/7 — STORE · end-of-session]` at end of your response.
