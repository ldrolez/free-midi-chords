DATE=$(shell date +'%Y%m%d')

dist:
	rm -rf output/*
	python3 gen.py
	cp README.md LICENSE output
	rm -f dist/free-midi-chords-${DATE}.zip
	cd output; zip -r ../dist/free-midi-chords-${DATE}.zip *
	# make the progressions only pack
	mkdir output/progression
	cp -rv output/*/4\ Progression output/progression
	mv output/progression/4\ Progression/* output/progression/
	rmdir output/progression/4\ Progression/
	cp README.md LICENSE output/progression
	cd output/progression; zip -r ../../dist/free-midi-progressions-${DATE}.zip *

.PHONY: dist
