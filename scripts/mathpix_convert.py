#!/usr/bin/env python3
"""
mathpix_convert.py — PDF → Markdown conversion pipeline using the Mathpix API.

Usage:
    python3 mathpix_convert.py <PDF or directory> [options]

Options:
    --force           re-convert files that were already converted
    --dry-run         list targets without calling the API
    --include-venv    include PDFs inside .venv (default: excluded)
    --exclude NAME    skip folders with this name (repeatable, e.g. --exclude Homework_Solution)
    --exclude-path S  skip paths containing S (repeatable, e.g. --exclude-path IDA/Tutorials)

Output (compatible with the Marker convention):
    <pdf_dir>/pdf/foo.pdf  →  <pdf_dir>/md/foo/foo.md + images
    any other flat layout  →  <pdf_dir>/foo/foo.md + images

Credentials:
    environment variables MATHPIX_APP_ID, MATHPIX_APP_KEY
    or a .env file in the same folder (KEY=VALUE)

Requirements:
    Python 3.9+, standard library only (no dependencies).
"""
import argparse
import json
import os
import re
import sys
import time
import uuid
from pathlib import Path
from urllib import error, parse, request

API_BASE = "https://api.mathpix.com/v3"
POLL_INTERVAL = 3
POLL_TIMEOUT = 600

# mathpix mmd embeds images two ways and BOTH carry remote cdn URLs that rot:
#   markdown      ![alt](url)
#   latex         \includegraphics[opts]{url}   (used inside tables / complex layouts)
# Localizing only the first leaves \includegraphics URLs pointing at cdn.mathpix.com,
# which expire — so we match and download both.
MD_IMG_RE  = re.compile(r"!\[([^\]]*)\]\((https?://[^)\s]+)\)")
INC_IMG_RE = re.compile(r"(\\includegraphics(?:\[[^\]]*\])?\{)(https?://[^}]+)(\})")


# ──────────────────────────────────────────────────────────────────
# HTTP helpers (stdlib only)
# ──────────────────────────────────────────────────────────────────
def _http_request(url, *, method="GET", headers=None, data=None, timeout=60):
    req = request.Request(url, data=data, method=method, headers=headers or {})
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} {url}\n  {body[:500]}") from None


def _build_multipart(fields, file_field, filename, file_bytes,
                     content_type="application/pdf"):
    """Build multipart/form-data. Returns (body_bytes, content_type)."""
    boundary = uuid.uuid4().hex
    crlf = b"\r\n"
    parts = []
    for k, v in fields.items():
        parts.append(b"--" + boundary.encode() + crlf)
        parts.append(f'Content-Disposition: form-data; name="{k}"'.encode() + crlf + crlf)
        parts.append(str(v).encode("utf-8") + crlf)
    parts.append(b"--" + boundary.encode() + crlf)
    parts.append(
        f'Content-Disposition: form-data; name="{file_field}"; filename="{filename}"'.encode()
        + crlf
    )
    parts.append(f"Content-Type: {content_type}".encode() + crlf + crlf)
    parts.append(file_bytes + crlf)
    parts.append(b"--" + boundary.encode() + b"--" + crlf)
    body = b"".join(parts)
    return body, f"multipart/form-data; boundary={boundary}"


# ──────────────────────────────────────────────────────────────────
# Credentials
# ──────────────────────────────────────────────────────────────────
def load_env(script_dir):
    env = {}
    env_file = script_dir / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    app_id = os.environ.get("MATHPIX_APP_ID") or env.get("MATHPIX_APP_ID") or ""
    app_key = os.environ.get("MATHPIX_APP_KEY") or env.get("MATHPIX_APP_KEY") or ""
    if not app_key:
        sys.exit(
            "MATHPIX_APP_KEY is not set.\n"
            f"Create {script_dir}/.env or set the environment variables."
        )
    return {"app_id": app_id, "app_key": app_key}


def auth(creds):
    h = {"app_key": creds["app_key"]}
    if creds.get("app_id"):
        h["app_id"] = creds["app_id"]
    return h


# ──────────────────────────────────────────────────────────────────
# Mathpix API calls
# ──────────────────────────────────────────────────────────────────
def submit_pdf(pdf_path, creds):
    options = {
        "conversion_formats": {"md": True},
        "math_inline_delimiters": ["$", "$"],
        "math_display_delimiters": ["$$", "$$"],
        "rm_spaces": True,
        "include_diagram_text": True,
    }
    file_bytes = pdf_path.read_bytes()
    body, ctype = _build_multipart(
        {"options_json": json.dumps(options)},
        file_field="file",
        filename=pdf_path.name,
        file_bytes=file_bytes,
    )
    headers = auth(creds) | {"Content-Type": ctype}
    raw = _http_request(f"{API_BASE}/pdf", method="POST",
                        headers=headers, data=body, timeout=180)
    obj = json.loads(raw)
    if "pdf_id" not in obj:
        raise RuntimeError(f"submission failed: {obj}")
    return obj["pdf_id"]


def poll_status(pdf_id, creds):
    deadline = time.time() + POLL_TIMEOUT
    last_pct = -1
    while time.time() < deadline:
        raw = _http_request(f"{API_BASE}/pdf/{pdf_id}",
                            headers=auth(creds), timeout=30)
        body = json.loads(raw)
        status = body.get("status")
        pct = body.get("percent_done", 0)
        if pct != last_pct and status != "completed":
            print(f"    {status} ({pct}%)")
            last_pct = pct
        if status == "completed":
            return body
        if status in ("error", "failed"):
            raise RuntimeError(f"conversion failed: {body}")
        time.sleep(POLL_INTERVAL)
    raise TimeoutError(f"polling timeout for {pdf_id}")


def fetch_mmd(pdf_id, creds):
    last_err = None
    for ext in ("mmd", "md"):
        try:
            raw = _http_request(f"{API_BASE}/pdf/{pdf_id}.{ext}",
                                headers=auth(creds), timeout=60)
            text = raw.decode("utf-8", errors="replace")
            if text.strip():
                return text
        except Exception as e:
            last_err = e
    raise RuntimeError(f"unable to fetch mmd/md for {pdf_id}: {last_err}")


def fetch_lines_json(pdf_id, creds):
    """OCR text of diagrams (included in lines.json when include_diagram_text=true)."""
    try:
        raw = _http_request(f"{API_BASE}/pdf/{pdf_id}.lines.json",
                            headers=auth(creds), timeout=60)
        text = raw.decode("utf-8", errors="replace")
        return text if text.strip() else None
    except Exception as e:
        print(f"    ⚠ lines.json fetch failed: {e}")
        return None


def download_images(mmd, out_dir):
    counter = [0]
    seen = {}

    def fetch_local(url):
        """Download url into out_dir; return local filename, or None on failure.
        414 (URI Too Long) happens for complex shapes whose polygon has thousands of
        characters — retry with the &polygon=... part removed. The bounding-box crop
        (height/width/top_left) stays, so we get a slightly larger rectangle of the same figure."""
        if url in seen:
            return seen[url]
        counter[0] += 1
        idx = counter[0]
        ext = Path(parse.urlparse(url).path).suffix.lower() or ".jpeg"
        if ext not in (".jpeg", ".jpg", ".png", ".gif", ".webp"):
            ext = ".jpeg"
        local_name = f"_image_{idx:03d}{ext}"
        local_path = out_dir / local_name
        # candidates: original → (for 414) polygon removed
        candidates = [url]
        stripped = re.sub(r"&polygon=[^&]*", "", url)
        if stripped != url:
            candidates.append(stripped)
        last_err = None
        for cand in candidates:
            for attempt in range(3):  # retry transient 502/503/504 with exponential backoff
                try:
                    data = _http_request(cand, timeout=60)
                    local_path.write_bytes(data)
                    seen[url] = local_name
                    if cand != url:
                        print(f"    ↻ image #{idx}: recovered with polygon removed (414)")
                    return local_name
                except Exception as e:
                    last_err = e
                    if any(code in str(e) for code in ("502", "503", "504")):
                        time.sleep(2 ** attempt)
                        continue
                    break  # 414 etc. → next candidate (polygon removed)
        print(f"    ⚠ image #{idx} download failed: {last_err}")
        return None

    def md_replace(m):
        alt, url = m.group(1), m.group(2)
        ln = fetch_local(url)
        return f"![{alt}]({ln})" if ln else m.group(0)

    def inc_replace(m):
        pre, url, post = m.group(1), m.group(2), m.group(3)
        ln = fetch_local(url)
        return f"{pre}{ln}{post}" if ln else m.group(0)

    # markdown images first, then \includegraphics — localize both
    mmd = MD_IMG_RE.sub(md_replace, mmd)
    mmd = INC_IMG_RE.sub(inc_replace, mmd)
    return mmd


# ──────────────────────────────────────────────────────────────────
# File discovery & output mapping
# ──────────────────────────────────────────────────────────────────
def output_paths(pdf_path):
    """Marker convention: <X>/pdf/foo.pdf → <X>/md/foo/foo.md, otherwise flat.
    <X>/pdf/<sub>/foo.pdf → <X>/md/<sub>/foo/foo.md (mirrors one subfolder level under pdf/, e.g. a year)."""
    parent = pdf_path.parent
    base = pdf_path.stem
    if parent.name == "pdf":
        out_root = parent.parent / "md"
    elif parent.parent.name == "pdf":
        out_root = parent.parent.parent / "md" / parent.name
    else:
        out_root = parent
    out_dir = out_root / base
    out_md = out_dir / f"{base}.md"
    return out_dir, out_md


def find_pdfs(target, include_venv, exclude_names=(), exclude_paths=()):
    if target.is_file():
        if target.suffix.lower() != ".pdf":
            return []
        return [target]
    if not target.is_dir():
        return []
    pdfs = []
    for p in sorted(target.rglob("*.pdf")):
        parts = p.parts
        if not include_venv and any(x in parts for x in (".venv", "venv", "node_modules")):
            continue
        rel_parts = p.relative_to(target).parts
        if exclude_names and any(n in rel_parts for n in exclude_names):
            continue
        if exclude_paths:
            rel_str = str(p.relative_to(target))
            if any(s in rel_str for s in exclude_paths):
                continue
        pdfs.append(p)
    return pdfs


# ──────────────────────────────────────────────────────────────────
# Per-file conversion
# ──────────────────────────────────────────────────────────────────
def convert_one(pdf_path, creds, force, dry_run):
    out_dir, out_md = output_paths(pdf_path)
    if out_md.exists() and not force:
        return "skip"
    if dry_run:
        print(f"    → {out_md}")
        return "dry"

    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_id = submit_pdf(pdf_path, creds)
    if force:
        # on re-conversion, remove _image_NNN files from the previous run so numbers don't mix (only files this script made)
        for old in out_dir.glob("_image_*"):
            old.unlink()
    print(f"    pdf_id={pdf_id}")
    poll_status(pdf_id, creds)
    mmd = fetch_mmd(pdf_id, creds)
    rewritten = download_images(mmd, out_dir)
    # safety net: warn right away if a CDN URL is left because a download failed
    # (the CDN hosts files only for a while after conversion → re-convert with --force while it is live)
    leftover = re.findall(r"https?://cdn\.mathpix\.com[^\s)}\]\"']+", rewritten)
    if leftover:
        print(f"    ⚠ {len(leftover)} CDN URL(s) left — download failed; re-convert with --force before the CDN expires:")
        for u in leftover[:5]:
            print(f"        {u[:90]}")
    out_md.write_text(rewritten, encoding="utf-8")
    # save the diagram-label OCR (lines.json) — used by the enrichment step
    lines_data = fetch_lines_json(pdf_id, creds)
    if lines_data:
        out_lines = out_dir / f"{pdf_path.stem}.lines.json"
        out_lines.write_text(lines_data, encoding="utf-8")
    img_count = len(list(out_dir.glob("_image_*")))
    print(f"    ✓ {len(rewritten):,} chars, {img_count} images → {out_md.name}")
    return "ok"


# ──────────────────────────────────────────────────────────────────
# Entry
# ──────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="Mathpix API → Markdown conversion")
    ap.add_argument("target", help="PDF file or directory")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--include-venv", action="store_true")
    ap.add_argument("--exclude", action="append", default=[],
                    help="skip folders with this name (repeatable)")
    ap.add_argument("--exclude-path", action="append", default=[],
                    help="skip paths containing this substring (repeatable)")
    args = ap.parse_args()

    target = Path(args.target).expanduser().resolve()
    if not target.exists():
        sys.exit(f"path not found: {target}")

    script_dir = Path(__file__).resolve().parent
    creds = (load_env(script_dir) if not args.dry_run
             else {"app_id": "", "app_key": ""})

    pdfs = find_pdfs(
        target,
        include_venv=args.include_venv,
        exclude_names=tuple(args.exclude),
        exclude_paths=tuple(args.exclude_path),
    )
    if not pdfs:
        sys.exit("nothing to convert")

    print(f"\ntargets: {len(pdfs)}")
    pending = []
    for p in pdfs:
        _, out_md = output_paths(p)
        rel = (p.relative_to(target) if target.is_dir() and p.is_relative_to(target)
               else p.name)
        if out_md.exists() and not args.force:
            print(f"  ⊘ {rel} (already exists)")
        else:
            pending.append(p)
    print(f"to process: {len(pending)}\n")

    if not pending:
        print("no files to process.")
        return

    counts = {"ok": 0, "skip": 0, "dry": 0, "fail": 0}
    failures = []
    for i, pdf in enumerate(pending, 1):
        rel = (pdf.relative_to(target) if target.is_dir() and pdf.is_relative_to(target)
               else pdf.name)
        print(f"[{i}/{len(pending)}] {rel}")
        try:
            r = convert_one(pdf, creds, args.force, args.dry_run)
            counts[r] = counts.get(r, 0) + 1
        except Exception as e:
            print(f"    ✗ failed: {e}")
            counts["fail"] += 1
            failures.append((pdf, str(e)))

    print(f"\n{'=' * 50}")
    print(f"done: {counts['ok']}  skipped: {counts['skip']}  "
          f"dry run: {counts['dry']}  failed: {counts['fail']}")
    if failures:
        print("\nfailed:")
        for p, e in failures:
            print(f"  - {p.name}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
