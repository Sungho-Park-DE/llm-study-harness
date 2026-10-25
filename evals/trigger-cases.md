# Skill trigger cases — ml-theory-tutor

Status: **not yet run.** The description rewrite (932 chars, negatives first) is checked only by reading. Run these against a session that has the skills installed. For example, use the skill-creator eval loop, or start a fresh `claude` session per prompt and check which skill loads.

## ml-theory-tutor — should trigger

| # | Prompt | Note |
|---|---|---|
| 1 | let's study I2DL this week | Sprint trigger (master §4.1) |
| 2 | derive why attention divides by √d | derivation |
| 3 | explain Theorem 2.1 on p.12 of this slide deck (course folder cwd) | lecture material |
| 4 | I'm confused about how SVD and PCA relate | math-for-data concept |
| 5 | how is PACELC different from the CAP theorem? | distributed-systems theory |
| 6 | /concept LoRA | shortcut |
| 7 | review mode for C03 | review mode phrase |
| 8 | park this for now, I'll revisit it on the weekend | /park phrase |
| 9 | exam mode | Exam Mode |
| 10 | I can't see where Cauchy-Schwarz is used in this proof | proof help |

## ml-theory-tutor — should NOT trigger

| # | Prompt | Why |
|---|---|---|
| 1 | polish the "fine-tuned a transformer" bullet on my CV | CV editing, ML word only |
| 2 | fix the tests of the digest module in my lecture-assistant app | app development |
| 3 | profile why this PyTorch DataLoader is slow | pure coding/debug |
| 4 | CMake build error in the CBDP assignment | C++ build (CBDP implementation) |
| 5 | compare embedding API prices | product/infra question |
| 6 | extract the concepts from these 3 past-exam PDFs | extraction is out of scope |
| 7 | draw the README diagram in mermaid | docs |
| 8 | convert every PDF in this folder to md | conversion tool step |
| 9 | bump the tokenizer library version | dependency work |
| 10 | organize my schedule for tomorrow | non-study |

## Command stubs

Typing each of `/concept /problem /tutor-review /exam /weaklog /remnote /park` should load its target. Check `/review` separately. It is the reason the stub is named `/tutor-review`, and its current behaviour in Claude Code is unverified.
