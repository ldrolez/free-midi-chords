#!/usr/bin/env python3

# Copyright (c) 2025 handeyeco
#
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
import shutil
import re
import xml.etree.ElementTree as ET
import mido

# only convert progressions in C keys
name_regex = re.compile('.+/M[a-z]+/C - (.+) -.+.mid')
input_folder = "output/progression/4 Progression/"
output_folder = "output/ripchord/"

white_key_intervals = [2, 2, 1, 2, 2, 2, 1]
issues = False

def read_midi_file(source_path):
  # make sure this is a MIDI file
  name_match = name_regex.match(source_path)
  print(source_path)
  if not name_match:
    return

  # get chord names from file name
  chord_names = name_match.group(1).split()

  prog_dict = {}
  chord_count = 0
  trig_note = 60
  chord_notes = []

  midi_file = mido.MidiFile(source_path)
  for msg in midi_file:
    # collect groups of "note on" MIDI messages
    if msg.type == "note_on":
      chord_notes.append(msg.note)

    # when we hit a "note off" MIDI message
    # convert collected "note on" messages into a chord
    elif msg.type == "note_off" and len(chord_notes) > 0:
      # if we have more chords than chord names, something is wrong
      if chord_count >= len(chord_names):
        global issues
        issues = True
        print("!!! Something sus with: " + source_path)
        print("!!! Skipping: " + source_path)
        return

      # create a new mapping: trigger + name + chord
      prog_dict[trig_note] = {}
      prog_dict[trig_note]["notes"] = chord_notes
      prog_dict[trig_note]["name"] = chord_names[chord_count]

      # reset
      # this just puts all the mappings on white keys
      trig_note += white_key_intervals[chord_count % len(white_key_intervals)]
      chord_count += 1
      chord_notes = []
  return prog_dict

# not very interesting, just converting a dict to XML
def write_ripchord_file(prog_dict, dest_path):
  root_tag = ET.Element('ripchord')
  preset_tag = ET.SubElement(root_tag, 'preset')
  for key in prog_dict:
    input_tag = ET.SubElement(preset_tag, 'input')
    input_tag.set('note', str(key))
    chord_tag = ET.SubElement(input_tag, 'chord')
    chord_tag.set('name', prog_dict[key]["name"])
    chord_tag.set('notes', ';'.join(str(x) for x in prog_dict[key]["notes"]))
  tree = ET.ElementTree(root_tag)
  ET.indent(tree)
  os.makedirs(os.path.dirname(dest_path), exist_ok=True)
  tree.write(dest_path, encoding='utf-8', xml_declaration=True)
  

def main():
  # clean output folder
  for filename in os.listdir(output_folder):
    path = os.path.join(output_folder, filename)
    if os.path.isdir(path):
      shutil.rmtree(path)
    elif filename != ".gitkeep":
      os.remove(path)

  # generate files
  for root, dirs, files in os.walk(input_folder):
    for file in files:
      # Read the MIDI file
      input_file = os.path.join(root, file)
      prog_dict = read_midi_file(input_file)

      if not prog_dict:
        continue

      # Check if we're at the top level of the directory
      if root == input_folder:
        # If it's at the top level, we use the filename directly (no subdirectories).
        output_file = os.path.join(output_folder, file)
      else:
        # If it's inside a subdirectory, do not preserve the subdirectory structure
        # Instead prefix the file name with the subdir name for faster searches
        relative_path = os.path.relpath(root, input_folder)
        output_subdir = output_folder
        os.makedirs(output_subdir, exist_ok=True)
        output_file = os.path.join(output_subdir, 'SHLD '+relative_path+' '+file)
        output_file = os.path.splitext(output_file)[0]+'.rpc'

      # Create a new Ripchord preset
      write_ripchord_file(prog_dict, output_file)

  if issues:
    print("Done, with problems")
  else:
    print("Done, without problems")

main()
