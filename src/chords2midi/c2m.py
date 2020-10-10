# c2m.py - chords2midi

import argparse
import errno
import os
import pychord
import time
import traceback

from midiutil import MIDIFile
from mingus.core.progressions import to_chords, determine
import mingus.core.notes as notes

####################################################################
# Data
####################################################################

# N: Next
# S: Same
# X: Rest

# TODO:
# +Z: Move Z Intervals Up
# +Z: Move Z Intervals Down

# TODO:
# Include duration in inputs
# ex: 2N X N .5S .5S

N = 'N'
X = 'X'
S = 'S'
patterns = {
    'long': [N, X, X, X],
    'basic': [N, X],
    'basic2': [N, X, S, X,],
    'basic4': [N, X, S, X, S, X, S, X],
    'alt': [X, N],
    'alt2': [X, N, X, S],
    'alt4': [X, N, X, S, X, S, X, S],
    'hiphop': [N, X, X, N, X, N, X, N]
}

####################################################################
# Main
####################################################################

class Chords2Midi(object):
    """
    Read CLI input, create MIDI files.

    """

    def handle(self, argv=None):
        """
        Main function.

        Parses command, load settings and dispatches accordingly.

        """
        help_message = "Please supply chord progression!. See --help for more options."
        parser = argparse.ArgumentParser(description='chords2midi - Create MIDI files from written chord progressions.\n')
        parser.add_argument('progression', metavar='U', type=str, nargs='*', help=help_message)
        parser.add_argument('-B', '--bassline', action='store_true', default=False, help='Throw an extra bassline on the pattern')
        parser.add_argument('-b', '--bpm', type=int, default=80, help='Set the BPM (default 80)')
        parser.add_argument('-t', '--octave', type=str, default='4', help='Set the octave(s) (ex: 3,4) (default 4)')
        parser.add_argument('-i', '--input', type=str, default=None, help='Read from an input file.')
        parser.add_argument('-k', '--key', type=str, default='C', help='Set the key (default C)')
        parser.add_argument('-n', '--notes', type=int, default=99, help='Notes in each chord (default all)')
        parser.add_argument('-N', '--name', type=str, default='track', help='Set a name for the MIDI track')
        parser.add_argument('-d', '--duration', type=float, default=1.0, help='Set the chord duraction (default 1)')
        parser.add_argument('-D', '--directory', action='store_true', default=False, help='Output the contents to the directory of the input progression.')
        parser.add_argument('-H', '--humanize', type=float, default=0.0, help='Set the amount to "humanize" (strum) a chord, in ticks - try .11 (default 0.0)')
        parser.add_argument('-o', '--output', type=str, help='Set the output file path. Default is the current key and progression in the current location.')
        parser.add_argument('-O', '--offset', type=float, default=0.0, help='Set the amount to offset each chord, in ticks. (default 0.0)')
        parser.add_argument('-p', '--pattern', type=str, default=None, help='Set the pattern. Available patterns: ' + (', '.join(patterns.keys())))
        parser.add_argument('-r', '--reverse', action='store_true', default=False, help='Reverse a progression from C-D-E format into I-II-III format')
        parser.add_argument('-v', '--version', action='store_true', default=False,
            help='Display the current version of chords2midi')
        args = parser.parse_args(argv)
        self.vargs = vars(args)

        if self.vargs['version']:
            version = pkg_resources.require("chords2midi")[0].version
            print(version)
            return

        # Support `c2m I III V and `c2m I,III,V` formats.
        if not self.vargs['input']:
            if len(self.vargs['progression']) < 1:
                print("You need to supply a progression! (ex I V vi IV)")
                return
            if len(self.vargs['progression']) < 2:
                progression = self.vargs['progression'][0].split(',')
            else:
                progression = self.vargs['progression']
        else:
            with open(self.vargs['input']) as fn:
                content = ''.join(fn.readlines()).strip()
                content = content.replace('\n', ' ').replace(',', '  ')
                progression = content.split(' ')
        og_progression = progression

        # If we're reversing, we don't need any of the MIDI stuff.
        if self.vargs['reverse']:
            result = ""
            key = self.vargs['key']
            for item in progression:
                comps = pychord.Chord(item).components()
                position = determine(comps, key, True)[0]
                if 'M' in position:
                    position = position.upper()
                    position = position.replace('M', '')
                if 'm' in position:
                    position = position.lower()
                    position = position.replace('m', '')
                if 'B' in position:
                    position = position + "b"
                    position = position.replace('B', '')

                result = result + position + " "
            print(result)
            return

        track    = 0
        channel  = 0
        ttime     = 0
        duration = self.vargs['duration'] # In beats
        tempo    = self.vargs['bpm']   # In BPM
        volume   = 100  # 0-127, as per the MIDI standard
        bar = 0
        humanize_interval = self.vargs['humanize']
        directory = self.vargs['directory']
        num_notes = self.vargs['notes']
        offset = self.vargs['offset']
        key = self.vargs['key']
        octaves = self.vargs['octave'].split(',')
        root_lowest = self.vargs.get('root_lowest', False)
        bassline = self.vargs['bassline']
        pattern = self.vargs['pattern']

        # Could be interesting to do multiple parts at once.
        midi = MIDIFile(1)
        midi.addTempo(track, ttime, tempo)
        midi.addTrackName(0, 0, self.vargs["name"])

        ##
        # Main generator
        ##
        has_number = False
        progression_chords = []

        # Apply patterns
        if pattern:
            if pattern not in patterns.keys():
                print("Invalid pattern! Must be one of: " + (', '.join(patterns.keys())))
                return

            new_progression = []
            input_progression = progression[:] # 2.7 copy
            pattern_mask = patterns[pattern]
            pattern_mask_index = 0
            current_chord = None

            while True:
                pattern_instruction = pattern_mask[pattern_mask_index]

                if pattern_instruction == "N":
                    if len(input_progression) == 0:
                        break
                    current_chord = input_progression.pop(0)
                    new_progression.append(current_chord)
                elif pattern_instruction == "S":
                    new_progression.append(current_chord)
                elif pattern_instruction == "X":
                    new_progression.append("X")

                if pattern_mask_index == len(pattern_mask) - 1:
                    pattern_mask_index = 0
                else:
                    pattern_mask_index = pattern_mask_index + 1
            progression = new_progression

        # We do this to allow blank spaces
        for chord in progression:

            # This is for # 'I', 'VI', etc
            progression_chord = to_chords(chord, key)
            if progression_chord != []:
                has_number = True

            # This is for 'C', 'Am', etc.
            if progression_chord == []:
                try:
                    progression_chord = [pychord.Chord(chord).components()]
                except Exception:
                    # This is an 'X' input
                    progression_chord = [None]

            chord_info = {}
            chord_info['notes'] = progression_chord[0]
            if has_number:
                chord_info['number'] = chord
            else:
                chord_info['name'] = chord

            if progression_chord[0]:
                chord_info['root'] = progression_chord[0][0]
            else:
                chord_info['root'] = None
            progression_chords.append(chord_info)

        # For each input..
        previous_pitches = []
        for chord_index, chord_info in enumerate(progression_chords):

            # Unpack object
            chord = chord_info['notes']
            # NO_OP
            if chord == None:
                bar=bar+1
                continue
            root = chord_info['root']
            root_pitch = pychord.utils.note_to_val(notes.int_to_note(notes.note_to_int(root)))

            # Reset internals
            humanize_amount = humanize_interval
            pitches = []
            all_new_pitches = []

            # Turns out this algorithm was already written in the 1800s!
            # https://en.wikipedia.org/wiki/Voice_leading#Common-practice_conventions_and_pedagogy

            # a) When a chord contains one or more notes that will be reused in the chords immediately following, then these notes should remain, that is retained in the respective parts.
            # b) The parts which do not remain, follow the law of the shortest way (Gesetze des nachsten Weges), that is that each such part names the note of the following chord closest to itself if no forbidden succession XXX GOOD NAME FOR A BAND XXX arises from this.
            # c) If no note at all is present in a chord which can be reused in the chord immediately following, one must apply contrary motion according to the law of the shortest way, that is, if the root progresses upwards, the accompanying parts must move downwards, or inversely, if the root progresses downwards, the other parts move upwards and, in both cases, to the note of the following chord closest to them.
            root = None
            for i, note in enumerate(chord):

                # Sanitize notes
                sanitized_notes = notes.int_to_note(notes.note_to_int(note))
                pitch = pychord.utils.note_to_val(sanitized_notes)

                if i == 0:
                    root = pitch

                if root:
                    if root_lowest and pitch < root: # or chord_index is 0:
                        pitch = pitch + 12 # Start with the root lowest

                all_new_pitches.append(pitch)

                # Reuse notes
                if pitch in previous_pitches:
                    pitches.append(pitch)

            no_melodic_fluency = False # XXX: vargify
            if previous_pitches == [] or all_new_pitches == [] or pitches == [] or no_melodic_fluency:
                pitches = all_new_pitches
            else:
                # Detect the root direction
                root_upwards = None
                if pitches[0] >= all_new_pitches[0]:
                    root_upwards = True
                else:
                    root_upwards = False

                # Move the shortest distance
                if pitches != []:
                    new_remaining_pitches = list(all_new_pitches)
                    old_remaining_pitches = list(previous_pitches)
                    for i, new_pitch in enumerate(all_new_pitches):
                        # We're already there
                        if new_pitch in pitches:
                            new_remaining_pitches.remove(new_pitch)
                            old_remaining_pitches.remove(new_pitch)
                            continue

                    # Okay, so need to find the overall shortest distance from the remaining pitches - including their permutations!
                    while len(new_remaining_pitches) > 0:
                        nearest_distance = 9999
                        previous_index = None
                        new_index = None
                        pitch_to_add = None
                        for i, pitch in enumerate(new_remaining_pitches):
                            # XXX: DRY

                            # The Pitch
                            pitch_to_test = pitch
                            nearest = min(old_remaining_pitches, key=lambda x:abs(x-pitch_to_test))
                            old_nearest_index = old_remaining_pitches.index(nearest)
                            if nearest < nearest_distance:
                                nearest_distance = nearest
                                previous_index = old_nearest_index
                                new_index = i
                                pitch_to_add = pitch_to_test

                            # +12
                            pitch_to_test = pitch + 12
                            nearest = min(old_remaining_pitches, key=lambda x:abs(x-pitch_to_test))
                            old_nearest_index = old_remaining_pitches.index(nearest)
                            if nearest < nearest_distance:
                                nearest_distance = nearest
                                previous_index = old_nearest_index
                                new_index = i
                                pitch_to_add = pitch_to_test

                            # -12
                            pitch_to_test = pitch - 12
                            nearest = min(old_remaining_pitches, key=lambda x:abs(x-pitch_to_test))
                            old_nearest_index = old_remaining_pitches.index(nearest)
                            if nearest < nearest_distance:
                                nearest_distance = nearest
                                previous_index = old_nearest_index
                                new_index = i
                                pitch_to_add = pitch_to_test

                        # Before we add it - just make sure that there isn't a better place for it.
                        pitches.append(pitch_to_add)
                        del old_remaining_pitches[previous_index]
                        del new_remaining_pitches[new_index]

                        # This is for the C E7 type scenario
                        if len(old_remaining_pitches) == 0:
                            for x, extra_pitch in enumerate(new_remaining_pitches):
                                pitches.append(extra_pitch)
                                del new_remaining_pitches[x]

                    # Final check - can the highest and lowest be safely folded inside?
                    max_pitch = max(pitches)
                    min_pitch = min(pitches)
                    index_max = pitches.index(max_pitch)
                    folded_max = max_pitch - 12
                    if (folded_max > min_pitch) and (folded_max not in pitches):
                        pitches[index_max] = folded_max

                    max_pitch = max(pitches)
                    min_pitch = min(pitches)
                    index_min = pitches.index(min_pitch)

                    folded_min = min_pitch + 12
                    if (folded_min < max_pitch) and (folded_min not in pitches):
                        pitches[index_min] = folded_min

                    # Make sure the average can't be improved
                    # XXX: DRY
                    if len(previous_pitches) != 0:
                        previous_average = sum(previous_pitches) / len(previous_pitches)

                        # Max
                        max_pitch = max(pitches)
                        min_pitch = min(pitches)
                        index_max = pitches.index(max_pitch)
                        folded_max = max_pitch - 12

                        current_average = sum(pitches) / len(pitches)
                        hypothetical_pitches = list(pitches)
                        hypothetical_pitches[index_max] = folded_max
                        hypothetical_average = sum(hypothetical_pitches) / len(hypothetical_pitches)
                        if abs(previous_average-hypothetical_average) <= abs(previous_average-current_average):
                            pitches[index_max] = folded_max
                        # Min
                        max_pitch = max(pitches)
                        min_pitch = min(pitches)
                        index_min = pitches.index(min_pitch)
                        folded_min = min_pitch + 12

                        current_average = sum(pitches) / len(pitches)
                        hypothetical_pitches = list(pitches)
                        hypothetical_pitches[index_min] = folded_min
                        hypothetical_average = sum(hypothetical_pitches) / len(hypothetical_pitches)
                        if abs(previous_average-hypothetical_average) <= abs(previous_average-current_average):
                            pitches[index_min] = folded_min

                # Apply contrary motion
                else:
                    print ("Applying contrary motion!")
                    for i, new_pitch in enumerate(all_new_pitches):
                        if i == 0:
                            pitches.append(new_pitch)
                            continue

                        # Root upwards, the rest move down.
                        if root_upwards:
                            if new_pitch < previous_pitches[i]:
                                pitches.append(new_pitch)
                            else:
                                pitches.append(new_pitch - 12)
                        else:
                            if new_pitch > previous_pitches[i]:
                                pitches.append(new_pitch)
                            else:
                                pitches.append(new_pitch + 12)

            # Bassline
            if bassline:
                pitches.append(root_pitch - 24)

            # Melody

            # Octave is a simple MIDI offset counter
            for octave in octaves:
                for note in pitches:
                    pitch = int(note) + (int(octave.strip()) * 12)

                    # Don't humanize bassline note
                    if bassline and (pitches.index(note) == len(pitches) -1):
                        midi_time = offset + bar
                    else:
                        midi_time = offset + bar + humanize_amount

                    # Write the note
                    midi.addNote(
                        track=track,
                        channel=channel,
                        pitch=pitch,
                        time=midi_time,
                        duration=duration,
                        volume=volume
                    )

                humanize_amount = humanize_amount + humanize_interval
                if i + 1 >= num_notes:
                    break
            bar = bar + 1
            previous_pitches = pitches

        ##
        # Output
        ##

        if self.vargs['output']:
            filename = self.vargs['output']
        elif self.vargs['input']:
            filename = self.vargs['input'].replace('.txt', '.mid')
        else:
            if has_number:
                key_prefix = key + '-'
            else:
                key_prefix = ''

            filename = key_prefix + '-'.join(og_progression) + '-' + str(tempo)
            if bassline:
                filename = filename + "-bassline"
            if pattern:
                filename = filename + "-" + pattern
            if os.path.exists(filename):
                filename = key_prefix + '-'.join(og_progression) + '-' + str(tempo) + '-' + str(int(time.time()))
            filename = filename + '.mid'

            if directory:
                directory_to_create = '-'.join(og_progression)
                try:
                    os.makedirs(directory_to_create)
                except OSError as exc:  # Python >2.5
                    if exc.errno == errno.EEXIST and os.path.isdir(directory_to_create):
                        pass
                    else:
                        raise
                filename = directory_to_create + '/' + filename

        with open(filename, "wb") as output_file:
            midi.writeFile(output_file)


def handle(): # pragma: no cover
    """
    Main program execution handler.
    """
    try:
        c2m_obj = Chords2Midi()
        c2m_obj.handle()
    except (KeyboardInterrupt, SystemExit): # pragma: no cover
        return
    except Exception as e:
        print(e)
        traceback.print_exc()

if __name__ == '__main__': # pragma: no cover
    handle()
