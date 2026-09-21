#!/usr/bin/env python3
"""Build a machine-readable index of a free-midi-chords pack.

The pack ships no manifest: key, mode, numerals, mood tags and rhythm style exist only
inside filenames (and the MIDI track name). This script extracts them once so agents and
scripts can query instead of scraping paths.

    python skills/music-theory/scripts/build_index.py                  # newest dist/ archive
    python skills/music-theory/scripts/build_index.py --pack output    # a built pack tree
    python skills/music-theory/scripts/build_index.py --pack ~/Downloads/free-midi-chords-20260314.zip
    python skills/music-theory/scripts/build_index.py --read-midi --jsonl --csv --shards

Inputs are interchangeable: the release `.zip`, or the `output/` tree `make dist` cuts it
from. Output goes to `dist/<name>.json` by default (a build output, never a source of truth
- chords.py / gen.py stay authoritative); `--shards` adds `dist/<name>/` beside it, which is
what a query reads slice-by-slice instead of loading the whole file.

Output schema (schema: 1):
    {"schema", "pack", "pack_file", "version", "generated", "source_rev", "counts",
     "tag_vocabulary", "progressions": [...], "chords": [...]}

Shard directory (schema: 1):
    <name>/manifest.json                  header + one record per slice (no payload)
    <name>/progressions/<mode>-<key>.json one slice per mode x key, in pack spelling
    <name>/chords.json                    chord-library slice, when the input has one
"""

from __future__ import annotations

import argparse
import collections
import datetime
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    MODES, Source, datetime_from_name, find_source, human_bytes, parse_entry, repo_root,
    tag_vocabulary, version_from_name,
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


def slice_record(name: str, entries: list[dict], blob: bytes) -> dict:
    """One slice: its path inside the shard directory, plus what it holds (no payload)."""
    record = {
        "slice": name,
        "kind": entries[0]["kind"] if entries else None,
        "entries": len(entries),
        "bytes": len(blob),
        "sha256": hashlib.sha256(blob).hexdigest(),
    }
    if record["kind"] == "progression":
        record["mode"] = entries[0]["mode"]
        record["key"] = entries[0]["key"]
        # Per-slice tag histogram: lets a caller decide whether it needs this slice
        # without reading it. Marginal counts only - the intersection of two tags needs
        # the entries, so a tag-pruned read is a superset, never a false negative.
        record["tags"] = dict(sorted(collections.Counter(
            t for e in entries for t in e["tags"]).items(), key=lambda kv: (-kv[1], kv[0])))
    return record


def write_shards(shard_dir: Path, index: dict, progressions: list[dict], chords: list[dict],
                 flat_index: str | None = None) -> dict:
    """Write a sharded index: manifest.json + one file per (mode, key) + chords.json.

    The flat `.json` stays the release asset; this is the read path, so an agent or a DAW
    script ready to load a 5 MB file can load the ~100 kB slice a query actually needs.
    """
    shutil.rmtree(shard_dir, ignore_errors=True)  # build output: drop stale slices
    (shard_dir / "progressions").mkdir(parents=True, exist_ok=True)

    slices, payloads = [], []
    order = {mode: i for i, mode in enumerate(MODES)}
    grouped: dict[tuple[str, str], list[dict]] = collections.defaultdict(list)
    for entry in progressions:
        grouped[(entry["mode"], entry["key"])].append(entry)
    for group in sorted(grouped, key=lambda gk: (order.get(gk[0], 99), gk[1])):
        mode, key = group
        payloads.append((f"progressions/{mode}-{key}.json", grouped[group]))
    if chords:
        payloads.append(("chords.json", chords))

    for name, entries in payloads:
        # Write bytes, not text: text mode would turn every "\n" into "\r\n" on Windows,
        # so the recorded sha256 and byte count would describe a file nobody has.
        blob = json.dumps(entries, indent=1).encode("utf-8")
        (shard_dir / name).write_bytes(blob)
        slices.append(slice_record(name, entries, blob))

    manifest = {
        "schema": SCHEMA,
        "kind": "manifest",
        "pack": index["pack"],
        "pack_file": index["pack_file"],
        "version": index["version"],
        "generated": index["generated"],
        "source_rev": index["source_rev"],
        "flat_index": flat_index,  # the single-file index this is a read path for
        "counts": index["counts"],
        "tag_vocabulary": index["tag_vocabulary"],
        "bytes": sum(s["bytes"] for s in slices),
        "slices": slices,
    }
    (shard_dir / "manifest.json").write_bytes(json.dumps(manifest, indent=1).encode("utf-8"))
    return manifest


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
    ap.add_argument("--shards", action="store_true",
                    help="also write a sharded copy beside <out>: <out without .json>/"
                         "manifest.json + one file per key/mode, so a query reads only its slice")
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
    tempos = sum(1 for e in progressions if e.get("bpm") is not None)
    if args.read_midi and not tempos:
        # Silent nulls are worse than an error: mido lives in the interpreter, not in the repo,
        # so `make index` under a python3 without it marks every file as tempo-less.
        print(f"warning: --read-midi read no tempo from any of {len(progressions)} files - "
              "is mido installed for the interpreter running this? 'bpm' is null throughout.",
              file=sys.stderr)
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
    # Byte-written so the output is identical on every platform (text mode would write
    # "\r\n" on Windows, which the recorded slice sha256s would not match).
    out.write_bytes(json.dumps(index, indent=1).encode("utf-8"))

    manifest = None
    if args.shards:
        manifest = write_shards(out.with_suffix(""), index, progressions, chords, flat_index=out.name)

    if args.jsonl:
        with out.with_suffix(".jsonl").open("w", encoding="utf-8", newline="\n") as fh:
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
        if args.read_midi:
            bpms = sorted({e["bpm"] for e in progressions if e.get("bpm") is not None})
            print(f"bpm         : {tempos}/{len(progressions)} files"
                  + (f", {', '.join(str(b) for b in bpms)}" if bpms else " (no tempo read)"))
        print(f"index       : {out}  ({human_bytes(out.stat().st_size)})")
        if manifest:
            biggest = max(manifest["slices"], key=lambda s: s["bytes"])
            print(f"shards      : {out.with_suffix('')} "
                  f"({len(manifest['slices'])} slices, {human_bytes(manifest['bytes'])} total; "
                  f"largest {biggest['slice']} {human_bytes(biggest['bytes'])})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())