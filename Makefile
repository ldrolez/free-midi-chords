DATE=$(shell date +'%Y%m%d')

dist:
	rm -rf output/*
	python3 gen.py
	cp README.md LICENSE output
	rm -f ../dist/free-midi-chords-${DATE}.zip
	cd output; zip -r ../dist/free-midi-chords-${DATE}.zip *

.PHONY: dist
