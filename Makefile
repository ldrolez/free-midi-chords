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

.PHONY: check dist ripchord
