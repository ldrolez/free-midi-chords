#!/usr/bin/env python3

# Copyright (c) 2019-2025 Ludovic Drolez

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
    "I I IM-5 IM-5 IV IV V Vsus2 =Joyful Triumphant",
    "I I IV iii =Hopeful Nostalgic",
    "I I7 Idom7 I7 =Relaxed Playful",
    "I I7 Idom7 IV =Relaxed Nostalgic",
    "I iii IV vi =Romantic Nostalgic",
    "I iii vi Isus4 =Tender Spiritual",
    "I iii vi IV =Romantic Hopeful",
    "I IV ii V =Joyful Triumphant",
    "I IV Isus2 IV =Peaceful Hopeful",
    "I IV V IV =Joyful Triumphant",
    "I IV V V =Joyful Excited",
    "I IV vi V =Joyful Hopeful",
    "I IV vii iii vi ii V I =Romantic Triumphant",
    "I V I IV =Joyful Playful",
    "I V IV vi =Romantic Hopeful",
    "I V vi ii =Hopeful Romantic",
    "I V vi iii IV I IV V =Hopeful Joyful",
    "I V vi iii IV =Hopeful Joyful",
    "I V vi IV =Hopeful Romantic",
    "I V vi V =Hopeful Romantic",
    "I vi I IV =Tender Nostalgic",
    "I vi ii IV =Tender Nostalgic",
    "I vi ii V =Nostalgic Romantic",
    "I vi IV iii =Nostalgic Romantic",
    "I vi IV V =Romantic Hopeful",
    "I7 V7 viadd9 IV7 =Playful Joyful",
    "ii IV V V =Hopeful",
    "ii IV vi V =Romantic",
    "ii V I I =Triumphant",
    "ii V I IV =Hopeful Triumphant",
    "ii7 Vadd9 I7 I7 =Triumphant",
    "iii vi IV I =Romantic Nostalgic",
    "iim7 V7 iiim7 vi7 iim7 V7 =Romantic Nostalgic",
    "Isus2 I vi7 visus4 =Playful Romantic",
    "IV I ii vi =Nostalgic Peaceful",
    "IV I iii IV =Playful Joyful",
    "IV I IV6 Iadd9 =Relaxed Joyful",
    "IV I V vi =Joyful Romantic",
    "IV IV I V =Joyful Hopeful",
    "IV vi I V =Hopeful Romantic",
    "IV vi iii I =Nostalgic Playful",
    "IV vi IV vi =Nostalgic",
    "V I vi V =Hopeful Romantic",
    "V IV vi I =Hopeful Triumphant",
    "V vi IV I =Hopeful Romantic",
    "vi ii V I =Hopeful Romantic",
    "vi IV I V =Hopeful Romantic",
    "vi V IV V ii V I I =Triumphant Hopeful",
    "vi V IV V =Romantic Hopeful",
]

# minor progressions
prog_min = [
    "i i iv iv v7 ii5 v v7 =Dark Mysterious",
    "i ii v i =Mysterious Triumphant",
    "i III iv VI =Nostalgic Romantic",
    "i III VII VI =Nostalgic Romantic",
    "i ii v III i ii v VII =Mysterious Dramatic",
    "i iv III VI =Nostalgic Romantic",
    "i iv v iv =Mysterious Sad",
    "i iv v v =Sad Lonely",
    "i iv VI v =Sad Hopeful",
    "i iv VII i =Sad Nostalgic",
    "i iv VII v i i ii V =Mysterious Surprised",
    "i v iv VII =Sad Rebellious",
    "i vdim iv VI =Dark Nostalgic",
    "i VI III VII i VI69 III7 VII =Mysterious Spiritual",
    "i VI III VII =Nostalgic Hopeful",
    "i VI iv ii =Sad Tender",
    "i VI iv III =Sad Nostalgic",
    "i VI iv v =Sad Hopeful",
    "i VI VII iv =Mysterious Nostalgic",
    "i VI VII v =Mysterious Rebellious",
    "i VI VII VII =Triumphant Rebellious",
    "i VII i v III VII i v i =Mysterious Surprised",
    "i VII i v =Mysterious Nostalgic",
    "i VII III VI =Rebellious Triumphant",
    "i VII v VI =Mysterious Hopeful",
    "i VII VI III iv VI VII i =Mysterious Surprised",
    "i VII VI III =Nostalgic Hopeful",
    "i VII VI iv =Sad Romantic",
    "i VII VI VII =Rebellious Triumphant",
    "i7 VI III7 VII6 i i7 III7 iv7 =Dark Nostalgic",
    "ii v i i =Peaceful Hopeful",
    "ii v i iv =Peaceful Nostalgic",
    "ii VI i iv =Sad Hopeful",
    "im7 ivsus4 v7 isus4 =Mysterious Tender",
    "iv i v VI =Nostalgic Hopeful",
    "iv III VII i =Nostalgic Mysterious",
    "iv III vsus4 VI iv i III VI =Nostalgic Mysterious",
    "iv v VI VII =Mysterious Rebellious",
    "iv VI v VII =Mysterious Hopeful",
    "iv VI VII i =Triumphant",
    "v i iv VII =Dark Rebellious",
    "v iv i i =Lonely",
    "v VI III i =Hopeful Nostalgic",
    "v VI v i =Sad",
    "VI i v III =Hopeful Nostalgic",
    "VI i v v =Sad",
    "VI III i v =Nostalgic Dark",
    "VI iv i v =Hopeful Tender",
    "VI VI i VII =Empowered",
    "VI VII i III =Triumphant Nostalgic",
    "VI VII v III =Rebellious Nostalgic",
    "VII iv v i =Mysterious Dark",
    "VII iv VII i =Spiritual",
]

# Major and minor suffixes often need to be added to get the right chord with Mingus
# No. Mode
# 1   Ionian (major)  I    ii    iii    IV   V     vi    viidim
# 2   Dorian          im   ii    bIIIM  IV   vm    vidim bVIIM
# 3   Phrygian        im   bIIM  bIIIM  ivm  vdim  bVIM  bviim
# 4   Lydian          I    IIM   iii   #IVdim V     vi   viim
# 5   Mixolydian      I    ii    iiidim IV   vm    vi    bVIIM
# 6   Aeolian (n.min) im   iidim bIIIM  ivm  vm    bVIM  bVIIM
# 7   Locrian         idim  bIIM biii   ivm  bV    bVIM  bviim

# Modal progressions
prog_modal = [
    "bIIIM ii bIIM I =Mysterious Surprised",
    "bIIM bVIM biii bviim =Mysterious Surprised",
    "bIIM ivm biii im =Mysterious Dark",
    "bVIIM bIIM bIIIM im =Mysterious Rebellious",
    "bVIM bIIIM bVIIM IV I =Triumphant Mysterious",
    "bVIM bVIIm im bIIM =Mysterious Dark",
    "bVIM vi im bVIIM =Hopeful Mysterious",
    "bVIM7 ivmadd9 I I =Spiritual Nostalgic",
    "I bIIIM bVIIM I =Triumphant Rebellious",
    "I bIIIM bVIIM IV =Triumphant Mysterious",
    "I bIIIM bVIM bVIIM =Triumphant Hopeful",
    "I bIIIM IV I =Romantic",
    "I bIIM I iii =Surprised Mysterious",
    "I bIIM7 bIIIM6 bIIM7 I im bVIIM bIIM =Surprised Mysterious",
    "I bVIIM bVIM bIIM =Triumphant Rebellious",
    "I bVIIM bVIM IV IVsus4 IV =Hopeful Nostalgic",
    "I bVIIM I I bVIM V =Triumphant Hopeful",
    "I bVIIM IV V =Joyful Triumphant",
    "I bVIM I bIIM =Surprised Mysterious",
    "I bVIM IV bIIIM bVIIM =Mysterious Nostalgic",
    "I I7 Idom7 IV ivm I =Relaxed Nostalgic",
    "I IIIM vi V =Joyful Hopeful",
    "I IIM iii V6 =Surprised Triumphant",
    "I IIM IV I =Joyful Triumphant",
    "I IV bIIIM bVIM =Nostalgic Mysterious",
    "I IV bVIIM IV =Joyful Rebellious",
    "I IV V bVIIM =Triumphant Rebellious",
    "I ivm bIIIM bVIIM =Mysterious Nostalgic",
    "I V bVIIM IV =Triumphant Rebellious",
    "I V ivm bVIM =Surprised Mysterious",
    "I5 iii II5 #IVm IV5 vi V5 viim =Excited Triumphant",
    "ii bIIM I bVIIM =Mysterious Rebellious",
    "ii bVIIM7 I =Hopeful Triumphant",
    "ii IVM vm bVIIM =Mysterious Nostalgic",
    "IIIM V VIsus4 VIM I IIM =Triumphant Surprised",
    "im bIIIM bVIIM IV =Romantic Nostalgic",
    "im bIIIM bVIM V =Mysterious Triumphant",
    "im bIIIM IV bVIM =Mysterious Hopeful",
    "im bIIIsus2 IV IV =Mysterious Peaceful",
    "im bIIM bIIIM bIIM =Mysterious Dark",
    "im bIIM biim6 ivm =Mysterious Tender",
    "im bIIM im7 bviim =Mysterious Spiritual",
    "im bIIM ivm IIIM bIIM ivm IIIM IIIM =Mysterious Nostalgic",
    "im bIIM vm im7 =Mysterious Dark",
    "im bVIIM bIIM vm =Mysterious Rebellious",
    "im bviim bVIM bIIM =Mysterious Hopeful",
    "im bVIM ivm V =Triumphant",
    "im ii vm IV =Nostalgic Hopeful",
    "im ivm9 bIIM im vm ivm7 bIIM im7 =Mysterious Tender",
    "im ivm9 bIIM im =Mysterious Nostalgic",
    "im V bVIIM IV bVIM bIIIM ivm V =Mysterious Rebellious",
    "im VIM bi V =Mysterious Triumphant",
    "im VIM IIIM bIIM =Nostalgic Surprised",
    "im vm bVIM bIIM =Mysterious Hopeful",
    "im vm ivm bIIM7 =Mysterious Dark",
    "IV V ii im bIIIM IV =Hopeful Nostalgic",
    "ivm bIIIM iim7 V =Mysterious Tender",
    "ivm im bviim bVIM =Dark",
    "vdim vdim ivm bIIIM =Fearful Mysterious",
    "vi bVIM bVIIM I =Hopeful Triumphant",
    "vi viim V vi #IVdim V =Nostalgic Dark",
    "VIM bVIM im bVIIM =Surprised Rebellious",

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
