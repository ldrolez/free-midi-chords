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

# Major progressions
prog_maj = [
    "I bIIM I iii",
    "I bIIM bIIIM bIIM",
    "I IIM iii V6",
    "I bIIIM bVIM bVIIM",
    "I bIIIM bVIIM IV",
    "I iii IV vi",
    "I iii vi Isus4",
    "I iii vi IV",
    "I IV Isus2 IV",
    "I IV ii V",
    "I IV vi V",
    "I IV V V",
    "I IV V bVIIM",
    "I IV bIIIM bVIM", 
    "I IV bVIIM IV",
    "I V I IV",
    "I V vi ii",
    "I V vi IV",
    "I V vi iii IV",
    "I V vi V",
    "I V vi iii IV I IV V", 
    "I V bVIIM IV",
    "I bVIM I bIIM",
    "I vi I IV", 
    "I vi ii IV", 
    "I vi ii V", 
    "I vi IV iii",
    "I vi IV V",
    "I bVIIM bVIM bIIM",
    "I bVIIM IV I", 
    "ii bIIM I bVIIM",
    "ii IV V V",
    "ii V I I",
    "ii V I IV",
    "ii bVIIM7 I", "ii7 V9 I7 I7",
    "iim7 V7 iiim7 vi7 iim7 V7",
    "bIIIM ii bIIM I",
    "iii vi IV I",
    "IV I ii vi",
    "IV I iii IV",
    "IV I V vi",
    "IV IV I V",
    "V I vi V",
    "V IV vi I",
    "V vi IV I",
    "vi IV I V",
    "vi bVIM bVIIM I",
    "vi V IV V",
]

# minor progressions
prog_min = [
    "i ii v i",
    "i III iv VI",
    "i iv v iv",
    "i iv v v",
    "i iv III VI",
    "i iv VI v",
    "i iv VII i",
    "i iv VII v i i ii V",
    "i v iv VII",
    "i VI bi v",
    "i VI III bii",
    "i VI III VII",
    "i VI III VII i VI69 III7 VII",
    "i VI iv ii",
    "i VI iv v",
    "i VI VII VII",
    "i VI VII v",
    "i bVIIM bVIM bVIIM",
    "i bVIIM VI bii",
    "i VII i v",
    "i VII i v III VII i v i",
    "i VII VI III",
    "i VII VI VII",
    "i7 VI III7 VII6 i i7 III7 iv7",
    "ii v i i",
    "ii v i iv",
    "ii VI i iv",
    "ii7 v9 i7",
    "iv i v VI",
    "iv VI VII i",
    "iv III VII i",
    "iv v VI VII",
    "v i iv VII",
    "v iv i i",
    "v VI III i",
    "v VI v i",
    "VI i v v",
    "VI iv i v",
    "VI bVI i VII",
    "VI VIm i VII",
    "VI VI i VII",
    "VI VII i III",
    "VI VII v III",
    "VII iv VII i",
    "VII iv v i",
]

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
        for n in [
            'sus2',  # 0, 2, 7
            'sus4',  # 0, 5, 7
            '6',  # 0, 4, 7, 9
            '7',  # 0, 4, 7, 10
            '7-5',  # 0, 4, 6, 10
            '7+5',  # 0, 4, 8, 10
            '7sus4',  # 0, 5, 7, 10
            'm6',  # 0, 3, 7, 9
            'm7',  # 0, 3, 7, 10
            'm7-5',  # 0, 3, 6, 10
            'dim6',  # 0, 3, 6, 9
            'maj7',  # 0, 4, 7, 11
            'M7+5',  # 0, 4, 8, 11
            'mM7',  # 0, 3, 7, 11
            'add9',  # 0, 4, 7, 14
            'madd9',  # 0, 3, 7, 14
            '2',  # 0, 4, 7, 14
            'add11',  # 0, 4, 7, 17
            'm69',  # 0, 3, 7, 9, 14
            '69',  # 0, 4, 7, 9, 14
            '9',  # 0, 4, 7, 10, 14
            'm9',  # 0, 3, 7, 10, 14
            'maj9',  # 0, 4, 7, 11, 14
            '9sus4',  # 0, 5, 7, 10, 14
            '7-9',  # 0, 4, 7, 10, 13
            '7+11',  # 0, 4, 7, 10, 18
        ]:
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
