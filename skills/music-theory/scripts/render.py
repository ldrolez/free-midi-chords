#!/usr/bin/env python3
"""Render a numeral progression (or absolute chord symbols) to MIDI with the repo's engine.

This wraps src/chords2midi - the same code that produced the pack - so a composition made
here and a file from the pack come from one implementation.

    python skills/music-theory/scripts/render.py --numerals "I V vi IV" --key D --pattern pop2 --out out/d-pop2.mid
    python skills/music-theory/scripts/render.py --numerals "bVIIM V7 I" --key a --style soul
    python skills/music-theory/scripts/render.py --numerals "I  IV" --bassline          # double space = rest
    python skills/music-theory/scripts/render.py --symbols "Am7b9b5 G7-5 Cmaj7" --key C # types numerals can't spell
    python skills/music-theory/scripts/render.py --reverse "C Am F G"                   # chords -> numerals
    python skills/music-theory/scripts/render.py --numerals "I vi IV V" --validate-only
    python skills/music-theory/scripts/render.py --numerals "I I IM-5 IM-5 IV IV V Vsus2" --expand

Recipes mirror gen.py: progressions use -t 5 -B with -d 1 -p long (rest-free) or
-d 2 -p basic (with rests); pack rhythm subdirectories use -p <style>. Single chord-library
symbols use -t 5 -p long -d 4 -B.
"""

from __future__ import annotations

import argparse
import io
import json
import contextlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_c2m, repo_root, validate_tokens  # noqa: E402


def build_args(tokens, key, style, pattern, duration, octave, bassline, out, name):
    args = list(tokens)
    if pattern:
        args += ["-p", pattern]
    elif style:
        args += ["-p", style]
    elif " X " in " ".join(tokens):
        args += ["-d", "2", "-p", "basic"]
    else:
        args += ["-d", "1", "-p", "long"]
    if duration is not None:
        args += ["-d", str(duration)]
    args += ["-t", str(octave)]
    if bassline:
        args += ["-B"]
    if name:
        args += ["-N", name]
    args += ["--key", key, "--output", str(out)]
    return args


def expand_symbols(tokens, key, repo):
    """Numerals -> absolute chord symbols, via the same engine the renderer uses.

    The fork must be on sys.path *before* mingus is imported: stock mingus rejects the
    suffix 'M-5', which the pack ships ('I I IM-5 IM-5 IV IV V Vsus2').
    """
    load_c2m(repo)
    from mingus.core.progressions import to_chords

    table = to_chords([t for t in tokens if t != "X"], key)
    return [" ".join(c) for c in table]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--numerals", help="numeral progression, e.g. 'I V vi IV'")
    ap.add_argument("--symbols", help="absolute chord symbols, e.g. 'Am7 G7-5 Cmaj7'")
    ap.add_argument("--reverse", help="chord symbols -> numerals")
    ap.add_argument("--key", default="C", help="key; MINOR KEYS MUST BE LOWERCASE ('a', not 'A')")
    ap.add_argument("--style", help="pack rhythm style (pop, pop2, soul, hiphop2)")
    ap.add_argument("--pattern", help="engine pattern (long, basic, hiphop, pop, soul, ...)")
    ap.add_argument("--duration", type=float)
    ap.add_argument("--octave", default="5", help="default 5, as gen.py uses for the pack")
    ap.add_argument("--bpm", type=int, default=80)
    ap.add_argument("--bassline", action="store_true", default=True)
    ap.add_argument("--no-bassline", dest="bassline", action="store_false")
    ap.add_argument("--out", help="output .mid path")
    ap.add_argument("--repo", help="free-midi-chords checkout")
    ap.add_argument("--validate-only", action="store_true", help="check the numeral vocabulary only")
    ap.add_argument("--expand", action="store_true", help="print absolute chord symbols, write nothing")
    args = ap.parse_args()

    if args.reverse:
        repo = repo_root(args.repo)
        c2m = load_c2m(repo)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            try:
                # -r reads the symbols against the key (C unless --key says otherwise).
                c2m.Chords2Midi().handle(args.reverse.split() + ["-r", "--key", args.key])
            except SystemExit:
                pass
            except Exception as exc:  # noqa: BLE001 - mingus raises bare ValueError for minor keys
                print(f"reverse failed: {type(exc).__name__}: {exc}\n"
                      "  -r reads the symbols against a MAJOR scale: pass an uppercase root"
                      " (--key G), or spell the answer as numerals yourself.", file=sys.stderr)
                return 2
        print(buf.getvalue().strip() or "(no output)")
        return 0

    if not args.numerals and not args.symbols:
        ap.error("supply --numerals, --symbols or --reverse")

    tokens = (args.numerals or args.symbols).split()

    if args.numerals or args.validate_only:
        bad = validate_tokens(tokens)
        if bad:
            print("cannot render as numerals:", file=sys.stderr)
            for token, reason in bad:
                print(f"  {token:<12} {reason}", file=sys.stderr)
            print("\nfix: use --symbols for chord types outside the numeral vocabulary,\n"
                  "     or scripts/find_progressions.py for progressions known to render.", file=sys.stderr)
            return 2
    if args.validate_only:
        print("ok: all tokens are renderable as numerals")
        return 0

    if args.expand:
        if not args.numerals:
            ap.error("--expand needs --numerals")
        print(json.dumps({"numerals": args.numerals, "key": args.key,
                          "symbols": expand_symbols(tokens, args.key, repo_root(args.repo))}, indent=1))
        return 0

    repo = repo_root(args.repo)
    c2m = load_c2m(repo)
    out = Path(args.out) if args.out else Path(repo) / "out" / f"render-{abs(hash(args.numerals or args.symbols)) % 10**8}.mid"
    out.parent.mkdir(parents=True, exist_ok=True)

    if args.symbols:
        # chord-library recipe from gen.py
        argv = list(tokens) + ["-t", str(args.octave), "-p", args.pattern or "long",
                               "-d", str(args.duration or 4)] + (["-B"] if args.bassline else [])
        argv += ["--key", args.key, "-b", str(args.bpm), "--output", str(out)]
    else:
        argv = build_args(tokens, args.key, args.style, args.pattern, args.duration,
                          args.octave, args.bassline, out, args.numerals)
        argv += ["-b", str(args.bpm)]

    c2m.Chords2Midi().handle(argv)
    if not out.exists():
        print("renderer produced no file", file=sys.stderr)
        return 1

    import mido

    mf = mido.MidiFile(out)
    tempo = next((round(60_000_000 / m.tempo) for m in mf if m.type == "set_tempo"), None)
    pitches = sorted({m.note for m in mf if m.type == "note_on" and m.velocity})
    print(json.dumps({
        "out": str(out), "numerals": args.numerals, "symbols": args.symbols, "key": args.key,
        "pattern": args.pattern or args.style or "long/basic (auto)",
        "bpm": tempo, "seconds": round(mf.length, 2), "pitches": pitches,
        "tracks": len(mf.tracks),
    }, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())