#!/usr/bin/env python3
"""Re-render indexed progressions with the repo's engine and diff them against the pack.

This is the skill's evidence tool: it answers "can the composition path actually reproduce
what the pack ships?" instead of assuming it.

    python skills/music-theory/scripts/verify_pack.py --limit 50
    python skills/music-theory/scripts/verify_pack.py --mode modal --style plain
    python skills/music-theory/scripts/verify_pack.py --limit 0 --json out/verify-all.json

Statuses: exact | timing | notes | render-failed.
"""

from __future__ import annotations

import argparse
import io
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    Source, find_source, human_bytes, load_c2m, load_index, repo_root,
)


def note_grid(source) -> list[tuple[int, int, int]]:
    """(onset_ticks, note, duration_ticks) for every note, merged across tracks."""
    import mido

    mf = mido.MidiFile(file=source) if hasattr(source, "read") else mido.MidiFile(source)
    t = 0
    open_at: dict[tuple[int, int], int] = {}
    events = []
    for msg in mf:
        t += msg.time
        if msg.type == "note_on" and msg.velocity:
            open_at[(msg.channel, msg.note)] = t
        elif msg.type == "note_off" or (msg.type == "note_on" and not msg.velocity):
            key = (msg.channel, msg.note)
            if key in open_at:
                start = open_at.pop(key)
                events.append((start, msg.note, t - start))
    return sorted(events)


def pack_recipe(entry) -> list[str]:
    """Exactly the argv gen.py's genprog() builds, minus the bits that only affect the name."""
    args = list(entry["tokens"])
    if entry["style"] != "plain":
        args += ["-p", entry["style"]]
    elif "X" in entry["tokens"]:
        args += ["-d", "2", "-p", "basic"]
    else:
        args += ["-d", "1", "-p", "long"]
    key = entry["key"].lower() if entry["mode"] == "minor" else entry["key"]
    return args + ["-t", "5", "-B", "--key", key, "-N", "verify", "--output", ""]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack", "--source", dest="pack",
                    help="release .zip or built pack directory (default: the freshest of dist/, output/, packs/)")
    ap.add_argument("--index", help="index .json (default: newest in dist/, then index/)")
    ap.add_argument("--repo", help="free-midi-chords checkout")
    ap.add_argument("--mode", choices=["major", "minor", "modal"])
    ap.add_argument("--style")
    ap.add_argument("--limit", type=int, default=50, help="0 = every matching file")
    ap.add_argument("--json", help="write a machine-readable report here")
    args = ap.parse_args()

    repo = repo_root(args.repo)
    loaded = load_index(repo, args.index, mode=args.mode, kinds=("progression",))
    index_path, meta, all_entries = loaded["path"], loaded["meta"], loaded["entries"]
    pack = find_source(repo, args.pack)
    c2m = load_c2m(repo)

    with Source(pack) as source:
        shipped_names = set(source.names())
        entries = [e for e in all_entries
                   if e["path"] in shipped_names
                   and (not args.mode or e["mode"] == args.mode)
                   and (not args.style or e["style"] == args.style)]
        if args.limit:
            entries = entries[: args.limit]
        if not entries:
            print("nothing to verify - check --pack/--index/--mode/--style", file=sys.stderr)
            return 1

        results, counts = [], Counter()
        with tempfile.TemporaryDirectory() as tmp:
            for entry in entries:
                shipped = note_grid(io.BytesIO(source.read(entry["path"])))
                out = Path(tmp) / "verify.mid"
                argv = pack_recipe(entry)
                argv[-1] = str(out)
                record = {"path": entry["path"], "mode": entry["mode"], "style": entry["style"]}
                try:
                    with io.StringIO() as _buf:
                        c2m.Chords2Midi().handle(argv)
                    ours = note_grid(out)
                except Exception as exc:  # noqa: BLE001
                    record.update(status="render-failed", error=f"{type(exc).__name__}: {exc}")
                    results.append(record)
                    counts["render-failed"] += 1
                    continue

                if Counter(ours) == Counter(shipped):
                    record["status"] = "exact"
                elif Counter((n, d) for _, n, d in ours) == Counter((n, d) for _, n, d in shipped):
                    record["status"] = "timing"
                    record["onset_only_diff"] = True
                elif sorted(n for _, n, _ in ours) == sorted(n for _, n, _ in shipped):
                    record["status"] = "timing"
                else:
                    record["status"] = "notes"
                    record["missing_notes"] = sorted(set(n for _, n, _ in shipped) - set(n for _, n, _ in ours))
                    record["extra_notes"] = sorted(set(n for _, n, _ in ours) - set(n for _, n, _ in shipped))
                results.append(record)
                counts[record["status"]] += 1

    print(f"pack  : {pack}")
    print(f"index : {index_path} ({meta['version']})"
          + (f" - {len(loaded['slices'])}/{loaded['slices_total']} slices, "
             f"{human_bytes(loaded['bytes_read'])} read" if loaded["sharded"] else ""))
    print(f"checked {len(results)} progression files")
    for status, count in counts.most_common():
        print(f"  {status:<14} {count}")
    bad = [r for r in results if r["status"] != "exact"]
    for record in bad[:10]:
        print(f"  ! {record['status']:<13} {record['path']} "
              f"{record.get('error') or record.get('missing_notes') or ''}")
    if len(bad) > 10:
        print(f"  ... {len(bad) - 10} more non-exact results")
    if args.json:
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json).write_text(json.dumps(
            {"pack": str(pack), "index": str(index_path), "counts": dict(counts),
             "results": results}, indent=1), encoding="utf-8")
        print(f"report: {args.json}")
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())