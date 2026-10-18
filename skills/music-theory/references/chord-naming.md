# Chord naming

Two dialects reach `src/chords2midi`, and they do not accept the same vocabulary.

## Dialect 1 — numerals (degrees + suffix in one token)

Grammar: `<b|#>*<roman degree><quality suffix>`, e.g. `I`, `vi`, `bVIIM`, `ivmadd9`, `#IVdim`, `bi`.

- Uppercase degree = major triad root, lowercase = minor triad root; the **suffix then spells the
  rest**, which is why `bIIIM` and `im` are both valid and mean different qualities.
- Accidental prefixes are relative to the Ionian scale of the key, per the README's modal rule.
- Rests: two spaces in `chords.py` become an `X` token (`gen.py` substitutes `'  ' -> ' X '`).

Verified renderable suffixes (24) against the fork: `''` `m` `M` `dim` `dim7` `m7` `M7` `m9` `M9`
`9` `6` `69` `m6` `M6` `7` `sus2` `sus4` `add9` `madd9` `mM7` `M7+5` `M-5` `dom7` `5`.

Suffixes that **raise `KeyError`** as numerals (19): `2` `5sus4` `m69` `7sus4` `add4` `madd4`
`add11` `dim6` `7-5` `7+5` `m7-5` `m7+5` `7-9` `7+11` `sus4add9` `9sus4` `m7b9b5` `m7add11`
`mM7add11`. These are real chord types in `chords.py` (`chord_types_maj` / `chord_types_min`) and
they ship in "3 All chords" as absolute symbols, so they are reachable — just not as numerals.

`M-5` is the trap inside the trap: it is in the renderable list **only** with the fork, and it is
in the pack's very first Major progression.

## Dialect 2 — absolute symbols (pychord)

`render.py --symbols "Am7b9b5 G7-5 Cmaj7 Dsus4add9"` accepts the full pychord vocabulary, which
covers every suffix the numeral dialect rejects. Use it when:

- a progression needs a chord type numerals cannot spell, or
- the input came from a DAW/score as absolute chords.

Slash chords are sanitised for filenames by the engine (`C/E` → `C_E` in the name only).

## Useful conversions

```bash
python skills/music-theory/scripts/render.py --reverse "C Am F G"            # -> I vi IV V
python skills/music-theory/scripts/render.py --reverse "G Em C D" --key G    # -> I vi IV V
python skills/music-theory/scripts/render.py --numerals "I I IM-5 IM-5 IV IV V Vsus2" --key Bb --expand
# -> Bb D F / Bb D F / Bb D Fb / Bb D Fb / Eb G Bb / Eb G Bb / F A C / F G C
```

`--reverse` is how you check a hand-written progression against the pack's notation; `--expand`
is the readable form of what the engine will play (note the engine's own spelling: `M-5` yields
`Fb`, the enharmonic of `E`).

Two quirks of `--reverse` that come from the engine, not from the wrapper:

- It reads the symbols against a **major** scale. Without `--key` that is C (`G Em C D` →
  `V iii I II`); pass the uppercase root to read in that key (`--key G` → `I vi IV V`). A
  lowercase (minor) key raises inside mingus, and `render.py` reports that instead of a traceback.
- Its output is a reading aid, not always re-feedable input: minor-ish chords come back with the
  accidental as a *suffix* (`Am F C G --key A` → `i VIb IIIb VIIb`), and `VIb` is not a numeral
  the renderer accepts — the pack's dialect writes that chord as `bVIM`. Translate before feeding
  it back.

## Interpretation rules that must not be "corrected"

- Modal numerals are always relative to Ionian (README, and `chords.py`'s modal block). `im bVIIM
  bIIM ivm` is Dorian-flavoured material in a minor-ish context; rewriting `bVIIM` as `VII` changes
  the chord.
- `Cadence`-tagged progressions are the same modal dialect; the tag is a label, not a different grammar.
- The pack's `3 All chords` degree prefixes (`V-VII`) are documentation, not input syntax — feed the
  chord symbol (`G2`), not the prefix.

## Vocabulary drift

The lists above were derived by rendering `chords.py`'s declared types and every suffix used by the
shipped pack. If a future release adds a type, re-derive instead of guessing:

```bash
make index && python - <<'EOF'
import json, collections, sys, pathlib
sys.path.insert(0, "skills/music-theory/scripts")
from common import DEGREE_RE, find_index, repo_root
idx = json.loads(pathlib.Path(find_index(repo_root())).read_text(encoding="utf-8"))
sufs = collections.Counter(DEGREE_RE.match(t).group("suf") for e in idx["progressions"] for t in e["tokens"])
print(sorted(sufs))
EOF
```
