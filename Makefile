DATE=$(shell date +'%Y%m%d')

dist:
	rm -rf output/*
	# full pack
	python3 gen.py
	cp README.md LICENSE output
	rm -f dist/free-midi-chords-${DATE}.zip
	cd output; zip -r ../dist/free-midi-chords-${DATE}.zip *
	# make the progressions only pack
	mkdir output/progression
	cp -r output/*/4\ Progression output/progression
	cp README.md LICENSE output/progression/4\ Progression
	cd output/progression/4\ Progression; zip -r ../../../dist/free-midi-progressions-${DATE}.zip *

.PHONY: dist
