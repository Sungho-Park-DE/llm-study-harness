# <ALIAS> — <Course title> (<course code>)

<!-- Place at $STUDY_ROOT/<term>/<ALIAS>/CLAUDE.md. Anonymized template distilled from four 2026 SoSe course files.
     Several headings (Lecture Material Learning, Materials Reference Priority, Materials Relationship, Past-Exam Learning Strategy, Exam Signal Strategy) are looked up by name from the master doc (~/.claude/llm-tutor-system.md); keep those headings. -->

Course aliases: <ALIAS>, <nickname>, <full English title>

## Course Info
- Lecturer / TAs: <names — keep contact details out of shared copies>
- Format: <lectures, tutorials, problem sheets, labs>
- Exam: <written / oral, date, allowed aids>
- Submissions: <system, which sheets are graded → Case B while not yet due>

## Unit Naming
- Unit id: **`W{xx}`** (lecture week) by default. For chapter-structured courses use `C{NN}` and say so here, e.g. `Reviews/C01_coverage.md`.

## Assistant Mode
| Task type | Behavior |
|---|---|
| Theory homework (derivations, proofs) | Hints first. Not-yet-due graded sheets → Case B (study-root CLAUDE.md): parallel problem + attempt review, no submittable answer |
| Coding from scratch / debugging | Direct working answer with shape comments |
| Paper discussion (ad-hoc) | Contribution → method → result → limitation. Assignment write-ups use master §7.1 |

## Lecture Material Learning
→ Follow the **LLM Tutor System** (`~/.claude/llm-tutor-system.md`) Sprint 7-stage workflow.

Course-specific reinforcement (optional, read at Sprint entry per master §1.15). Examples from the author's courses:
- Math-heavy course: finer Stage 3 decomposition, aggressive §1.7 prerequisite checks, end each step with "OK so far?". **Proof mode** (§2.3 row) — after the one-time SE training block, append "— done {YYYY-MM-DD}" here.
- Architecture-heavy course: inline diagrams (§1.9-A), shape annotations such as `B, T, C`.
- Systems course: name the trade-offs (CAP, latency vs throughput, scale-up vs scale-out) in Stage 3.

## Materials Reference Priority
<!-- Only if it differs from the study-root default (Slides → Tutorials → Homeworks). -->
1. `<primary source, e.g. Slides/md/<lecture-notes>/>` — PRIMARY
2. `<cross-reference source>`
3. `Homeworks/<name>/<name>.md`
4. `past_exams/analysis/concepts.md` — on request only
5. `Homework_Solution/` — opt-in only (state any exception here)

## Materials Relationship
> Consulted by SCAN (§2.1) and Stage 4 (§2.4): "for this unit, which materials, in which role".

### Folder roles
- `<folder>` — <role, naming quirks, what is intentionally missing>

### Matching rules (applied at runtime — verify by content, never trust numbers)
- **Unit id**: <W{xx} | C{NN}>; numbering offsets: <e.g. sheet "Week N" = lecture W(N-1)>
- **Tutorials / sheets**: content-check a ±1 window around the unit
- **Role assignment**:
  - concept absent from slides → **concept-add** (SCAN coverage)
  - practice of a slide-present concept → **applied-practice** (Stage 4 source)
  - pure prerequisite → **refresh on demand** (§1.7), not coverage
- **Missing files**: <which solutions were never published — missing = normal, do not generate>

## Past-Exam Learning Strategy
<!-- Courses with past exams. Feeds §2.7.1 review plans and §7.2 op 3 priority view. -->
- Sample: n=<N> sittings, examiners <…> → signal strength <weak/informative>
- Tier 1 topics: <…> · Tier 2: <…>
- Holdout for the timed mock (§2.7.2 / §7.2 op 4): <paper id | none — reason>

## Exam Signal Strategy
<!-- Courses WITHOUT past exams, instead of the section above. -->
- Primary exam signal = <problem sheets + tutorials>; coverage stays the whole lecture
- Priority view = weaklog only (Tier factor skipped explicitly, §7.2 op 3)

## Terminology & Rendering
- <e.g. math terms stay in English> · <e.g. use `\Vert` for norms>

## Current Status
- <short, dated status lines — progress lives in syllabus.md>
