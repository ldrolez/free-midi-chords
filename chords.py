#!/usr/bin/env python3

# Copyright (c) 2019-2023 Ludovic Drolez

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

# Major progressions
prog_maj = [
    "I I IM-5 IM-5 IV IV V Vsus2",
    "I I IV iii",
    "I iii IV vi",
    "I iii vi Isus4",
    "I iii vi IV",
    "I IV ii V",
    "I IV Isus2 IV",
    "I IV V IV",
    "I IV V V",
    "I IV vi V",
    "I IV vii iii vi ii V I",
    "I V I IV",
    "I V IV vi",
    "I V vi ii",
    "I V vi iii IV I IV V", 
    "I V vi iii IV",
    "I V vi IV",
    "I V vi V",
    "I vi I IV", 
    "I vi ii IV", 
    "I vi ii V", 
    "I vi IV iii",
    "I vi IV V",
    "I7 V7 viadd9 IV7",
    "ii IV V V",
    "ii IV vi V",
    "ii V I I",
    "ii V I IV",
    "ii7 Vadd9 I7 I7",
    "iii vi IV I",
    "iim7 V7 iiim7 vi7 iim7 V7",
    "Isus2 I vi7 visus4",
    "IV I ii vi",
    "IV I iii IV",
    "IV I V vi",
    "IV IV I V",
    "IV vi I V",
    "IV vi iii I",
    "IV vi IV vi",
    "V I vi V",
    "V IV vi I",
    "V vi IV I",
    "vi ii V I",
    "vi IV I V",
    "vi V IV V ii V I I",
    "vi V IV V",
]

# minor progressions
prog_min = [
    "i i iv iv v7 ii5 v v7",
    "i ii v i",
    "i III iv VI",
    "i III VII VI",
    "i iim v III i iim v VII",
    "i iim v IVM",
    "i iv III VI",
    "i iv v iv",
    "i iv v v",
    "i iv VI v",
    "i iv VII i",
    "i iv VII v i i ii V",
    "i v iv VII",
    "i vdim iv VI",
    "i VI III VII i VI69 III7 VII",
    "i VI III VII",
    "i VI iv ii",
    "i VI iv III",
    "i VI iv v",
    "i VI VII iv",
    "i VI VII v",
    "i VI VII VII",
    "i VII i i VI v i",
    "i VII i v III VII i v i",
    "i VII i v",
    "i VII III VI",
    "i VII v VI",
    "i VII VI III iv VI VII i",
    "i VII VI III",
    "i VII VI iv ivsus4 iv",
    "i VII VI iv",
    "i VII VI VII",
    "i VM VII IVM VI III iv VM",
    "i7 VI III7 VII6 i i7 III7 iv7",
    "ii v i i",
    "ii v i iv",
    "ii VI i iv",
    "iim IVM v VII",
    "im7 ivsus4 v7 isus4",
    "iv i v VI",
    "iv i VIIm VI",
    "iv III iim7 VM",
    "iv III VII i",
    "iv III vsus4 VI iv i III VI",
    "iv v VI VII",
    "iv VI v VII",
    "iv VI VII i",
    "IVM v iim i III IVM",
    "v i iv VII",
    "v iv i i",
    "v VI III i",
    "v VI v i",
    "VI i v III",
    "VI i v v",
    "VI III i v",
    "VI iv i v",
    "VI VI i VII",
    "VI VII i III",
    "VI VII v III",
    "VI VIm i VII",
    "VII iv v i",
    "VII iv VII i",
]

# No. Mode
# 1   Ionian (major)  I   ii  iii   IV   V   vi  viio
# 2   Dorian          i   ii  ♭III  IV   v   vio ♭VII
# 3   Phrygian        i   ♭II ♭III  iv   vo  ♭VI ♭vii
# 4   Lydian          I   II  iii   ♯ivo V   vi  vii
# 5   Mixolydian      I   ii  iiio  IV   v   vi  ♭VII
# 6   Aeolian (n.min) i   iio ♭III  iv   v   ♭VI ♭VII
# 7   Locrian         io  ♭II ♭iii  iv   ♭V  ♭VI ♭vii
# Modal progressions
prog_modal = [
    "bIIIM ii bIIM I",
    "bIIM bVIM biii bviim",
    "bIIM ivm biii im",
    "bVIIM bIIM bIIIM im",
    "bVIM bVIIm im bIIM",
    "I bIIIM bVIIM IV",
    "I bIIIM bVIM bVIIM",
    "I bIIM I iii",
    "I bVIIM bVIM bIIM",
    "I bVIIM IV V", 
    "I bVIM I bIIM",
    "I IIM iii V6",
    "I IIM IV I",
    "I IV bIIIM bVIM", 
    "I IV bVIIM IV",
    "I IV V bVIIM",
    "I V bVIIM IV",
    "I5 iii II5 #IVm IV5 vi V5 viim",
    "ii bIIM I bVIIM",
    "ii bVIIM7 I", 
    "IIIM V VIsus4 VIM I IIM",
    "im bIIM bIIIM bIIM",
    "im bIIM ivm IIIM bIIM ivm IIIM IIIM",
    "im VIM bi V",
    "im VIM IIIM bIIM",
    "vdim vdim ivm bIIIM",
    "vi bVIM bVIIM I",
    "vi vii V vi #IVdim V",
    "VIM bVIM im bVIIM",

    # cadences
    "bIIIM V7 I",
    "bVIIM V7 I",
    "im bVIIM IV im",
    "ivm bIIIM bIIM I",
    "ivm IIIM bIIM I",
    "ivm bIIIM bVIM I",
]

# Chord Types
# with major third
chord_types_maj = [
    'sus2',  # 0, 2, 7
    'sus4',  # 0, 5, 7
    '6',  # 0, 4, 7, 9
    '7',  # 0, 4, 7, 10
    '7-5',  # 0, 4, 6, 10
    '7+5',  # 0, 4, 8, 10
    '7sus4',  # 0, 5, 7, 10
    'maj7',  # 0, 4, 7, 11
    'M7+5',  # 0, 4, 8, 11
    'add4',  # 0, 4, 5, 7
    'add9',  # 0, 4, 7, 14
    'sus4add9', # 0, 5, 7, 14
    '2',  # 0, 4, 7, 14
    'add11',  # 0, 4, 7, 17
    '69',  # 0, 4, 7, 9, 14
    '9',  # 0, 4, 7, 10, 14
    'maj9',  # 0, 4, 7, 11, 14
    '9sus4',  # 0, 5, 7, 10, 14
    '7-9',  # 0, 4, 7, 10, 13
    '7+11'  # 0, 4, 7, 10, 18
]

# with minor third
chord_types_min = [
    'sus2',  # 0, 2, 7
    'sus4',  # 0, 5, 7
    '7sus4',  # 0, 5, 7, 10
    'm6',  # 0, 3, 7, 9
    'm7',  # 0, 3, 7, 10
    'm7-5',  # 0, 3, 6, 10
    'm7+5',  # 0, 3, 8, 10
    'dim6',  # 0, 3, 6, 9
    'dim7', # 0, 3, 6, 9
    'mM7',  # 0, 3, 7, 11
    'madd4', # 0, 3, 5, 7
    'madd9',  # 0, 3, 7, 14
    'sus4add9', # 0, 5, 7, 14
    'm69',  # 0, 3, 7, 9, 14
    'm9',  # 0, 3, 7, 10, 14
    '9sus4',  # 0, 5, 7, 10, 14
    'm7b9b5', # 0, 3, 6, 10, 13
    'm7add11', # 0, 3, 7, 10, 17
    'mM7add11' # 0, 3, 7, 11, 17
]
