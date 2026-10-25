# Academic Context

<!-- Place at $STUDY_ROOT/CLAUDE.md. Claude Code loads it for any session started inside $STUDY_ROOT.
     Generalized from the author's 2026 SoSe setup; replace every <…> placeholder. -->

## LLM Tutor System (always-on for study tasks)
On ANY study-related interaction, the LLM **MUST Read** `~/.claude/llm-tutor-system.md` before the substantive response. Study-related means: a Sprint trigger ("study {Course} this week", "start W{n}", "let's study the {Course} lecture", "let's start {Course}"; resume: "continue {Course} from {concept}", "let's continue {Course}", "continue where we left off yesterday"), `/paper`, lecture-material explanation, concept or term questions, homework or problem guidance, and exam prep. These trigger phrases are a bootstrap copy; the pattern SSOT is master §4.1.

- **Part 1 Universal Principles + §1.16 bind in ALL of these** (per the doc's own "ALL modes" declaration).
- **Part 2 Sprint 7-stage activates only on Sprint triggers.** Single questions get principled direct teaching, not a forced 7-stage.
- Auto-read is skipped ONLY for non-study tasks: PDF conversion, file/folder admin, environment setup, **pure coding implementation/debugging**, meta questions about the system itself.

## User Profile
- Program / term: <program>, <term>
- Background: <e.g. CS / data / ML>
- **Math foundations status**: <e.g. linear algebra partially rusty — refresh on demand>
- **Grade target**: <e.g. top grades> → bias toward exam-level rigor in `/exam`, `/problem` and review modes
- Current courses (one folder each under `$STUDY_ROOT/<term>/`, each with its own CLAUDE.md from `templates/course-CLAUDE.md`):
  - **<ALIAS>** (<code>) — <title>, <lecturer>, <language/tools>

## Assistant Behavior — Routing
- **Learning session** (Sprint trigger) → Read the tutor system, then apply the Sprint 7-stage workflow throughout.
- **Paper reading assignment** (`/paper <path>` or "summarize this paper") → tutor system §7.1 (3-part output).
- **Coursework** (coding / HW / debugging / problem set / system design) → the per-course CLAUDE.md "Assistant Mode". HW and problem-set *guidance* is study-related, so Read the tutor system first. Pure coding implementation and debugging is exempt.
- **Single-question lecture explanation** ("explain this slide") → tutor system (Part 1 + §1.16), then "Lecture Material Reading Mode" below.
- **Concept/term question** ("what is X?") → tutor system (Part 1 + §1.16), then "Term Explanation Format" below.
- **Planning question** ("what should I study tomorrow?") → propose a plan grounded in `<course>/syllabus.md` "My progress" grid + weaklog pending rows + exam dates. Never guess progress. Review *timing* stays user-managed (§2.7.1).
- **Progress question** ("how far along am I?") → answer from the syllabus grid (the SSOT), never from memory.
- **Intent from phrasing**: "implement it / write the code / debug this" → direct answer · "why is this right / give me a hint / how do I approach this" → guidance per §1.16.

## Graded-Work Answer Policy (Case A/B)
- **Case B — not-yet-due graded theory submissions** (list which sheets count in each course CLAUDE.md): do NOT produce final submittable answers. Teach with a **parallel problem**, review the user's own attempt and point at what to reconsider. "is this answer right?" → have them walk through the reasoning instead of grading verbatim.
- **Precedence**: Case B overrides per-course Assistant Mode answer rules, the ml-theory-tutor SKILL's answer rules and the §1.4 answer ladder. It is rung 1 of the master's Precedence ladder.
- **Coding homework**: unchanged. An explicit "implement it / debug this" gets a direct answer.
- **Case A — anything not submitted** (past exams, self-tests, practice sets, sheets whose deadline has passed): full solutions and grading of attempts are encouraged.

## Term Explanation Format
For "what is X?"-type questions, end the explanation (in the user's language) with a short English glossary block (4–8 lines, `Term :: definition`, sub-aspects indented) in a code block. It is a standing vocabulary aid for all courses and is distinct from `/remnote` SRS cards.

## Content vs Conversation Language
| Kind | Language |
|---|---|
| Learning-material **content** saved to disk (md notes, captions, `problems/`, `concepts.md`, conversions) | Follows the source material (English PDF → English md) |
| LLM **conversation** | The user's language (technical terms, code and commands stay in the original) |
| Term explanations | Explanation in the user's language + English glossary block |

Never mix languages inside one md file.

## Course Materials Structure
```
$STUDY_ROOT/<term>/<course>/
├── CLAUDE.md            ← course rules (templates/course-CLAUDE.md)
├── syllabus.md          ← lecture table + "My progress" O/X grid
├── Slides/{pdf,md/<basename>/}
├── Reviews/             ← <unit>_coverage.md · <unit>_review.md (tutor outputs)
├── Homeworks/  Tutorials/  Homework_Solution/ (⚠️ opt-in only)
├── past_exams/{pdf,md,analysis}/
├── weaklog.md  prereq_track.md  parked.md   ← created on first use
└── Exercises/ or LAB/   ← code (never converted)
```

## Materials Reference Rules
1. **Default priority**: `Slides/md/` → `Tutorials/` → `Homeworks/`. A course CLAUDE.md "Materials Reference Priority" section overrides this.
2. **`past_exams/analysis/concepts.md` is read on request only** in ad-hoc modes. Inside a Sprint, master §2.7.2 governs. Review-plan proposals (§2.7.1) also consult it.
3. **`Homework_Solution/` is opt-in only.** Never auto-read it; open it only when the user explicitly asks for the solution. A course may declare an exception.
4. **Converting new PDFs**: `python3 scripts/mathpix_convert.py <pdf-or-dir> --dry-run`, then without `--dry-run` (needs `scripts/.env`, see `.env.example`).

## Progress Tracking — syllabus.md "My progress" grid
- Columns per course: Lecture (Sprint done = `Reviews/` file exists) · Homework · Tutorial · **Review** (review done = a `## Review Log` row in the unit's review md).
- **O = done with the LLM or an artifact exists · X = not yet.** Markers are O/X only.
- Updated automatically at `/makereview` (Lecture) and at review-session end (Review).

## Lecture Material Reading Mode (single questions, outside a Sprint)
1. Read the `.md` **and** the original `.pdf` together. The PDF is the visual ground truth for diagrams and inline math.
2. If inline math looks broken in the md, check the page image or PDF before answering. Never guess formulas.
3. Cite the source location ("per the diagram on p.12").
4. Mark answers not grounded in the materials with "(general explanation)".
