#!/usr/bin/env bash
# Coverage judge gate — UserPromptSubmit hook.
# Only on a session-end signal: block the end while a coverage file still says judged: false.
# Any other prompt passes untouched (never interrupt a lesson).
#
# On block, the reason is shown to the user only and never enters Claude's context
# (Claude Code hooks docs: UserPromptSubmit decision "block"), so the message tells
# the user what to do next.
#
# Config: STUDY_ROOT = parent of the term folders ($STUDY_ROOT/<term>/<course>/Reviews/),
#         default $HOME/study.
#         COVERAGE_GATE_EXTRA_END = optional extended regex of extra end phrases
#         (e.g. in your own language), matched against the whole lowercased prompt.

STUDY_ROOT="${STUDY_ROOT:-$HOME/study}"

input=$(cat)

# JSON parsing: jq → python3 → neither: warn the user and pass (no silent fail-open)
if command -v jq >/dev/null 2>&1; then
  prompt=$(printf '%s' "$input" | jq -r '.prompt // empty' 2>/dev/null)
  emit() { jq -n --arg r "$1" '{decision:"block", reason:$r}'; }
elif command -v python3 >/dev/null 2>&1; then
  prompt=$(printf '%s' "$input" | python3 -c 'import sys,json
try: print(json.load(sys.stdin).get("prompt",""), end="")
except Exception: pass' 2>/dev/null)
  emit() { python3 -c 'import sys,json; print(json.dumps({"decision":"block","reason":sys.argv[1]}, ensure_ascii=False))' "$1"; }
else
  printf '%s\n' '{"systemMessage":"coverage gate: jq/python3 not found - gate disabled"}'
  exit 0
fi

# End signal = the WHOLE prompt is an end phrase
# (a word inside a sentence — "stop gradient", "can we finish this proof?" — is not)
norm=$(printf '%s' "$prompt" | tr '[:upper:]' '[:lower:]' | sed -E 's/^[[:space:]]+//; s/[[:space:].!~]+$//')
is_end=0
case "$norm" in
  /makereview*) is_end=1 ;;   # slash command (arguments allowed)
esac
end_re="stop( here)?|let'?s stop( here)?|done for today|that'?s it for today|end (the )?session"
if [ $is_end -eq 0 ] && printf '%s' "$norm" | grep -qxE "$end_re"; then
  is_end=1
fi
if [ $is_end -eq 0 ] && [ -n "${COVERAGE_GATE_EXTRA_END:-}" ] && printf '%s' "$norm" | grep -qxE "$COVERAGE_GATE_EXTRA_END"; then
  is_end=1
fi
[ $is_end -eq 1 ] || exit 0

# A config error (missing STUDY_ROOT) is reported, not passed silently
if [ ! -d "$STUDY_ROOT" ]; then
  printf '%s\n' '{"systemMessage":"coverage gate: STUDY_ROOT folder not found - gate disabled (set STUDY_ROOT in settings.json)"}'
  exit 0
fi

# Read judged only inside the frontmatter (first --- block); example lines in the body are ignored
frontmatter_unjudged() {
  awk 'NR==1 { if ($0 != "---") exit; next } $0 == "---" { exit } { print }' "$1" 2>/dev/null \
    | grep -qE '^judged:[[:space:]]*["'"'"']?false["'"'"']?[[:space:]]*$'
}

# Find coverage files whose frontmatter says judged: false (no hardcoded term folder)
unjudged=()
while IFS= read -r f; do
  # R4: skip files not modified for 48 h, so an orphan from another course/week cannot block this session
  [ -z "$(find "$f" -mmin +2880 2>/dev/null)" ] || continue
  frontmatter_unjudged "$f" && unjudged+=("${f#"$STUDY_ROOT"/}")
done < <(find "$STUDY_ROOT" -mindepth 4 -maxdepth 4 -path '*/Reviews/*_coverage.md' -type f 2>/dev/null)

if [ ${#unjudged[@]} -gt 0 ]; then
  list=$(printf '%s, ' "${unjudged[@]}"); list=${list%, }
  emit "⚠️ Session end paused — coverage not judged yet: ${list}. Send \"run the coverage judge\" as your next message and Claude runs the master doc's §2.7.3 cold judge (checks only what this session taught; untaught items go to ## Remaining). Once the file says judged: true, send the end signal again."
fi
exit 0
