# Licensing and attribution

- The MIDI pack is MIT: "All the MIDI files are licensed under the MIT license, and you can use them
  in any musical project freely." The repository code (including `src/chords2midi`, which carries
  Rich Jones' original work, and `gen-ripchord.py`, copyright its contributor) is MIT as well.
- Anything this skill generates is derived data from an MIT source, so the same permission carries
  over — including an index file redistributed alongside the pack. Keep the upstream notice
  (`LICENSE`, and the author's attribution in the README) with any redistributed copy.
- `src/chords2midi/c2mpatterns.py` and the fork (`ldrolez/python-mingus`) are bundled because the
  generator depends on them; do not ship them without their own notices.
- Generated MIDI belongs to whoever composed the progression with it, but the *pack's* files
  themselves stay credited to the pack. When a composition reuses a shipped progression verbatim,
  note which pack version and path it came from — the index records both (`version`, `path`,
  `sha256`).
- Attribution wording that stays accurate:

```text
Chord progressions and chord voicings from the SHLD Free MIDI Chord Packs
(https://github.com/ldrolez/free-midi-chords), MIT.
```

Do not describe the pack as "public domain", and do not present a re-render as a new pack.
