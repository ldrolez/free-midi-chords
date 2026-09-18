#!/usr/bin/env python3
"""Build a machine-readable index of a free-midi-chords pack.

The pack ships no manifest: key, mode, numerals, mood tags and rhythm style exist only
inside filenames (and the MIDI track name). This script extracts them once so agents and
scripts can query instead of scraping paths.

    python skills/music-theory/scripts/build_index.py                  # newest dist/ archive
    python skills/music-theory/scripts/build_index.py --pack output    # a built pack tree
    python skills/music-theory/scripts/build_index.py --pack ~/Downloads/free-midi-chords-20260314.zip
    python skills/music-theory/scripts/build_index.py --read-midi --jsonl --csv

Inputs are interchangeable: the release `.zip`, or the `output/` tree `make dist` cuts it
from. Output goes to `dist/<name>.json` by default (a build output, never a source of truth
- chords.py / gen.py stay authoritative).

Output schema (schema: 1):
    {"schema", "pack", "pack_file", "version", "generated", "source_rev", "counts",
     "tag_vocabulary", "progressions": [...], "chords": [...]}
"""

from __future__ import annotations

import argparse
import collections
import datetime
import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    Source, datetime_from_name, find_source, parse_entry, repo_root, tag_vocabulary,
    version_from_name,
)

SCHEMA = 1


def tempo_of(data: bytes) -> int | None:
    try:
        import io

        import mido

        for msg in mido.MidiFile(file=io.BytesIO(data)):
            if msg.type == "set_tempo":
                return round(60_000_000 / msg.tempo)
    except Exception:  # noqa: BLE001 - a missing/unreadable tempo is not fatal
        return None
    return None


def source_rev(repo: Path) -> str | None:
    try:
        return subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except Exception:  # noqa: BLE001 - not a git checkout, or git absent
        return None


def default_name(progressions: int, chords: int, today: str) -> str:
    """Name the index after what it actually contains, not after the input path."""
    kind = "free-midi-progressions" if not chords else "free-midi-chords"
    return f"{kind}-{today}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack", "--source", dest="pack",
                    help="release .zip or built pack directory (default: the freshest of dist/, output/, packs/)")
    ap.add_argument("--repo", help="free-midi-chords checkout")
    ap.add_argument("--out", help="output .json path (default: <repo>/dist/<name>.json)")
    ap.add_argument("--version", help="pack version label (default: from the archive name)")
    ap.add_argument("--read-midi", action="store_true",
                    help="also read the tempo of every MIDI (slower, sets 'bpm')")
    ap.add_argument("--jsonl", action="store_true", help="also write <out>.jsonl")
    ap.add_argument("--csv", action="store_true", help="also write <out>.csv")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    repo = repo_root(args.repo)
    pack = find_source(repo, args.pack)
    today = datetime_from_name(pack.name if pack.is_file() else "")
    version = args.version or (version_from_name(pack.name) if pack.is_file() else f"v0.{today}")

    progressions, chords = [], []
    with Source(pack) as source:
        for name in source.names():
            entry = parse_entry(name)
            if not entry:
                continue
            data = source.read(name)
            entry["sha256"] = hashlib.sha256(data).hexdigest()
            if entry["kind"] == "progression" and args.read_midi:
                entry["bpm"] = tempo_of(data)
            (progressions if entry["kind"] == "progression" else chords).append(entry)

    if not progressions and not chords:
        print(f"no .mid files found in {pack}", file=sys.stderr)
        return 1

    progressions.sort(key=lambda e: (e["mode"], e["key"], e["style"], e["length"], e["numerals"]))
    if args.out:
        out = Path(args.out)
    else:
        out = Path(repo) / "dist" / f"{default_name(len(progressions), len(chords), today)}.json"
    out.parent.mkdir(parents=True, exist_ok=True)

    index = {
        "schema": SCHEMA,
        "pack": "free-midi-chords" if chords else "free-midi-progressions",
        "pack_file": pack.name,
        "version": version,
        "generated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_rev": source_rev(repo),
        "counts": {
            "progressions": len(progressions),
            "chords": len(chords),
            "by_mode": dict(collections.Counter(e["mode"] for e in progressions)),
            "by_style": dict(collections.Counter(e["style"] for e in progressions)),
            "unique_numerals": len({e["numerals"] for e in progressions if e["style"] == "plain"}),
        },
        "tag_vocabulary": tag_vocabulary(progressions),
        "progressions": progressions,
        "chords": chords,
    }
    out.write_text(json.dumps(index, indent=1), encoding="utf-8")

    if args.jsonl:
        with out.with_suffix(".jsonl").open("w", encoding="utf-8") as fh:
            for entry in progressions + chords:
                fh.write(json.dumps(entry) + "\n")
    if args.csv:
        import csv

        cols = ["kind", "mode", "key", "style", "numerals", "tags", "length", "new",
                "symbol", "bpm", "path", "sha256"]
        with out.with_suffix(".csv").open("w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(cols)
            for entry in progressions + chords:
                row = dict(entry)
                row["tags"] = " ".join(row.get("tags", []) or [])
                row["numerals"] = row.get("numerals") or row.get("symbol", "")
                w.writerow([row.get(c, "") for c in cols])

    if not args.quiet:
        print(f"source      : {pack}")
        print(f"version     : {version}   source_rev: {index['source_rev']}")
        print(f"progressions: {len(progressions)}  ({index['counts']['by_mode']})")
        print(f"chords      : {len(chords)}")
        print(f"tags        : {len(index['tag_vocabulary'])} distinct")
        print(f"index       : {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())