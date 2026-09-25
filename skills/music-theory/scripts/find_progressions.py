#!/usr/bin/env python3
"""Search the generated progression index by mood tags, key, mode, length.

    python skills/music-theory/scripts/find_progressions.py --vocab
    python skills/music-theory/scripts/find_progressions.py --tags nostalgic,hopeful --format numerals
    python skills/music-theory/scripts/find_progressions.py --tags dark --mode minor --key D --limit 10
    python skills/music-theory/scripts/find_progressions.py --tags joyful --style pop2 --format json
    python skills/music-theory/scripts/find_progressions.py --tags nostaligc            # typo -> suggestions

`--index` takes either the flat `free-midi-progressions-<date>.json` or the shard
directory `free-midi-progressions-<date>/`. With shards, only the slices the query can
match are read - `--mode`/`--key` prune exactly, `--tags` prunes conservatively - and the
bytes read are reported on stderr, so "load only the slice it needs" is checkable.
"""

from __future__ import annotations

import argparse
import difflib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    ENHARMONIC, PACK_STYLES, human_bytes, load_index, repo_root_or_none,
)


def normalize_keys(keys):
    """Accept enharmonic spellings (C# / Db) so callers are not surprised by pack spelling."""
    wanted = set(keys)
    for k in keys:
        if k in ENHARMONIC:
            wanted.add(ENHARMONIC[k])
    return wanted


def tags_of(args):
    """The tags this query must see - the slice pruning bound (excludes never prune)."""
    wanted = set()
    for field in ("tags", "tags_any"):
        value = getattr(args, field)
        if value:
            wanted |= {t.strip().lower() for t in value.split(",") if t.strip()}
    return wanted or None


def split(value):
    return {v.strip() for v in value.split(",") if v.strip()}


def print_slices(loaded, path):
    if not loaded["sharded"]:
        print(f"{path} is a flat index - one file, nothing to slice.\n"
              "Rebuild with `--shards` (or `make index`) to get one file per key/mode.")
        return 0
    print(f"{path}  ({loaded['meta']['version']}, {loaded['slices_total']} slices, "
          f"{human_bytes(loaded['bytes_total'])})")
    print(f"{'slice':<32} {'mode':<6} {'key':<4} {'n':>5} {'bytes':>9}  tags")
    for record in loaded["slices"]:
        top = ", ".join(f"{tag} {count}" for tag, count in list((record.get("tags") or {}).items())[:3])
        print(f"{record['slice']:<32} {record.get('mode', ''):<6} {record.get('key', ''):<4} "
              f"{record['entries']:>5} {human_bytes(record['bytes']):>9}  {top}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--index", help="flat index .json, or a shard directory (default: newest in dist/, then index/)")
    ap.add_argument("--repo", help="free-midi-chords checkout")
    ap.add_argument("--tags", help="comma-separated mood tags, ALL must match")
    ap.add_argument("--tags-any", help="comma-separated mood tags, ANY may match")
    ap.add_argument("--exclude-tags", help="comma-separated tags to exclude")
    ap.add_argument("--key", help="comma-separated keys (enharmonic-aware)")
    ap.add_argument("--mode", choices=["major", "minor", "modal"])
    ap.add_argument("--style", help="comma-separated rhythm styles (plain,pop,pop2,soul,hiphop2)")
    ap.add_argument("--new", dest="new", action="store_true", default=None, help="only 'New'-tagged")
    ap.add_argument("--no-new", dest="new", action="store_false", help="exclude 'New'-tagged")
    ap.add_argument("--min-chords", type=int, dest="min_chords")
    ap.add_argument("--max-chords", type=int, dest="max_chords")
    ap.add_argument("--limit", type=int, default=20, help="rows to show (0 = all)")
    ap.add_argument("--group", dest="group", action="store_true", default=None,
                    help="one row per progression, collapsing keys/styles (default: on unless "
                         "--key or --style is given)")
    ap.add_argument("--no-group", dest="group", action="store_false")
    ap.add_argument("--format", choices=["table", "json", "numerals", "paths"], default="table")
    ap.add_argument("--vocab", action="store_true", help="print the tag vocabulary with counts")
    ap.add_argument("--slices", dest="slices", action="store_true",
                    help="print the index's slices and what each holds (manifest only, no data read)")
    args = ap.parse_args()

    repo = repo_root_or_none(args.repo)  # an explicit --index works with no checkout at all
    keys = normalize_keys(split(args.key)) if args.key else None
    meta_only = bool(args.vocab or args.slices)
    loaded = load_index(repo, args.index, mode=args.mode, keys=keys, tags=tags_of(args),
                        kinds=("progression",), entries=not meta_only)
    index, path, entries = loaded["meta"], loaded["path"], loaded["entries"]

    if args.slices:
        return print_slices(loaded, path)

    if args.vocab:
        print(f"{path}  ({index['version']}, {index['counts']['progressions']} progression files"
              f"{', manifest only - no slice read' if loaded['sharded'] else ''})")
        for tag, count in index["tag_vocabulary"].items():
            print(f"  {tag:<12} {count}")
        return 0

    vocab = list(index["tag_vocabulary"])
    for field in ("tags", "tags_any", "exclude_tags"):
        value = getattr(args, field)
        if not value:
            continue
        for tag in (t.strip().lower() for t in value.split(",") if t.strip()):
            if tag not in vocab:
                near = difflib.get_close_matches(tag, vocab, n=3, cutoff=0.6)
                print(f"warning: {tag!r} is not in the pack's tag vocabulary"
                      + (f" - did you mean {', '.join(near)}?" if near else ""), file=sys.stderr)

    def keep(e):
        tags = set(e["tags"])
        if args.tags and not {t.strip().lower() for t in args.tags.split(",")}.issubset(tags):
            return False
        if args.tags_any and not tags & {t.strip().lower() for t in args.tags_any.split(",")}:
            return False
        if args.exclude_tags and tags & {t.strip().lower() for t in args.exclude_tags.split(",")}:
            return False
        if args.mode and e["mode"] != args.mode:
            return False
        if args.key and e["key"] not in keys:
            return False
        if args.style and e["style"] not in split(args.style):
            return False
        if args.new is not None and e["new"] != args.new:
            return False
        if args.min_chords and e["length"] < args.min_chords:
            return False
        if args.max_chords and e["length"] > args.max_chords:
            return False
        return True

    hits = [e for e in entries if keep(e)]
    rank = {name: i for i, name in enumerate(PACK_STYLES)}
    hits.sort(key=lambda e: (e["mode"], rank.get(e["style"], 99), e["length"], e["numerals"], e["key"]))

    group = args.group if args.group is not None else (not args.key and not args.style)
    if group:
        grouped: dict[tuple[str, str], dict] = {}
        for e in hits:
            g = grouped.setdefault((e["mode"], e["numerals"]), {
                "mode": e["mode"], "numerals": e["numerals"], "tags": e["tags"],
                "length": e["length"], "keys": set(), "styles": set(), "example": e["path"]})
            g["keys"].add(e["key"])
            g["styles"].add(e["style"])
        rows = sorted(grouped.values(), key=lambda g: (g["mode"], g["length"], g["numerals"]))
    else:
        rows = hits

    print(f"# {path} | version {index['version']} | "
          + (f"{len(loaded['slices'])}/{loaded['slices_total']} slices, "
             f"{human_bytes(loaded['bytes_read'])} of {human_bytes(loaded['bytes_total'])} read | "
             if loaded["sharded"] else
             f"flat index, {human_bytes(loaded['bytes_read'])} read | ")
          + f"{len(hits)} pack files"
          + (f" -> {len(rows)} unique progressions" if group else ""), file=sys.stderr)
    shown = rows if args.limit == 0 else rows[: args.limit]

    if args.format == "json":
        print(json.dumps([{**r, "keys": sorted(r["keys"]), "styles": sorted(r["styles"])}
                          if group else r for r in shown], indent=1))
    elif args.format == "numerals":
        for r in shown:
            print(r["numerals"])
    elif args.format == "paths":
        for r in shown:
            print(r["example"] if group else r["path"])
    elif group:
        print(f"{'mode':<6} {'n':>2}  {'numerals':<44} {'keys':>4} styles            tags")
        for r in shown:
            print(f"{r['mode']:<6} {r['length']:>2}  {r['numerals']:<44} {len(r['keys']):>4} "
                  f"{','.join(sorted(r['styles'])):<18} {' '.join(r['tags'])}")
    else:
        print(f"{'mode':<6} {'key':<4} {'style':<8} {'n':>2}  {'numerals':<44} tags")
        for r in shown:
            print(f"{r['mode']:<6} {r['key']:<4} {r['style']:<8} {r['length']:>2}  "
                  f"{r['numerals']:<44} {' '.join(r['tags'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())