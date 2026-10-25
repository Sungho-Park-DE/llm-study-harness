"""Helper: parse mathpix lines.json and emit diagram summaries.

Usage: python3 scripts/_parse_diagrams.py <path-to-lines.json>
"""
import json
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: _parse_diagrams.py <lines.json>", file=sys.stderr)
        sys.exit(1)
    path = Path(sys.argv[1])
    try:
        with path.open() as f:
            data = json.load(f)
    except FileNotFoundError:
        sys.exit(f"not found: {path}")
    except json.JSONDecodeError as e:
        sys.exit(f"invalid JSON in {path}: {e}")

    print(f"Total pages: {len(data.get('pages', []))}")
    langs = set()
    for p in data.get("pages", []):
        for lg in p.get("languages_detected", []) or []:
            langs.add(lg)
    print(f"Languages: {langs}")

    diag_summary = []
    for p in data.get("pages", []):
        page_num = p.get("page")
        lines = p.get("lines", [])
        diagrams = [l for l in lines if l.get("type") == "diagram"]
        for d in diagrams:
            children = [l for l in lines if l.get("parent_id") == d.get("id")]
            child_texts = [c.get("text", "") for c in children if c.get("text")]
            child_types = [c.get("type", "") for c in children]
            diag_summary.append(
                {
                    "page": page_num,
                    "diagram_id": d.get("id"),
                    "child_count": len(children),
                    "child_types": child_types,
                    "child_texts": child_texts,
                }
            )

    print(f"\nTotal diagrams: {len(diag_summary)}")
    print("\n--- Diagrams overview ---")
    for i, d in enumerate(diag_summary):
        types_set = set(d["child_types"])
        text_preview = " | ".join(d["child_texts"][:10])
        if len(d["child_texts"]) > 10:
            text_preview += f" | ... ({len(d['child_texts'])} total)"
        print(f"[{i:02d}] page={d['page']} children={d['child_count']} types={types_set}")
        print(f"     texts: {text_preview}")


if __name__ == "__main__":
    main()
