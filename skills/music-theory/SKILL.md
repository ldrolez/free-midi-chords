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
| Ask what the pack actually contains | `find_progressions.py --vocab` / `--slices` — both answer from the index manifest alone |
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

## What this skill depends on

Declared per path, because the search path is deliberately the cheap one.

| Path | Hard requirements | Optional |
| --- | --- | --- |
| `find_progressions.py` — search, `--vocab`, `--slices` | `python3` (3.8+; annotations are deferred, run on 3.10.11 / 3.11.15 / 3.14.6) and a generated index | nothing else — no `mingus`, no `chords2midi`, no pack archive, no MIDI file, no network, and no checkout at all when `--index` is given |
| `build_index.py` — `make index` | `python3` and a pack archive or a built `output/` tree | `mido` for `--read-midi`; `git` for `source_rev` |
| `render.py` | a checkout, the `python-mingus` fork beside it, and `requirements.txt` (`mido`, `MIDIUtil`, `pychord`, `mingus`, `packaging`) | — |
| `verify_pack.py` | everything `render.py` needs, plus a pack archive or `output/` tree, plus an index | — |

`requirements.txt` is the whole third-party list and `python-mingus` is the only thing outside it
(see [references/setup.md](references/setup.md)). Nothing here touches the network, plays audio or
needs a DAW: the render path writes a `.mid` and returns a JSON summary, nothing more. The split is
on purpose — an agent can be handed an index, or just the slice it needs, and search with a bare
`python3`.

## Build or reuse the index

The pack ships no manifest — key, mode, numerals, mood tags and style exist only in filenames.

```bash
make index                                             # after make dist -> dist/free-midi-progressions-<date>.json
python skills/music-theory/scripts/build_index.py       # freshest of dist/, output/, packs/
python skills/music-theory/scripts/build_index.py --pack ~/Downloads/free-midi-chords-20260314.zip
python skills/music-theory/scripts/build_index.py --read-midi --jsonl --csv --shards
python skills/music-theory/scripts/find_progressions.py --slices
python skills/music-theory/scripts/find_progressions.py --vocab
python skills/music-theory/scripts/find_progressions.py --tags nostalgic,hopeful --format numerals
python skills/music-theory/scripts/find_progressions.py --tags dark --mode minor --key D --limit 10
```

A release `.zip` and a built `output/` tree are interchangeable inputs. The index is a build
output, never a source of truth: `chords.py` / `gen.py` stay authoritative, so it cannot disagree
with the pack for longer than one `make index`.

### Read the slice, not the index

`--shards` (which `make index` passes) writes a second form beside the flat file: a
`manifest.json` plus one file per mode and key — `progressions/modal-Db.json`. The flat `.json`
stays the release asset (one file to attach); the shard directory is the read path, because a
request almost never needs all 11,400 rows:

| Query | Files read | Bytes read |
| --- | --- | --- |
| `--mode modal --key A --tags nostalgic` | 1 of 36 | 170 KiB of 4.5 MiB |
| `--tags anguished` (rarest tag in the pack) | 12 of 36 | 2.0 MiB of 4.5 MiB |
| `--tags nostalgic,hopeful` (both present in every slice) | 36 of 36 | 4.5 MiB of 4.5 MiB |

`--mode` / `--key` prune exactly — they are the slice key. `--tags` prunes on the per-slice tag
histogram in the manifest, which is a superset filter, so entries are still filtered after
loading (`--exclude-tags` never prunes). `--vocab` and `--slices` answer from the manifest alone
and read no slice at all. The stderr header reports what was read —
`# … 1/36 slices, 170.3 KiB of 4.5 MiB read | 100 pack files` — so this is checkable, not asserted.

`--index` takes the flat `.json`, the shard directory, or its `manifest.json`; with no flag the
newer of the two forms in `dist/` wins. Given an index, `find_progressions.py` needs no checkout.

`--read-midi` fills `bpm` with `mido`, which lives in the interpreter rather than the repo: run it
under a python without `mido` and every `bpm` is silently null. The build now warns and prints
`bpm : 0/11400 files (no tempo read)` — read that line before quoting a tempo (the shipped pack is
all 80).

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