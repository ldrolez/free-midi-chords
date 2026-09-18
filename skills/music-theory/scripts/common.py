"""Shared helpers: repo discovery, pack sources, filename grammar, numeral vocabulary.

The pack's metadata lives only in filenames, so this module is the single place that
knows the grammar. Everything else in this skill imports from here.

Verified against free-midi-chords release v0.20260314 + the ldrolez/python-mingus fork.
"""

from __future__ import annotations

import collections
import datetime
import os
import re
import sys
import zipfile
from pathlib import Path

REPO_ENV = "FREE_MIDI_CHORDS_REPO"
PACK_ENV = "FREE_MIDI_CHORDS_PACK"

MODES = ("major", "minor", "modal")
# Rhythm variants the pack ships as subdirectories ("plain" = no subdirectory).
PACK_STYLES = ("plain", "pop", "pop2", "soul", "hiphop2")

# Numeral quality suffixes the repo's engine accepts, per degree, with the fork installed.
# Derived two ways: enumerating chords.py's chord_types_* against I / i / V / VII, and
# verifying every suffix the shipped pack actually uses (which adds M-5 and M6 - stock
# mingus rejects M-5, so it must be listed here or the first Major progression is refused).
SUPPORTED_SUFFIXES = (
    "", "m", "M", "dim", "dim7", "m7", "M7", "m9", "M9", "9", "6", "69", "m6", "M6",
    "7", "sus2", "sus4", "add9", "madd9", "mM7", "M7+5", "M-5", "dom7", "5",
)
# Chord types that exist in chords.py (and ship inside "3 All chords" as absolute
# symbols) but raise KeyError when written as a numeral. Route these through
# render.py --symbols instead.
UNSUPPORTED_SUFFIXES = (
    "2", "5sus4", "m69", "7sus4", "add4", "madd4", "add11", "dim6", "7-5", "7+5",
    "m7-5", "m7+5", "7-9", "7+11", "sus4add9", "9sus4", "m7b9b5", "m7add11", "mM7add11",
)

DEGREE_RE = re.compile(r"^(?P<acc>[b#]*)(?P<deg>[ivIV]+)(?P<suf>.*)$")
CHORD_LETTER_RE = re.compile(r"^[A-G][#b]?")
ENHARMONIC = {"C#": "Db", "Db": "C#", "F#": "Gb", "Gb": "F#", "G#": "Ab", "Ab": "G#"}

_PROG_ONLY = re.compile(r"^(Major|Minor|Modal)(?:/([a-z0-9]+) style)?/(.+)$")
_TOP_DIR = re.compile(r"^(\d+) - ([A-G][#b]?) Major - ([A-G][#b]?) minor$")
_CATEGORY = re.compile(r"^\d ")
_STYLE_DIR = re.compile(r"^([a-z0-9]+) style$")


def repo_root(explicit: str | None = None) -> Path:
    """Locate the free-midi-chords checkout (flag, env var, or this script's own parents)."""
    for cand in (explicit, os.environ.get(REPO_ENV)):
        if cand and (Path(cand) / "gen.py").is_file():
            return Path(cand).resolve()
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / "gen.py").is_file():
            return parent
    raise SystemExit(
        "free-midi-chords checkout not found.\n"
        "  git clone https://github.com/ldrolez/free-midi-chords.git\n"
        f"  or set {REPO_ENV}=<path to the clone>"
    )


def use_toolchain(repo: Path) -> None:
    """Put the repo and its required python-mingus fork ahead of site-packages.

    Stock `pip install mingus` cannot render shipped progressions such as
    'I I IM-5 IM-5 IV IV V Vsus2' (KeyError: 'M-5') - the fork is mandatory.
    """
    fork = Path(repo) / "python-mingus"
    if not (fork / "mingus").is_dir():
        raise SystemExit(
            f"required python-mingus fork missing: {fork}\n"
            "  git clone https://github.com/ldrolez/python-mingus.git python-mingus"
        )
    for path in (str(fork), str(repo)):
        while path in sys.path:
            sys.path.remove(path)
        sys.path.insert(0, path)


def load_c2m(repo: Path):
    """Import the repo's own chords2midi engine (never a reimplementation)."""
    use_toolchain(repo)
    from src.chords2midi import c2m  # noqa: E402  (path set up above)

    return c2m


class Source:
    """The MIDI files to index or verify: a release `.zip`, or a built pack directory.

    Addresses every file by its pack-relative POSIX path, so a freshly built
    `output/` tree and the `.zip` cut from it are interchangeable inputs.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._zip: zipfile.ZipFile | None = None
        if self.path.is_dir():
            self.root: Path | None = self.path
        elif self.path.is_file() and zipfile.is_zipfile(self.path):
            self.root = None
            self._zip = zipfile.ZipFile(self.path)
        else:
            raise SystemExit(f"not a pack archive or directory: {self.path}")

    def names(self) -> list[str]:
        if self._zip is not None:
            return [n for n in self._zip.namelist() if n.lower().endswith(".mid")]
        return sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob("*.mid"))

    def read(self, name: str) -> bytes:
        if self._zip is not None:
            return self._zip.read(name)
        return (self.root / name).read_bytes()

    def close(self) -> None:
        if self._zip is not None:
            self._zip.close()
            self._zip = None

    def __enter__(self) -> "Source":
        return self

    def __exit__(self, *exc) -> None:
        self.close()


def pack_mtime(path: Path) -> float:
    """Newest .mid timestamp in a pack archive or tree (used to pick the freshest source)."""
    if path.is_file():
        return path.stat().st_mtime
    newest = 0.0
    for entry in path.rglob("*.mid"):
        try:
            newest = max(newest, entry.stat().st_mtime)
        except OSError:
            pass
    return newest


def find_source(repo: Path, explicit: str | None = None) -> Path:
    """Pick the pack to work on: the flag, the env var, else the freshest one at hand.

    Candidates are the archives in `dist/` (what `make dist` cuts), the `output/` tree it
    cuts them from, and a downloaded release dropped in `packs/`. Whichever was built or
    downloaded most recently wins, so `make dist && make index` indexes what was just built
    and a consumer with only a release archive gets that.
    """
    for cand, origin in ((explicit, "--pack"), (os.environ.get(PACK_ENV), PACK_ENV)):
        if cand:
            path = Path(cand)
            if not path.exists():
                raise SystemExit(f"{origin}: no such path: {path}")
            return path
    candidates: list[Path] = []
    for directory in ("dist", "packs"):
        candidates += sorted((Path(repo) / directory).glob("free-midi-*.zip"))
    output = Path(repo) / "output"
    if output.is_dir() and any(output.rglob("*.mid")):
        candidates.append(output)
    if not candidates:
        raise SystemExit(
            "no pack to index - run `make dist` first, or point\n"
            f"  --pack / {PACK_ENV} at a release .zip or a built pack directory"
        )
    return max(candidates, key=pack_mtime)


def datetime_from_name(name: str) -> str:
    m = re.search(r"free-midi-(?:chords|progressions)-(\d{8})", Path(name).name)
    return m.group(1) if m else datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d")


def version_from_name(name: str) -> str:
    return f"v0.{datetime_from_name(name)}"


def parse_entry(name: str) -> dict | None:
    """Parse one pack-relative path into an index entry (progression or chord-library file)."""
    parts = name.split("/")
    base = parts[-1]
    if not base.lower().endswith(".mid"):
        return None
    dirs = parts[:-1]
    category = next((d for d in dirs if _CATEGORY.match(d)), None)
    mode_dir = next((d for d in dirs if d in ("Major", "Minor", "Modal")), None)
    style = next((m.group(1) for d in dirs if (m := _STYLE_DIR.match(d))), "plain")
    top = next((d for d in dirs if _TOP_DIR.match(d)), None)
    keys = {}
    if top:
        m = _TOP_DIR.match(top)
        keys = {"key_major": m.group(2), "key_minor": m.group(3), "number": int(m.group(1))}

    # Progressions-only pack: "Major/…" at top level. Full pack: "…/4 Progression/<mode>/…".
    is_progression = category == "4 Progression" or (category is None and mode_dir is not None)
    chunks = base[:-4].split(" - ")

    if is_progression:
        numerals = chunks[1] if len(chunks) > 1 else ""
        tags = chunks[2].split() if len(chunks) > 2 else []
        return {
            "kind": "progression",
            "key": chunks[0],
            "mode": (mode_dir or "").lower(),
            "style": style,
            "numerals": numerals,
            "tokens": numerals.split(),
            "tags": sorted(t.lower() for t in tags),
            "new": any(t.lower() == "new" for t in tags),
            "length": len(numerals.split()),
            "path": name,
            **keys,
        }

    scale = next((d for d in dirs if d in ("Major", "Minor") and d != mode_dir), None)
    return {
        "kind": "chord",
        "category": category,
        "scale": scale,
        "label": chunks[0],
        "symbol": chunks[1] if len(chunks) > 1 else "",
        "path": name,
        **keys,
    }


def tag_vocabulary(entries) -> dict:
    counts = collections.Counter(t for e in entries for t in e.get("tags", ()))
    return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))


def validate_tokens(tokens) -> list[tuple[str, str]]:
    """Return [(token, reason)] for tokens the repo engine cannot render as numerals."""
    bad = []
    for token in tokens:
        if token == "X":
            continue
        m = DEGREE_RE.match(token)
        if not m or not m.group("deg"):
            hint = "absolute chord symbol" if CHORD_LETTER_RE.match(token) else "not a numeral"
            bad.append((token, f"{hint} - use render.py --symbols for that"))
        elif m.group("suf") and m.group("suf") not in SUPPORTED_SUFFIXES:
            bad.append((token, f"unsupported numeral suffix {m.group('suf')!r}"))
    return bad


def find_index(repo: Path, explicit: str | None = None) -> Path:
    """Locate a generated index: the flag, then the newest in `dist/` (written by
    `make index`), then the newest in `index/` (a locally kept copy)."""
    if explicit:
        return Path(explicit)
    for directory in ("dist", "index"):
        candidates = sorted((Path(repo) / directory).glob("free-midi-*.json"),
                            key=lambda p: p.stat().st_mtime)
        if candidates:
            return candidates[-1]
    raise SystemExit(
        "no index found - run `make index` (or skills/music-theory/scripts/build_index.py) first"
    )