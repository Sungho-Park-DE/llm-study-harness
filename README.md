# LLM Study Harness

[![CI](https://github.com/Sungho-Park-DE/llm-study-harness/actions/workflows/ci.yml/badge.svg)](https://github.com/Sungho-Park-DE/llm-study-harness/actions/workflows/ci.yml)

A Claude Code setup that turns the assistant into a structured 1:1 tutor for university theory courses. It is built from prompt documents, a skill, slash commands and one hook. I built and used it during one semester (TUM, 2026 summer term, four courses: deep learning, foundation models, data-analysis math, cloud data processing).

What you get:

- A **7-stage learning cycle** per concept: SCAN → pre-attempt → worked example → faded practice → retrieval → calibration → store. Each stage has gates and stage tags, and failures route back to earlier stages.
- **Learning-protection rules** that apply in every mode: no praise, tiered hints instead of answers, no ready-made notes to copy, and a guard against doing graded homework for you.
- **Persistent study state** as plain markdown in each course folder: a coverage list per unit, review sheets, a weak-spot log, a prerequisite queue and parked concepts.
- A **cold coverage judge**: a fresh subagent checks at each concept exit whether every item of the unit was actually taught. A hook stops a session from ending while a unit is still unjudged.
- An **exam gate**: if a course folder holds structured past-exam data (`past_exams/analysis/`, produced outside this repo), original exam problems unlock once all their concepts are learned.

## Workflow

![One Sprint cycle per concept: 7 stages, backward routes, cold coverage judge, exam gate and the session-end hook](docs/workflow.svg)

A PNG copy for slides and documents is in `docs/workflow.png`.

## Architecture

```mermaid
flowchart TB
    U([User prompt]) --> HOOK
    HOOK{{"hooks/coverage_judge_gate.sh<br/>UserPromptSubmit"}} -- "end signal + judged:false" --> BLOCK["blocked; user sees<br/>'run the coverage judge first'"]
    HOOK -- otherwise --> CC[Claude Code session]

    subgraph Context["Loaded context"]
        ROOT["$STUDY_ROOT/CLAUDE.md<br/>always-on rule: read the master doc<br/>routing · Case A/B graded-work policy"]
        COURSE["&lt;course&gt;/CLAUDE.md<br/>aliases · unit naming · materials map<br/>exam strategy · course overrides"]
        MASTER["docs/llm-tutor-system.md<br/>(master doc = system prompt)<br/>Part 1 principles · Part 2 Sprint · judges"]
    end

    CC --> ROOT --> MASTER
    MASTER -- "§1.15 read at Sprint entry" --> COURSE
    CC -.ad-hoc questions.-> SKILL["skills/ml-theory-tutor<br/>7 modes: concept · problem · review<br/>exam · weaklog · remnote · park"]
    SKILL -- "yields during a Sprint" --> MASTER
    CMD["commands/<br/>/makereview /makeremnote /feynman /paper<br/>+ pointer stubs for skill modes"] --> MASTER
    CMD --> SKILL

    subgraph Disk["Course folder ($STUDY_ROOT/&lt;term&gt;/&lt;course&gt;/)"]
        COV["Reviews/&lt;unit&gt;_coverage.md<br/>judged: false|true · session_log"]
        REV["Reviews/&lt;unit&gt;_review.md<br/>Self-Test · Review Log"]
        WEAK["weaklog.md · prereq_track.md · parked.md"]
        ANALYSIS["past_exams/analysis/<br/>(optional, external)"]
    end

    MASTER -- "SCAN writes" --> COV
    MASTER -- "cold judge subagent sets judged:true" --> COV
    HOOK -. reads .-> COV
    MASTER --> REV & WEAK
    MASTER -- "§2.7.2 exam gate" --> ANALYSIS
    SCRIPTS["scripts/mathpix_convert.py<br/>PDF → md + images + lines.json"] --> Disk
```

Precedence when files disagree, highest first, defined in the master doc Part 1: graded-work Case B, then a course rule that names the master section it replaces, then the master doc, then course patterns, then skill defaults.

## Design rationale

**Learning-science basis.** Each rule in the master doc carries its source inline. The main ones:

| Mechanism in the harness | Source cited in the doc |
|---|---|
| Stage 2 pre-attempt before instruction | Richland, Kornell & Kao 2009; Kornell, Hays & Bjork 2009 (pretesting effect) |
| Stage 3 self-explanation at principle-bearing steps only | Chi 1989; Renkl 1997; Kalyuga 2007 |
| Compressed entry when the pre-attempt is already correct | Kalyuga 2003/2007 (expertise reversal); Salden et al. 2010 |
| Stage 4 completion-problem fading; proof-shaped prompts | Renkl & Atkinson 2003; Hodds, Alcock & Inglis 2014 |
| Comparing two worked examples | Alfieri, Nokes-Malach & Schunn 2013 |
| Calibration: user predicts first, then sees the LLM estimate | Tversky & Kahneman 1974 (anchoring); Koriat 1997; Hacker et al. 2000 |
| "What you got right" stated as data, never as praise | Butler, Karpicke & Roediger 2008; Kluger & DeNisi 1996 |
| High-confidence errors get extra feedback | Butterfield & Metcalfe 2001; Metcalfe 2017 |
| A weak spot resolves only after an unaided retrieval | Rawson & Dunlosky 2011 (successive relearning) |
| Interleaved, unlabeled multi-unit review | Rohrer, Dedrick & Stershic 2015; Brunmair & Richter 2019 |
| Transfer drills with feedback after every solve | Pan & Rickard 2018; Butler 2010 |
| Unassisted solo blocks and timed mocks | Bastani et al. 2025 (PNAS); Zhang, Morphew & Stelzer 2023 |

The doc cites about 25 works in total. These are the citations as written in the doc. I did not re-verify them for this README. The doc itself notes (§1.14) that an earlier reference file it replaced contained citation errors and asks for fresh verification before relying on a claim.

**Why a cold judge plus a hook.** In a long tutoring session the main context drifts: it compresses what was covered and stops noticing what was skipped. So coverage is checked by a **fresh subagent** that reads two things from disk: the coverage list written at SCAN time, before any drift, and the raw dialogue turns, never a summary written by the main session. The doc records an informal stress test in which a summary-based handoff made the judge flag 16 items against 3 real gaps (§2.7.3). Prompt-level rules can be forgotten, so the stop condition is backed by a `UserPromptSubmit` hook. A session-end message such as "done for today", "stop" or `/makereview` is blocked while any recent coverage file still says `judged: false`. A blocked prompt never reaches the model, so the hook's message tells the *user* to ask for the judge first.

## Install

Requirements: Claude Code; `bash`; `jq` or `python3` for the hook; Python ≥ 3.9 (stdlib only) and a Mathpix API key for PDF conversion. Tested on macOS only.

```bash
git clone <this repo> ~/dev/llm-study-harness && cd ~/dev/llm-study-harness
./install.sh            # dry run: shows the symlinks it would create in ~/.claude
./install.sh --apply    # create them (existing non-symlink files are left alone)
```

Then:

1. Merge `settings.example.json` into `~/.claude/settings.json` and point `STUDY_ROOT` at the folder that holds your term folders (`$STUDY_ROOT/<term>/<course>/`).
2. Copy `templates/study-root-CLAUDE.md` to `$STUDY_ROOT/CLAUDE.md`, and `templates/course-CLAUDE.md` into each course folder. Fill in the placeholders. Aliases and unit naming are set per course.
3. Optional, for PDF conversion: `cp scripts/.env.example scripts/.env`, add your keys, then run `python3 scripts/mathpix_convert.py <pdf-or-dir> --dry-run`.
4. Start a session inside a course folder and say, for example, "let's study I2DL this week".

Checks: `bash tests/test_coverage_gate.sh` (hook behavior) and `python3 tests/check_repo.py` (frontmatter, § references, repo paths, privacy guard; needs `pyyaml`). CI runs both on Ubuntu and macOS, plus shellcheck, on every push.

## Repository layout

```
docs/llm-tutor-system.md     master doc (the system prompt), ~800 lines
docs/workflow.svg|png        workflow diagram
skills/ml-theory-tutor/      ad-hoc tutoring modes
commands/                    /makereview /makeremnote /feynman /paper + mode stubs
hooks/coverage_judge_gate.sh session-end gate
tests/                       hook tests + static repo checks
.github/workflows/ci.yml     CI (Ubuntu + macOS)
evals/trigger-cases.md       skill trigger cases (not yet run)
scripts/                     Mathpix conversion + diagram OCR summary
templates/                   study-root and course CLAUDE.md
```

## Limitations

- **No learning-outcome data.** The harness encodes evidence-based techniques, but I have not measured whether it improves learning, retention or grades for me or anyone else. There was no control condition and nothing was logged for evaluation.
- **Not included on purpose.** The past-exam extraction pipeline, course materials (slides, sheets, solutions, exams) and personal study data (coverage files, reviews, weak-spot logs) stay out of this repo.
- **One user, one term.** It was designed and tuned by one person, for one program, and originally used in Korean with English technical terms. This repo is an English translation; the translated prompts and trigger phrases have not been used in real sessions.
- **Mostly prompt-enforced.** Apart from the coverage hook, every rule depends on the model following a long document. Compliance was not measured.
- **Skill triggering is unverified.** The rewritten skill descriptions and the `/tutor-review` rename are based on reading, not on runs. See `evals/trigger-cases.md`.
- **Hook caveats.** `UserPromptSubmit` receives a slash command as typed (`/makereview W03`), not the expanded text. This is documented in the Claude Code hooks reference; I have not tested it in a live session. Coverage files left unjudged for more than 48 h are skipped by design, so such orphans need manual cleanup.
- **The master doc grew by accretion.** It carries dated decisions such as "2026-06-12" and examples from four specific courses. It reads as a working document, not a polished spec.

## License

MIT, see [LICENSE](LICENSE).
