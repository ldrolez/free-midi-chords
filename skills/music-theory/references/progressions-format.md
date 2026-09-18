# Progressions format

Everything the pack knows about a progression is in its filename:

```
<KEY> - <NUMERALS>[ - <MOOD TAGS>].mid
Modal/A - bVIM7 ivmadd9 I - Spiritual Nostalgic.mid
```

Splitting rule: split on `" - "` (space-hyphen-space). Chord tokens contain hyphens themselves
(`IM-5`, `7-5`), so a bare `-` split corrupts them. The tag field is optional; 1 to 3 words, no
ordering rule, no schema.

## Tag vocabulary (v0.20260314)

23 words. Structural/recency markers are mixed in with moods:

| kind | words |
| --- | --- |
| moods | Mysterious, Nostalgic, Hopeful, Triumphant, Romantic, Rebellious, Joyful, Surprised, Sad, Dark, Tender, Playful, Spiritual, Relaxed, Peaceful, Empowered, Excited, Lonely, Fearful, Dramatic, Anguished |
| structural | Cadence (6 progressions) |
| recency | New (marks recent additions) |

Counts are per-file, not per-progression: each progression exists in 12 keys x 5 styles, so
"Hopeful 3180" means 265 progression-files per mode group. Use `find_progressions.py --vocab`
rather than reciting numbers from memory.

## Parsing without the index

`common.parse_entry(path)` returns the full record (`kind, key, mode, style, numerals, tokens,
tags, new, length, path`, plus `key_major`/`key_minor`/`number` for full-pack paths) and handles
both archive layouts. Do not hand-roll a regex: the pack's own top level (`01 - C Major - A minor`)
and its `N style` directories are easy to mis-slice.

## Known data wrinkles

- `im bVIIM IV im` is listed twice in `chords.py` (once in `prog_modal` as *New Nostalgic
  Mysterious*, once in the cadence block as *Cadence*), so **120 files** in the release are two
  names for the same 60 progressions, with identical note content. Reported upstream as
  [issue 46](https://github.com/ldrolez/free-midi-chords/issues/46); until it is fixed, dedupe by
  `(mode, key, style, numerals)` when counting.
- The progression set is key-independent within a mode: all 12 Major keys carry the same 50
  progressions, Minor 58, Modal 81 (82 entries with the duplicate above). Grouping by numerals is
  therefore safe when no key filter is given — that is what `find_progressions.py` does by default.
- Long progressions exist: chord counts run 3–9, with 4 and 8 the most common. Do not assume 4/4.
- Style copies differ only in timing; the numerals and tags are identical.
- Tags are sparse in combination: only **53 of the 210 possible tag pairs** co-occur anywhere in the
  pack (most common: hopeful+romantic 780 files, hopeful+nostalgic and mysterious+nostalgic 720 each).
  `dark`+`tender` never co-occur at all. An empty `--tags a,b` result is data, not a broken query —
  check `find_progressions.py --vocab` and relax to `--tags-any` before assuming a bug.
