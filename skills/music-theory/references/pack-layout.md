# Pack layout

## Two release archives

| Archive | Contents |
| --- | --- |
| `free-midi-chords-YYYYMMDD.zip` | Everything: triads, 7ths/9ths, the full chord library, all progressions |
| `free-midi-progressions-YYYYMMDD.zip` | Only the progressions, flattened into `Major/ Minor/ Modal/` for MPC/Roland import |

Releases are cut roughly twice a year and tagged `v0.YYYYMMDD` (e.g. `v0.20260314`, Spring 2026).
The release assets also carry a generated `free-midi-progressions-YYYYMMDD.json` index
(`make index`), with a full `sha256` per file so downstream consumers can pin the exact
pack they reasoned about.

## The four levels

```
01 - C Major - A minor/
├── 1 Triad/{Major,Minor}/            <degree> - <chord symbol>.mid
├── 2 7th and 9th/{Major,Minor}/      <degree> - <chord symbol>.mid
├── 3 All chords/                     <degree>-<parallel degree> - <chord symbol>.mid
└── 4 Progression/{Major,Minor,Modal}[/<style> style]/
                                      <KEY> - <numerals>[ - <MOOD TAGS>].mid
```

The progressions-only archive omits the numbered top level and starts at `Major/ Minor/ Modal/`.

## Things that surprise people

- **`output/` is not always a clean pack.** `make dist` copies `*/4 Progression` into
  `output/progression/` to cut the progressions archive, and leaves it there, so the tree then
  holds each progression twice (13,536 files under `NN - Key Major - key minor/`, plus the 11,400
  staging copies). Indexing a `dist/` archive - the default - avoids this; if you do index the
  tree, delete `output/progression` first or expect 22,800 progression entries.
- **The key directory names are not the render keys.** `01 - C Major - A minor` means C major and
  its *relative* minor, A minor. `gen.py` builds the pair from `keys = [('C','A'), ('Db','Bb'), …]`
  and renders major content with `root_maj` and minor content with `root_min.lower()`. The pack's
  minor folders spell sharp keys as `C#`, `F#`, `G#`; the renderer must receive `c#`, `f#`, `g#`.
- **Only 12 of the possible 15 spellings ship.** `C#`/`F#`/`G#` exist as minor keys while `Db`/`Gb`
  exist as major keys; `Cb`, `Fb` and the other seven-accidental keys are absent. Treat key
  spelling as pack data, not as something to derive — `find_progressions.py` matches enharmonics.
- **Rhythm styles are sibling directories**, not files: `pop style/`, `pop2 style/`, `soul style/`,
  `hiphop2 style/` next to the plain files in each mode folder. `gen.py`'s `styles` list is
  `['', 'pop', 'pop2', 'hiphop2', 'soul']`; `''` is the plain set.
- **"3 All chords" prefixes encode two degrees** — `<major-key degree>-<parallel-minor degree>`,
  e.g. `V-VII - G2.mid`: G is degree V of C major and degree VII of A natural minor.
- **File counts change without a format change**: progressions grow release over release
  (v0.20260314 has 50 Major / 58 Minor / 81 Modal per key). Never hard-code counts; read them
  from the index (`find_progressions.py --vocab` or `index.counts`).

## Release-relative noise

`New` appears in 840 filenames as a tag word (168 per mode group) and marks progressions added in
recent releases. It is not a mood and it is never removed, so filter it out of mood queries
(`--no-new`) unless you specifically want recently added material.
