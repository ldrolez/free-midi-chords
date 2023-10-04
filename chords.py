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
    "Isus2 I vi7 visus4",
    "I I IM-5 IM-5 IV IV V Vsus2",
    "I I IV iii",
    "I bIIM I iii",
    "I bIIM bIIIM bIIM",
    "I IIM iii V6",
    "I IIM7 IV I",
    "I bIIIM bVIM bVIIM",
    "I bIIIM bVIIM IV",
    "I iii IV vi",
    "I iii vi Isus4",
    "I iii vi IV",
    "I5 iii II5 #IVm IV5 vi V5 viim",
    "I IV Isus2 IV",
    "I IV ii V",
    "I IV V IV",
    "I IV V V",
    "I IV V bVIIM",
    "I IV vi V",
    "I IV bIIIM bVIM", 
    "I IV bVIIM IV",
    "I V I IV",
    "I V IV vi",
    "I V vi ii",
    "I V vi IV",
    "I V vi iii IV",
    "I V vi V",
    "I V vi iii IV I IV V", 
    "I V bVIIM IV",
    "I IV vii iii vi ii V I",
    "I7 V7 viadd9 IV7",
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
    "ii IV vi V",
    "ii V I I",
    "ii V I IV",
    "ii bVIIM7 I", 
    "ii7 Vadd9 I7 I7",
    "iim7 V7 iiim7 vi7 iim7 V7",
    "bIIIM ii bIIM I",
    "iii vi IV I",
    "IIIM V VIsus4 VIM I IIM",
    "IV I ii vi",
    "IV I iii IV",
    "IV I V vi",
    "IV IV I V",
    "IV vi I V",
    "IV vi IV vi",
    "IV vi iii I",
    "V I vi V",
    "V IV vi I",
    "V vi IV I",
    "vi ii V I",
    "vi IV I V",
    "vi bVIM bVIIM I",
    "vi V IV V",
    "vi V IV V ii V I I",
    "vi vii V vi #IVdim V",
    # cadences
    "bIII V7 I",  
    "bVII V7 I"
]

# minor progressions
prog_min = [
    "i i iv iv v7 ii5 v v7",
    "i bIIM iv III bIIM iv III III",
    "i ii v i",
    "i iim v IVM",
    "i iim v III i iim v VII",
    "i III iv VI",
    "i III VII VI",
    "i iv v iv",
    "i iv v v",
    "i iv III VI",
    "i iv VI v",
    "i iv VII i",
    "i iv VII v i i ii V",
    "im7 ivsus4 v7 isus4",
    "i v iv VII",
    "i vdim iv VI",
    "i VM VII IVM VI III iv VM",
    "i VI bi v",
    "i VI III bii",
    "i VI III VII",
    "i VI III VII i VI69 III7 VII",
    "i VI iv ii",
    "i VI iv III",
    "i VI iv v",
    "i VI VII VII",
    "i VI VII v",
    "i bVIIM bVIM bVIIM",
    "i bVIIM VI bii",
    "i VII i v",
    "i VII i v III VII i v i",
    "i VII v VI",
    "i VII VI III",
    "i VII VI III iv VI VII i",
    "i VII VI VII",
    "i7 VI III7 VII6 i i7 III7 iv7",
    "ii v i i",
    "ii v i iv",
    "ii VI i iv",
    "iim IVM v VII",
    "bIIM iv III i",
    "bIIM VI III VIIm",
    "iv i v VI",
    "iv VI v VII",
    "iv VI VII i",
    "iv III vsus4 VI iv i III VI",
    "iv III VII i",
    "iv III iim7 VM",
    "iv v VI VII",
    "iv i VIIm VI",
    "IVM v iim i III IVM",
    "v i iv VII",
    "v iv i i",
    "v VI III i",
    "v VI v i",
    "vdim vdim iv III",
    "VI i v III",
    "VI i v v",
    "VI iv i v",
    "VI III i v",
    "VI bVI i VII",
    "VI VIm i VII",
    "VI VI i VII",
    "VI VII i III",
    "VI VII v III",
    "VI VIIm i bIIM",
    "VII iv VII i",
    "VII iv v i",
    "VIIm bIIM III i",
    # cadences
    "i VII VI VM",
    "i VII VI V7",
    "i viim VI VM",
    "i bVIIM bVIM iv"
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
