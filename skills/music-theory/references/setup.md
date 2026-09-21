# Setup

## What is needed

1. A `free-midi-chords` checkout (the data generators and the chord engine live there).
2. The **modified python-mingus fork** beside it, as `python-mingus/` — the same thing the
   Makefile's `check` target requires to build the pack.
3. A Python environment with `MIDIUtil`, `pychord`, `mido` and the fork on the path.

```bash
git clone https://github.com/ldrolez/free-midi-chords.git
cd free-midi-chords
git clone https://github.com/ldrolez/python-mingus.git python-mingus
python3 -m venv .venv && . .venv/bin/activate          # Windows: .venv/Scripts/activate
pip install -r requirements.txt
```

Nothing else has to be downloaded to work on the pack: `make dist` builds it (see the Makefile)
and `make index` then indexes whatever it built. To work against a *released* pack instead, drop
the release archive in `packs/` — with no `--pack`, the scripts index the freshest thing they can
find (an archive in `dist/`, the built `output/` tree, or an archive in `packs/`).

## What each script actually needs

Only the two engine paths need the fork. Searching an existing index does not:

| Script | Needs |
| --- | --- |
| `find_progressions.py` | `python3` and an index — `--index` works with no checkout, no fork, no pack |
| `build_index.py` | `python3` and a pack archive or `output/` tree (`mido` for `--read-midi`, `git` for `source_rev`) |
| `render.py`, `verify_pack.py` | the checkout, `python-mingus/`, and `requirements.txt` |

`requirements.txt` is the entire third-party list; `python-mingus` is the only thing outside it.
Nothing in the skill touches the network, plays audio, or needs a DAW.

`--read-midi` is the one flag whose dependency is easy to lose: it reads each file's tempo with
`mido`, which lives in the interpreter, not the repo. `make index` calls plain `python3`, so on a
machine where that is a system python without `mido` the build succeeds with `bpm` null for every
file — it now warns and prints `bpm : 0/11400 files (no tempo read)`. Run the target inside the
venv (or with `python3` resolving there) to get the real `80`.

`FREE_MIDI_CHORDS_REPO` overrides the checkout location and `FREE_MIDI_CHORDS_PACK` the pack to
index; the scripts otherwise find the checkout from their own parent directories.

## Why the fork is mandatory

`requirements.txt` pins plain `mingus`, but the repo's Makefile `check` target insists on the
fork for a reason. `src/chords2midi/c2m.py` hands *numeral* tokens to mingus, and stock mingus
cannot spell several types that `chords.py` uses:

| Input | Stock mingus | With the fork |
| --- | --- | --- |
| `I I IM-5 IM-5 IV IV V Vsus2` (the pack's first Major progression) | `KeyError: 'M-5'` | renders |
| `bVIM7 ivmadd9 I` | `KeyError: 'madd9'` | renders |

Two practical consequences:

- `common.load_c2m()` puts `<repo>/python-mingus` at the front of `sys.path` before importing
  anything from mingus. Import mingus yourself and you may silently get the site-packages copy.
- A `KeyError` on a numeral is almost never bad input — it is the wrong mingus. Check the import
  path before "fixing" the progression.

The scripts run the engine in-process through `load_c2m()`. `make dist` instead sets
`PYTHONPATH=python-mingus/` for `gen.py`; both routes depend on the same fork.

## Platform notes

- On Windows, invoke the venv interpreter explicitly (`.venv/Scripts/python.exe`) and pass
  forward-slash paths to native tools.
- `c2m.py` calls `pkg_resources.require(...)` for its `--version` branch without importing
  `pkg_resources`; do not rely on wrappers passing `--version` through.
- The engine writes MIDI with `mido`/`MIDIUtil`, so no audio device or DAW is needed; nothing
  here plays or renders audio.

## Sanity check

```bash
make check                                     # python-mingus fork present
python skills/music-theory/scripts/render.py --numerals "I V vi IV" --key C --out out/smoke.mid
python skills/music-theory/scripts/find_progressions.py --vocab | head -5   # after make index
```