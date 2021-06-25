#!/usr/bin/env python3

# Copyright (c) 2019-2021 Ludovic Drolez

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import mingus.core.scales as scales

from src.chords2midi import c2m
from chords import *

# output dir
out = "output"

# Basic keys
keys = [
    ('C', 'A'),  # nothing
    #('C#', 'a#')  #  7 #
    ('Db', 'Bb'),  # 5 b
    ('D', 'B'),  # 2 #
    ('Eb', 'C'),  # 3 b
    ('E', 'C#'),  # 4 #
    ('F', 'D'),  # 1 b
    #('F#', 'd#'), #  6 #
    ('Gb', 'Eb'),  # 6 b
    ('G', 'E'),  # 1 #
    ('Ab', 'F'),  # 4 b
    ('A', 'F#'),  # 3 #
    ('Bb', 'G'),  # 2 b
    ('B', 'G#'),  # 5 #
    # ('Cb', 'ab'), #  7 b
]

deg_maj = ['I', 'ii', 'iii', 'IV', 'V', 'vi', 'vii']
deg_min = ['i', 'ii', 'III', 'iv', 'v', 'VI', 'VII']

#
# Generate a single chord
#
def gen(dir, key, chords, prefix):
    if not os.path.exists(dir):
        os.makedirs(dir)
    c2m_obj = c2m.Chords2Midi()
    c2m_obj.handle([f"{chords}", "-t", "5", "-p", "long", "-d", "4",
        "-B", "--key", f"{key}", "-N", f"{prefix} - {chords}", "--output", 
        f"{dir}/{prefix} - {chords}.mid"])

#
# Generate a chord progression
#
def genprog(dir, key, chords, prefix, style = ''):
    c2m_obj = c2m.Chords2Midi()
    args = chords.split(" ")
    if style != '':
        args.extend(["-p", style])
        dir = dir + "/" + style + " style"
    else:
        args.extend(["-d", "4", "-p", "long"])
    args.extend(["-t", "5", "-B",
        "--key", f"{key}", "-N", f"{prefix} - {chords}", "--output", 
        f"{dir}/{prefix} - {chords}.mid"])
    if not os.path.exists(dir):
        os.makedirs(dir)
    c2m_obj.handle(args)

num = 1
# Iterate for each key
for key in keys:

    root_maj = key[0]
    root_min = key[1]
    scale_maj = scales.Major(root_maj).ascending()
    scale_min = scales.NaturalMinor(root_min).ascending()
    base = f'{out}/{num:02} - {root_maj} Major - {root_min} minor'

    # Major triads
    i = 0
    for n in ['', 'm', 'm', '', '', 'm', 'dim']:
        chord = scale_maj[i] + n
        gen(f'{base}/1 Triad/Major', root_maj, chord, deg_maj[i])
        i = i + 1

    # Minor triads
    i = 0
    for n in ['m', 'dim', '', 'm', 'm', '', '']:
        chord = scale_min[i] + n
        gen(f'{base}/1 Triad/Minor', root_min, chord, deg_min[i])
        i = i + 1

    # Major 7th
    i = 0
    for n in [['M7', 'M9'], ['m7', 'm9'], ['m7', 'm9'],
              ['M7', 'M9'], ['7', '9'], ['m7', 'm9'],
              ['m7-5', 'm7b9b5']]:
        for c in n:
            chord = scale_maj[i] + c
            gen(f'{base}/2 7th and 9th/Major', root_maj, chord, deg_maj[i])
        i = i + 1

    # Minor 7th
    i = 0
    for n in [['m7', 'm9'], ['m7-5', 'm7b9b5'], ['M7', 'M9'], 
              ['m7', 'm9'], ['m7', 'm9'],
              ['M7', 'M9'], ['7', '9']]:
        for c in n:
            chord = scale_min[i] + c
            gen(f'{base}/2 7th and 9th/Minor', root_min, chord, deg_min[i])
        i = i + 1

    # All Other chords
    i = 0
    for c in [1, 2, 3, 4, 5, 6, 7]:
        for n in chord_types:
            chord = scale_maj[i] + n
            gen(f'{base}/3 All chords/', root_maj, chord, deg_maj[i] 
                + '-' + deg_min[(i+5) % 7])
        i = i + 1

    # Major progressions
    for style in [ '', 'basic4', 'alt4', 'hiphop' ]:
        for n in prog_maj:
            genprog(f'{base}/4 Progression/Major', root_maj, n, root_maj, style)

    # Minor progressions
    for style in [ '', 'basic4', 'alt4', 'hiphop' ]:
        for n in prog_min:
            genprog(f'{base}/4 Progression/Minor', root_min.lower(), n, root_min, style)

    # next key
    num = num + 1
