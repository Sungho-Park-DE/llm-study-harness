---
description: Generate RemNote cloze card drafts for the current concept; user registers them (rewrite optional)
---

You are now in `/makeremnote` mode (Sprint Stage 7: STORE, per-cycle invocation).

## Task

1. **Identify the current sprint concept** from conversation context. If ambiguous, ask the user briefly.

2. **Generate 1–3 atomic card drafts** in **RemNote-native syntax** (user uses RemNote only, NOT Anki):
   - **Cloze** for facts, definitions, formulas — wrap the hidden span in `{{ }}`. **No `c1::`/`c2::` numbering — that is Anki syntax; in RemNote the literal `c1::` shows up inside the card.**
     - Example: `Backpropagation uses {{chain rule}} to compute {{∂L/∂w_l = ∂L/∂z_l × ∂z_l/∂w_l}}`
   - **Q&A (basic card)** for concepts, "why" questions, comparisons — `Question >> Answer` (`>>` renders as a forward arrow in RemNote)
     - Example: `Why does sigmoid cause vanishing gradient in deep nets? >> Its derivative max is 0.25, so gradients compress geometrically through layers.`
   - **Concept/definition** — `Term :: Definition` (bidirectional concept card)

3. **Atomic principle**: one concept per card. Do not combine multiple concepts.

4. **Output format** (RemNote-native, paste-ready — one card per line):
   ```
   Term :: Definition
   Sentence with the {{hidden span}}.
   Question >> Answer
   ```

5. **Registration-ready quality** (drafts are registered as-is in practice — master §1.5, 2026-06-12): write each card at register-quality — precise wording, atomic, no placeholder phrasing. Do NOT append rewrite reminders or nagging; rewriting in own words is the user's optional call.

6. **DO NOT register cards yourself**. User handles RemNote registration manually.

Append `[Stage: 7/7 — STORE · per-cycle]` at end of your response.
