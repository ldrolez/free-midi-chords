---
name: music-theory
description: Compose, search and verify chord progressions and MIDI from the free-midi-chords pack.
---

# Music Theory (free-midi-chords)

Compose chord progressions, reharmonize, and render chord MIDI from the SHLD free-midi-chords
pack (13,536 MIDI files, 11,400 of them mood-tagged progressions across 12 keys x 5 rhythm
styles). Reuse the pack's curated data where it exists and the repo's own chord engine
everywhere. Never re-implement chord spelling — `src/chords2midi` in this checkout is the
authority, and its numeral dialect is narrower than it looks.

Commands below run from the repository root; the scripts find the checkout themselves
(`--repo`, or `FREE_MIDI_CHORDS_REPO`, or the script's own parent directories).

## Choose the path

| Request | Path |
| --- | --- |
| "nostalgic but hopeful, D minor" | `find_progressions.py --tags … --key …` then render with the flags the pack used |
| Compose something new | Invent numerals from the vocabulary → `render.py --validate-only` → render |
| Chord type numerals cannot spell (`7-5`, `add11`, `m7b9b5`, `9sus4`) | `render.py --symbols "F7-5 Cmaj7"` |
| Hand-written absolute chords, want the numerals | `render.py --reverse "C Am F G"` |
| Read the numerals as concrete pitches | `render.py --expand` |
| Ask what the pack actually contains | `make index` then `find_progressions.py --vocab` |
| Claim the pack is reproducible | `verify_pack.py` (never assert this without its output) |
| Mood words on percussion/bass instead of chords | Out of scope — this pack is chords only |

```text
mood + key -> find_progressions (index)  -> numerals + the tags that matched
numerals   -> validate_tokens            -> reject/repair before the engine runs
numerals   -> src/chords2midi (c2m)      -> MIDI (pattern, octave, bassline, bpm)
shipped    -> verify_pack                -> re-render vs the pack: exact / timing / notes
```

## Set up once

Read [references/setup.md](references/setup.md). The `python-mingus` fork is **not optional**:
with stock `pip install mingus` the pack's own first Major progression fails with
`KeyError: 'M-5'`, and `bVIM7 ivmadd9 I` fails with `KeyError: 'madd9'`.

## Build or reuse the index

The pack ships no manifest — key, mode, numerals, mood tags and style exist only in filenames.

```bash
make index                                             # after make dist -> dist/free-midi-progressions-<date>.json
python skills/music-theory/scripts/build_index.py       # freshest of dist/, output/, packs/
python skills/music-theory/scripts/build_index.py --pack ~/Downloads/free-midi-chords-20260314.zip
python skills/music-theory/scripts/build_index.py --read-midi --jsonl --csv
python skills/music-theory/scripts/find_progressions.py --vocab
python skills/music-theory/scripts/find_progressions.py --tags nostalgic,hopeful --format numerals
python skills/music-theory/scripts/find_progressions.py --tags dark --mode minor --key D --limit 10
```

A release `.zip` and a built `output/` tree are interchangeable inputs. The index is a build
output, never a source of truth: `chords.py` / `gen.py` stay authoritative, so it cannot disagree
with the pack for longer than one `make index`.

Default output groups by progression (one row per numerals, with the styles and key count that
carry it). Tag typos are reported with suggestions; keys are enharmonic-aware (`C#` matches `Db`).
Read [references/progressions-format.md](references/progressions-format.md) before parsing paths
by hand, and [references/pack-layout.md](references/pack-layout.md) before guessing where a file lives
(it also explains why an `output/` tree can hold each progression twice after `make dist`).

## Compose and render

Read [references/chord-naming.md](references/chord-naming.md) before writing numerals and
[references/rendering.md](references/rendering.md) before choosing flags.

```bash
python skills/music-theory/scripts/render.py --numerals "I V vi IV" --key D --pattern pop2 --bpm 96 --out out/d.mid
python skills/music-theory/scripts/render.py --numerals "bVIIM V7 I" --key a --style soul
python skills/music-theory/scripts/render.py --numerals "I  IV" --no-bassline          # double space = rest
python skills/music-theory/scripts/render.py --numerals "I V vi 7-5" --validate-only   # exits 2 before rendering
```

Render output is a JSON summary (path, pattern, bpm, seconds, pitches). Report that, not adjectives.

## Verify before claiming anything about the pack

```bash
python skills/music-theory/scripts/verify_pack.py --limit 50
python skills/music-theory/scripts/verify_pack.py --limit 0 --json out/verify-all.json   # every progression file

# exact reproduction needs the release-era source, not the current checkout:
python skills/music-theory/scripts/verify_pack.py --limit 0 --repo <release-era worktree> \
  --pack dist/free-midi-progressions-20260314.zip --index dist/free-midi-progressions-20260314.json
```

Statuses: `exact | timing | notes | render-failed`. Measured for v0.20260314: **11,400/11,400 exact**
from the release-era commit (`dfafc5a`), **8,390/11,400 exact** from current `main` — the remaining
3,010 differ by one voicing note (the post-release inversion change `b9fe0c3`), and nothing fails to
render. Never quote a reproducibility figure without naming the revision it came from.

## Never

- Invent a numeral suffix outside the supported vocabulary (see below) — it raises `KeyError`
at render time; use `--symbols` instead.
- Pass an uppercase key for a minor progression: `-k G#` raises
`NoteFormatError: unrecognized format for key 'G#'`. `gen.py` uses `root_min.lower()`.
- "Normalise" modal numerals (`bVIIM`, `bIIIM`, `im`). They are Ionian-relative by design;
rewriting them changes the harmony.
- Edit `chords.py` / `gen.py` to make a render fit. The pack is the input, not a scratchpad.
- Commit a generated index into the repository, or treat one as the pack itself: it is derived
data, rebuilt by `make index`, and shipped beside the release archives.
- Present a successful render or a playable file as evidence of musical quality. Say what was
rendered, in which key and pattern, and let the caller judge.

## Verified facts (pack v0.20260314)

| Fact | Value |
| --- | --- |
| Progression files | 11,400 = 12 keys x 5 rhythm styles x {Major 50, Minor 58, Modal 81} unique |
| Full pack `.mid` files | 13,536 (adds 1,632 "3 All chords", 336 "2 7th and 9th", 168 "1 Triad") |
| Index / manifest in the pack | none — metadata is filename-only |
| Mood tag vocabulary | 23 words, no schema, includes `New` (release recency) and `Cadence` (structural) |
| Numeral suffixes that render | 24 (see chord-naming.md); `M-5` only with the fork |
| Reproducibility, release-era source `dfafc5a` | 11,400 / 11,400 files re-render exactly |
| Reproducibility, current `main` (`b9fe0c3`) | 8,390 / 11,400 exact; 3,010 differ by one voicing note; 0 render errors |

Sources: the pack's own `chords.py` / `gen.py` / `src/chords2midi`, the release archives, and the
re-render checks in `verify_pack.py`. Licences: [references/licensing.md](references/licensing.md).