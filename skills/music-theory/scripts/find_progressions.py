#!/usr/bin/env python3
"""Search the generated progression index by mood tags, key, mode, length.

    python skills/music-theory/scripts/find_progressions.py --vocab
    python skills/music-theory/scripts/find_progressions.py --tags nostalgic,hopeful --format numerals
    python skills/music-theory/scripts/find_progressions.py --tags dark --mode minor --key D --limit 10
    python skills/music-theory/scripts/find_progressions.py --tags joyful --style pop2 --format json
    python skills/music-theory/scripts/find_progressions.py --tags nostaligc            # typo -> suggestions
"""

from __future__ import annotations

import argparse
import difflib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ENHARMONIC, PACK_STYLES, find_index, repo_root  # noqa: E402


def load(args):
    path = find_index(repo_root(args.repo), args.index)
    return json.loads(Path(path).read_text(encoding="utf-8")), path


def normalize_keys(keys):
    """Accept enharmonic spellings (C# / Db) so callers are not surprised by pack spelling."""
    wanted = set(keys)
    for k in keys:
        if k in ENHARMONIC:
            wanted.add(ENHARMONIC[k])
    return wanted


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--index", help="index .json (default: newest in <repo>/index)")
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
    args = ap.parse_args()

    index, path = load(args)
    entries = index["progressions"]

    if args.vocab:
        print(f"{path}  ({index['version']}, {len(entries)} progression files)")
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
        if args.key and e["key"] not in normalize_keys({k.strip() for k in args.key.split(",")}):
            return False
        if args.style and e["style"] not in {s.strip() for s in args.style.split(",")}:
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

    print(f"# {path} | version {index['version']} | {len(hits)} pack files"
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