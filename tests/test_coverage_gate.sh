#!/usr/bin/env bash
# Tests for hooks/coverage_judge_gate.sh — run: bash tests/test_coverage_gate.sh
set -u
HOOK="$(cd "$(dirname "$0")/.." && pwd)/hooks/coverage_judge_gate.sh"
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
ROOT="$TMP/study"; mkdir -p "$ROOT/term1/CourseA/Reviews" "$ROOT/term2/CourseB/Reviews"
FILE="$ROOT/term1/CourseA/Reviews/W01_coverage.md"
printf -- '---\njudged: false\n---\n' > "$FILE"
fail=0

json() { python3 -c 'import json,sys; print(json.dumps({"prompt":sys.argv[1]}))' "$1"; }
run() { json "$1" | STUDY_ROOT="$ROOT" PATH="${2:-$PATH}" bash "$HOOK"; }
check() { # expected(block|pass) prompt [PATH]
  out=$(run "$2" "${3:-$PATH}")
  if printf '%s' "$out" | grep -q '"decision"'; then got=block; else got=pass; fi
  if [ "$got" = "$1" ]; then echo "ok    $got  | $2"; else echo "FAIL  want $1 got $got | $2"; fail=1; fi
}

echo "## end signals (block)"
for p in "/makereview" "/makereview W03" "done for today" "Done for today." "that's it for today" "end session" "end the session" "stop" "Stop" "STOP!" "stop here" "let's stop"; do check block "$p"; done
echo "## mid-lesson prompts (pass)"
for p in "can we finish this proof?" "stop here and move to the next concept" "what does the makereview command do?" "Why do we use stop gradient in BYOL?" "what is a stop-gradient op" "explain early stopping" "next concept"; do check pass "$p"; done

echo "## extra end phrases (COVERAGE_GATE_EXTRA_END)"
check pass "Schluss für heute"
export COVERAGE_GATE_EXTRA_END="schluss( für heute)?"
check block "Schluss für heute"
check pass "kein Schluss für heute, weiter"
unset COVERAGE_GATE_EXTRA_END

echo "## R4 age window (48h)"
touch -t "$(date -v-47H +%Y%m%d%H%M 2>/dev/null || date -d '-47 hours' +%Y%m%d%H%M)" "$FILE"; check block "done for today"
touch -t "$(date -v-49H +%Y%m%d%H%M 2>/dev/null || date -d '-49 hours' +%Y%m%d%H%M)" "$FILE"; check pass "done for today"
touch "$FILE"

echo "## any term folder"
mv "$FILE" "$TMP/"; printf -- '---\njudged: false\n---\n' > "$ROOT/term2/CourseB/Reviews/W01_coverage.md"; check block "done for today"
rm "$ROOT/term2/CourseB/Reviews/W01_coverage.md"; check pass "done for today"; mv "$TMP/W01_coverage.md" "$FILE"

echo "## frontmatter-only judged check"
mv "$FILE" "$TMP/"
B="$ROOT/term1/CourseA/Reviews"
printf -- '---\njudged: true\n---\nexample line:\njudged: false\n' > "$B/W02_coverage.md"; check pass "done for today"
printf -- '---\njudged: "false"\n---\n' > "$B/W03_coverage.md"; check block "done for today"
rm "$B/W02_coverage.md" "$B/W03_coverage.md"; mv "$TMP/W01_coverage.md" "$FILE"

echo "## missing STUDY_ROOT"
out=$(json "done for today" | STUDY_ROOT="$TMP/nope" bash "$HOOK")
if printf '%s' "$out" | grep -q systemMessage; then echo "ok    missing root -> systemMessage"; else echo "FAIL  missing root should warn"; fail=1; fi
out=$(json "next concept" | STUDY_ROOT="$TMP/nope" bash "$HOOK")
if [ -z "$out" ]; then echo "ok    missing root, no end signal -> silent"; else echo "FAIL  should stay silent"; fail=1; fi

echo "## parser fallbacks"
BIN="$TMP/bin"; mkdir -p "$BIN"
for b in bash cat grep find sed tr printf awk; do p=$(command -v "$b") && [ -x "$p" ] && ln -sf "$p" "$BIN/$b"; done
ln -sf "$(command -v python3)" "$BIN/python3"
check block "done for today" "$BIN"                     # python3, no jq
rm "$BIN/python3"
out=$(run "done for today" "$BIN")
if printf '%s' "$out" | grep -q systemMessage; then echo "ok    no jq/python3 -> systemMessage"; else echo "FAIL  no jq/python3 should warn"; fail=1; fi

[ $fail -eq 0 ] && echo "ALL PASS" || { echo "SOME FAILED"; exit 1; }
