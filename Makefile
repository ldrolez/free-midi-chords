DATE=$(shell date +'%Y%m%d')

# Chords distribution
dist: check
	rm -rf output/*
	# full pack
	env PYTHONPATH=python-mingus/ python3 gen.py
	cp README.md LICENSE output
	rm -f dist/free-midi-chords-${DATE}.zip
	cd output; zip -r ../dist/free-midi-chords-${DATE}.zip *
	# make the progressions only pack
	mkdir output/progression
	cp -r output/*/4\ Progression output/progression
	cp README.md LICENSE output/progression/4\ Progression
	cd output/progression/4\ Progression; zip -r ../../../dist/free-midi-progressions-${DATE}.zip *

ripchord:
	python3 gen-ripchord.py
	cd output/ripchord/; zip -r ../../dist/free-ripchord-progressions-${DATE}.zip *

# Check for GIT version of python-mingus
check:
	@test -f ./python-mingus/README.md || { echo "To build the pack you will need the modified python-mingus library:\n git clone https://github.com/ldrolez/python-mingus.git" ; exit 1; }

# Machine readable index of the built pack (release asset: dist/free-midi-progressions-${DATE}.json).
# Run after 'make dist'; indexes the newest archive in dist/, or output/ when there is none.
# --shards also writes dist/free-midi-progressions-${DATE}/: a manifest plus one file per key and
# mode, so a consumer (or an agent) reads only the slice a query needs instead of the whole index.
index:
	env PYTHONPATH=python-mingus/ python3 skills/music-theory/scripts/build_index.py --read-midi --jsonl --shards

.PHONY: check dist ripchord index
