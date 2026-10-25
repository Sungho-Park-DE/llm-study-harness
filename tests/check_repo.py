#!/usr/bin/env python3
"""Static repo checks — run: python3 tests/check_repo.py

1. Frontmatter of every skill and command parses as strict YAML and has a description.
2. Every master-doc section reference (§N.N) in the docs resolves to a heading in the master doc.
3. Repo paths named in backticks (scripts/, hooks/, templates/, commands/, ...) exist.
4. Privacy guard: no personal absolute paths, sync-folder paths, real e-mail addresses or key files.
"""
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
MASTER = ROOT / "docs" / "llm-tutor-system.md"
errors = []

# 1. frontmatter
for p in sorted(ROOT.glob("skills/*/SKILL.md")) + sorted(ROOT.glob("commands/*.md")):
    text = p.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if not text.startswith("---") or len(parts) < 3:
        errors.append(f"{p.relative_to(ROOT)}: no frontmatter")
        continue
    try:
        meta = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as e:
        errors.append(f"{p.relative_to(ROOT)}: frontmatter is not valid YAML ({str(e).splitlines()[0]})")
        continue
    if not meta.get("description"):
        errors.append(f"{p.relative_to(ROOT)}: missing description")
    if p.name == "SKILL.md" and len(meta.get("description", "")) > 1024:
        errors.append(f"{p.relative_to(ROOT)}: description over 1024 chars")

# 2. section references
sections = set(re.findall(r"^#{2,3} (\d+(?:\.\d+)+)\b", MASTER.read_text(encoding="utf-8"), re.M))
doc_files = [MASTER, ROOT / "README.md", *ROOT.glob("skills/*/SKILL.md"), *ROOT.glob("commands/*.md"), *ROOT.glob("templates/*.md")]
for p in doc_files:
    for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        for ref in re.findall(r"§ ?(\d+(?:\.\d+)*)", line):
            if ref not in sections:
                errors.append(f"{p.relative_to(ROOT)}:{n}: §{ref} has no heading in the master doc")

# 3. repo paths in backticks
path_re = re.compile(r"`((?:scripts|hooks|templates|commands|skills|docs|tests|evals)/[A-Za-z0-9_./-]+|settings\.example\.json|install\.sh)`")
for p in doc_files:
    for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        for ref in path_re.findall(line):
            if "<" in ref or "*" in ref or ref == "scripts/.env":  # .env is created by the user, never tracked
                continue
            if not (ROOT / ref.rstrip("/")).exists():
                errors.append(f"{p.relative_to(ROOT)}:{n}: `{ref}` does not exist")

# 4. privacy guard (tracked files only)
tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
allowed_mail = re.compile(r"(noreply@anthropic\.com|@users\.noreply\.github\.com|@example\.(com|org))$")
patterns = {
    "personal home path": re.compile(r"/Users/(?!<)[A-Za-z][\w.-]*"),
    "sync-folder path": re.compile(r"Mobile Documents|com~apple~CloudDocs|iCloud~md~obsidian"),
    "e-mail address": re.compile(r"[\w.%+-]+@[\w-]+(?:\.[\w-]+)+"),
}
for f in tracked:
    if f == ".env" or f.endswith("/.env"):
        errors.append(f"{f}: secrets file is tracked")
        continue
    if f == "tests/check_repo.py":
        continue  # this file names the patterns it searches for
    try:
        text = (ROOT / f).read_text(encoding="utf-8")
    except (UnicodeDecodeError, FileNotFoundError):
        continue
    for n, line in enumerate(text.splitlines(), 1):
        for label, rx in patterns.items():
            for m in rx.finditer(line):
                if label == "e-mail address" and allowed_mail.search(m.group(0)):
                    continue
                errors.append(f"{f}:{n}: {label}: {m.group(0)}")

if errors:
    print("\n".join(errors))
    print(f"\n{len(errors)} problem(s)")
    sys.exit(1)
print("repo checks: OK")
