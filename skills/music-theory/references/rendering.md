# Rendering

## The engine

`src/chords2midi/c2m.py` (`c2m.Chords2Midi().handle(argv)`) is the only renderer. It parses
numerals or absolute symbols with mingus/pychord and writes MIDI via `MIDIUtil`.

## Flags that matter

| flag | meaning | pack's choice |
| --- | --- | --- |
| `--key` | scale root; **lowercase for minor** (`-k g#`) | `root_maj` for Major/Modal, `root_min.lower()` for Minor |
| `-p/--pattern` | rhythm pattern (14 available) | `long` (rest-free progressions), `basic` (with rests), or the style name |
| `-d/--duration` | beats per chord | `1` with `long`, `2` with `basic`, `4` for single chord-library files |
| `-t/--octave` | octave(s); `5` keeps chords in a pad-friendly register | `5` |
| `-B/--bassline` | adds a bass track | always on in the pack |
| `-b/--bpm` | tempo | default `80`; every shipped file is 80 |
| `-H/--humanize` | strum offset in ticks (try `.11`) | off |
| `-O/--offset` | ticks offset per chord | off |
| `-n/--notes` | cap notes per chord | unlimited |
| `--no-longeven` | disables doubling the last chord of odd-length progressions | default (doubling on) |
| `-r/--reverse` | print numerals for absolute chords, write nothing | — |

Patterns (`src/chords2midi/c2mpatterns.py`): `long, basic, basic2, basic4, alt, alt2, alt3,
hiphop, hiphop2, hiphop3, pop, pop2, soul, soul2`. Pattern tokens are `<beats><N|S|X>` where N =
next chord, S = sustain, X = rest.

Pack rhythm styles = `plain | pop | pop2 | soul | hiphop2` (sibling directories). `render.py --style
pop2` uses the same pattern the pack used, so a re-render can be compared against the shipped file.

## Recipes (mirror these when verifying)

```python
# genprog(): progressions
[tokens…] + (['-p', style] if style else (['-d','2','-p','basic'] if 'X' in tokens else ['-d','1','-p','long'])) \
         + ['-t','5','-B','--key', key, '-N', name, '--output', out]

# gen(): single chord-library file
[symbol] + ['-t','5','-p','long','-d','4','-B','--key', key, '-N', name, '--output', out]
```

`verify_pack.py` builds exactly the first recipe; that is why its `exact` status is meaningful.

## What the output contains

Tempo 80, ticks-per-beat 960, 2 tracks (chords + bassline), and a track name of `<prefix> -
<numerals>` — the mood tags are **not** in the MIDI, only in the filename. Metadata such as key,
mode and tags must therefore come from the index or the path.

## Pitfalls

- Uppercase minor key → `NoteFormatError: unrecognized format for key 'G#'`. Lowercase it.
- A numeral with an unsupported suffix → `KeyError: '<suffix>'` from mingus (e.g. `KeyError:
  'm7b9b5'`). Validate first (`render.py --validate-only`) or use `--symbols`.
- `c2m.py --version` calls `pkg_resources` without importing it; avoid the flag.
- Slash chords in filenames are replaced with `_`; the notes are unaffected.
- The engine writes a file only if the argv parses; a script that swallows stdout may look
  successful while writing nothing. Check the path exists, then parse it (`render.py` does both and
  reports pitch content).

## Reproducibility: pin the source revision

The pack reproduces, but only from the source that built it:

| Generator revision | Result over the 11,400 progression files of v0.20260314 |
| --- | --- |
| `dfafc5a` (2026-02-28, release-era) | 11,400 exact |
| `b9fe0c3` (2026-09-12, current `main`) | 8,390 exact, 3,010 differ by one voicing note, 0 errors |

`b9fe0c3` added "repeat chord voicings climb an octave on every 4th chord", which moves one note in
the affected progressions. Releases record no source revision of their own, so recreate the right
one before making exactness claims:

```bash
git worktree add --detach ../free-midi-chords-at-release dfafc5a
cp -r python-mingus ../free-midi-chords-at-release/python-mingus   # the fork is not in a fresh worktree
python skills/music-theory/scripts/verify_pack.py --limit 0 \
  --repo ../free-midi-chords-at-release \
  --pack dist/free-midi-progressions-20260314.zip \
  --index dist/free-midi-progressions-20260314.json
```

`--repo` selects which `src/chords2midi` runs, so this is a real A/B of the generator rather than a
re-label of the same output. With only the current checkout available, "8,390 exact, 3,010 voicing
differences" is the honest statement for HEAD.
