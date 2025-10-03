# c2m-patterns.py - chords2midi

####################################################################
# Data
####################################################################

# N: Next
# S: Same
# X: Rest
# Duration in beats before letter
# ex: 2N X N .5S .5S

# TODO:
# +Z: Move Z Intervals Up
# +Z: Move Z Intervals Down

N = 'N'
X = 'X'
S = 'S'

patterns = {
    'long': ['4N'],
    'basic': [N, X],
    'basic2': [N, X, S, X],
    'basic4': ['0.5N', '0.5X', '0.5S', '0.5X', '0.5S', '0.5X', '0.5S', '0.5X'],
    'alt': [X, N],
    'alt2': [X, N, X, S],
    'alt3': [X, N, X, S, X, S, X, S],
    'hiphop': ['N', '2X', 'N', 'X', 'N', 'X', 'N'],
    'hiphop2': [ '1N', '0.75X', '2.25S', '0.75X', '1.25N', '2S' ],
    'hiphop3': [ '0.5X', '1N', '0.5X', '1S', '1X', '0.5S', '0.5N', '3S' ],
    'pop': [ '1.5N', '2.5N', '1.5N', '2.5N'],
    'pop2': [ '1.75N', '2.25N', '1.75N', '2.25N'],
    'soul': [ 'N', 'S', '1.5N', '2N', '2.5N' ],
    'soul2': ['2N', '0.5X', '0.85S', '0.7S', '1.45N', '0.5S', '0.5X', '0.8S', '0.7S'],
}

