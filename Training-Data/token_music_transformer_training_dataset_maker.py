# -*- coding: utf-8 -*-
"""Token_Music_Transformer_Training_Dataset_Maker.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1MMYq2iD-z6h1QRADAdfhmDuvSVn5GUQ4

# Token Music Transformer Training Dataset Maker (ver. 1.0)

***

Powered by tegridy-tools: https://github.com/asigalov61/tegridy-tools

***

#### Project Los Angeles

#### Tegridy Code 2023

***

# (SETUP ENVIRONMENT)
"""

#@title Install all dependencies (run only once per session)

!git clone https://github.com/asigalov61/tegridy-tools
!pip install tqdm

#@title Import all needed modules

print('Loading needed modules. Please wait...')
import os

import math
import statistics
import random

from tqdm import tqdm

if not os.path.exists('/content/Dataset'):
    os.makedirs('/content/Dataset')

print('Loading TMIDIX module...')
os.chdir('/content/tegridy-tools/tegridy-tools')

import TMIDIX

print('Done!')

os.chdir('/content/')
print('Enjoy! :)')

"""# (DOWNLOAD SOURCE MIDI DATASET)"""

# Commented out IPython magic to ensure Python compatibility.
#@title Download original LAKH MIDI Dataset

# %cd /content/Dataset/

!wget 'http://hog.ee.columbia.edu/craffel/lmd/lmd_full.tar.gz'
!tar -xvf 'lmd_full.tar.gz'
!rm 'lmd_full.tar.gz'

# %cd /content/

#@title Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

"""# (FILE LIST)"""

#@title Save file list
###########

print('Loading MIDI files...')
print('This may take a while on a large dataset in particular.')

dataset_addr = "/content/Dataset"
# os.chdir(dataset_addr)
filez = list()
for (dirpath, dirnames, filenames) in os.walk(dataset_addr):
    filez += [os.path.join(dirpath, file) for file in filenames]
print('=' * 70)

if filez == []:
    print('Could not find any MIDI files. Please check Dataset dir...')
    print('=' * 70)

print('Randomizing file list...')
random.shuffle(filez)

TMIDIX.Tegridy_Any_Pickle_File_Writer(filez, '/content/drive/MyDrive/filez')

#@title Load file list
filez = TMIDIX.Tegridy_Any_Pickle_File_Reader('/content/drive/MyDrive/filez')

"""# (PROCESS)"""

#@title Process MIDIs with TMIDIX MIDI processor

print('=' * 70)
print('TMIDIX MIDI Processor')
print('=' * 70)
print('Starting up...')
print('=' * 70)

###########

START_FILE_NUMBER = 0
LAST_SAVED_BATCH_COUNT = 0

input_files_count = START_FILE_NUMBER
files_count = LAST_SAVED_BATCH_COUNT

melody_chords_f = []

stats = [0, 0, 0, 0, 0]

print('Processing MIDI files. Please wait...')
print('=' * 70)

for f in tqdm(filez[START_FILE_NUMBER:]):
    try:
        input_files_count += 1

        fn = os.path.basename(f)
        fn1 = fn.split('.')[0]

        # Filtering out giant MIDIs
        file_size = os.path.getsize(f)

        if file_size < 200000:

          #=======================================================
          # START PROCESSING

          # Convering MIDI to ms score with MIDI.py module
          score = TMIDIX.midi2ms_score(open(f, 'rb').read())

          # INSTRUMENTS CONVERSION CYCLE
          events_matrix = []
          itrack = 1
          patches = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

          patch_map = [
                      [0, 1, 2, 3, 4, 5, 6, 7], # Piano 
                      [24, 25, 26, 27, 28, 29, 30], # Guitar
                      [32, 33, 34, 35, 36, 37, 38, 39], # Bass
                      [40, 41], # Violin
                      [42, 43], # Cello
                      [46], # Harp
                      [56, 57, 58, 59, 60], # Trumpet
                      [64, 65, 66, 67, 68, 69, 70, 71], # Sax
                      [72, 73, 74, 75, 76, 77, 78], # Flute
                      [-1], # Drums
                      [52, 53], # Choir
                      [16, 17, 18, 19, 20] # Organ
                      ]

          while itrack < len(score):
              for event in score[itrack]:         
                  if event[0] == 'note' or event[0] == 'patch_change':
                      events_matrix.append(event)
              itrack += 1

          events_matrix.sort(key=lambda x: x[1])

          events_matrix1 = []

          for event in events_matrix:
                  if event[0] == 'patch_change':
                      patches[event[2]] = event[3]

                  if event[0] == 'note':
                      event.extend([patches[event[3]]])
                      once = False
                      
                      for p in patch_map:
                          if event[6] in p and event[3] != 9: # Except the drums
                              event[3] = patch_map.index(p)
                              once = True
                              
                      if not once and event[3] != 9: # Except the drums
                          event[3] = 15 # All other instruments/patches channel
                          event[5] = max(90, event[5])
                          
                      if event[3] in [0, 1, 2, 3, 6, 7, 8, 9]: # We won't write useless chans...
                          # recalculating timings
                          event[1] = int(event[1] / 10)
                          event[2] = int(event[2] / 10)
                            
                          event[5] = 90
                          event[6] = 0
                            
                          events_matrix1.append(event)
                      
                      else:
                          # putting all other events as drums (42) to keep the beat
                          
                          event[2] = 20
                          event[3] = 9
                          event[4] = 42
                          event[5] = 90
                          event[6] = 0
                            
                          # recalculating timings
                          event[1] = int(event[1] / 10)
                          event[2] = int(event[2] / 10)

                          if event not in events_matrix1:
                            events_matrix1.append(event)

          #==========================================================================

          # Rearranging channels

          for e in events_matrix1:
            if e[3] in [6, 7, 8]:
              e[3] = 3 # Leads channel (Violin, Trumpet, Sax, Flute)
            
            if e[3] == 9: 
              e[3] = 4 # Drums channel

          events_matrix1.sort(key=lambda x: x[4], reverse=True)
          events_matrix1.sort(key=lambda x: x[1])

          output_signature = 'Project Los Angeles'
          track_name='Tegridy Code 2022'
          list_of_MIDI_patches=[0, 24, 32, 40, 42, 46, 56, 71, 73, 0, 53, 19, 0, 0, 0, 0]
          text_encoding='ISO-8859-1'

          output_header = [score[0], 
                          [['track_name', 0, bytes(output_signature, text_encoding)]]]                                                    

          patch_list = [['patch_change', 0, 0, list_of_MIDI_patches[0]], 
                          ['patch_change', 0, 1, list_of_MIDI_patches[1]],
                          ['patch_change', 0, 2, list_of_MIDI_patches[2]],
                          ['patch_change', 0, 3, list_of_MIDI_patches[3]],
                          ['patch_change', 0, 4, list_of_MIDI_patches[4]],
                          ['patch_change', 0, 5, list_of_MIDI_patches[5]],
                          ['patch_change', 0, 6, list_of_MIDI_patches[6]],
                          ['patch_change', 0, 7, list_of_MIDI_patches[7]],
                          ['patch_change', 0, 8, list_of_MIDI_patches[8]],
                          ['patch_change', 0, 9, list_of_MIDI_patches[9]],
                          ['patch_change', 0, 10, list_of_MIDI_patches[10]],
                          ['patch_change', 0, 11, list_of_MIDI_patches[11]],
                          ['patch_change', 0, 12, list_of_MIDI_patches[12]],
                          ['patch_change', 0, 13, list_of_MIDI_patches[13]],
                          ['patch_change', 0, 14, list_of_MIDI_patches[14]],
                          ['patch_change', 0, 15, list_of_MIDI_patches[15]],
                          ['track_name', 0, bytes(track_name, text_encoding)]]

          final_score = output_header + [patch_list + events_matrix1]

          opus = TMIDIX.score2opus(final_score)

          #=======================================================
          # PRE-PROCESSING

          # checking number of instruments in a composition
          instruments_list_without_drums = list(set([y[2] for y in opus[2][17:] if y[2] != 9]))

          instruments_list = list(set([y[2] for y in opus[2][17:]]))
          num_instr = len(instruments_list)

          # filtering out empty compositions and checking desired number of instruments in a composition
          # It had been observed that music models learn best from multi-instrumental music, even for solo instruments
          # So you can setup filtering by number of instruments here if you want

          if len(opus[2][17:]) > 1600 and len(instruments_list_without_drums) > 0:

            #=======================================================
            # FINAL PRE-PROCESSING

            melody_chords = []

            events = ['note_on', 'note_off']
      
            for e in opus[2][17:]:
              if e[1] >= 0 and e[0] in events:
                if e[3] > 20 and e[3] < 109:

                  # Cliping all values...
                  time = max(0, min(31, e[1]))
                  cha = max(0, min(4, e[2]))
                  aug_ptc = (max(21, min(108, e[3]))) - 21 # 88 pitches range, shifted to 0 <--> 88

                  if e[0] == 'note_on':
                    velocity = 90
                  else:
                    velocity = 0

                  # Writing final note
                  melody_chords.append([time, cha, aug_ptc, velocity])

            #=======================================================
            # FINAL PROCESSING
            #=======================================================            

            times = [y[0] for y in melody_chords]
            avg_time = sum(times) / len(times)

            if len(melody_chords) > 1600 and avg_time < 16:
                
              #=======================================================
              # 28168 == SOS/EOS token
              # 28160-28161 == Composition is without drums or with drums
              # 28162-28166 == First note instrument
              #=======================================================

              #=======================================================
              # Break between compositions / Intro seq
              #=======================================================

              if 9 in instruments_list:
                drums_present = 28161 # Yes
              else:
                drums_present = 28160 # No

              first_note_channel = melody_chords[0][1] # 0 <--> 4
              
              melody_chords_f.extend([28168, drums_present, 28162+first_note_channel])
              
              #=======================================================
              # MAIN FINAL PROCESSING CYCLE
              #=======================================================
              
              events_counter = 0

              for m in melody_chords:

                if len(melody_chords) - events_counter == 400:
                  melody_chords_f.extend([28167]) # Outro token

                # WRITING EACH NOTE HERE

                if m[3] != 0:
                  cha_ptc_time = (m[1] * 88 * 32) + (m[2] * 32) + m[0] # note_on token
                else:
                  cha_ptc_time = ((m[1]+5) * 88 * 32) + (m[2] * 32) + m[0] # note_off token / channels = 5-9

                melody_chords_f.extend([cha_ptc_time])

                events_counter += 1
                stats[m[1]] += 1

              #=======================================================
              # TOTAL DICT SIZE 28168 + 1 = 28169
              #=======================================================

              # Processed files counter
              files_count += 1

              # Saving every 5000 processed files
              if files_count % 5000 == 0:
                print('SAVING !!!')
                print('=' * 70)
                print('Saving processed files...')
                print('=' * 70)
                print('Data check:', min(melody_chords_f), '===', max(melody_chords_f), '===', len(list(set(melody_chords_f))), '===', len(melody_chords_f))
                print('=' * 70)
                print('Processed so far:', files_count, 'out of', input_files_count, '===', files_count / input_files_count, 'good files ratio')
                print('=' * 70)
                count = str(files_count)
                TMIDIX.Tegridy_Any_Pickle_File_Writer(melody_chords_f, '/content/drive/MyDrive/LAKH_INTs_'+count)
                melody_chords_f = []
                print('=' * 70)
        
    except KeyboardInterrupt:
        print('Saving current progress and quitting...')
        break  

    except Exception as ex:
        print('WARNING !!!')
        print('=' * 70)
        print('Bad MIDI:', f)
        print('Error detected:', ex)
        print('=' * 70)
        continue

# Saving last processed files...
print('=' * 70)
print('Saving processed files...')
print('=' * 70)
print('Data check:', min(melody_chords_f), '===', max(melody_chords_f), '===', len(list(set(melody_chords_f))), '===', len(melody_chords_f))
print('=' * 70)
print('Processed so far:', files_count, 'out of', input_files_count, '===', files_count / input_files_count, 'good files ratio')
print('=' * 70)
count = str(files_count)
TMIDIX.Tegridy_Any_Pickle_File_Writer(melody_chords_f, '/content/drive/MyDrive/LAKH_INTs_'+count)

# Displaying resulting processing stats...
print('=' * 70)
print('Done!')   
print('=' * 70)

print('Resulting Stats:')
print('=' * 70)
print('Total good processed MIDI files:', files_count)
print('=' * 70)

print('Instruments stats:')
print('=' * 70)
print('Piano:', stats[0])
print('Guitar:', stats[1])
print('Bass:', stats[2])
print('Lead:', stats[3])
print('Drums:', stats[4])
print('=' * 70)

"""# (TEST INTS)"""

#@title Test INTs

track_name='Token'
output_signature = 'Project Los Angeles'
list_of_MIDI_patches=[0, 24, 32, 40, 42, 46, 56, 71, 73, 0, 53, 19, 0, 0, 0, 0]
text_encoding='ISO-8859-1'
output_file_name = '/content/Token-Music-Transformer-Composition'

train_data1 = melody_chords_f

print('Sample INTs', train_data1[:15])

out = train_data1[:200000]

if len(out) != 0:
    
    song = out
    song_f = []
    time = 0
    dur = 0
    vel = 0
    pitch = 0
    channel = 0

    for ss in song:
      if ss < 28160: # Filtering out special tokens

        channel = (ss // 32) // 88
        pitch = (ss // 32) % 88

        if (ss % 32) < 28:
          time = (ss % 32) * 20
        else:
          time = 1000

        if channel < 5:
          if channel == 4: # Restoring drums channel
            channel = 9
          song_f.append(['note_on', time, channel, pitch+21, 90])
        else:
          channel = channel - 5
          if channel == 4: # Restoring drums channel
            channel = 9
          song_f.append(['note_off', time, channel, pitch+21, 0])
                        
    output_header = [1000, 
                    [['track_name', 0, bytes(output_signature, text_encoding)]]]                                                    

    patch_list = [['patch_change', 0, 0, list_of_MIDI_patches[0]], 
                    ['patch_change', 0, 1, list_of_MIDI_patches[1]],
                    ['patch_change', 0, 2, list_of_MIDI_patches[2]],
                    ['patch_change', 0, 3, list_of_MIDI_patches[3]],
                    ['patch_change', 0, 4, list_of_MIDI_patches[4]],
                    ['patch_change', 0, 5, list_of_MIDI_patches[5]],
                    ['patch_change', 0, 6, list_of_MIDI_patches[6]],
                    ['patch_change', 0, 7, list_of_MIDI_patches[7]],
                    ['patch_change', 0, 8, list_of_MIDI_patches[8]],
                    ['patch_change', 0, 9, list_of_MIDI_patches[9]],
                    ['patch_change', 0, 10, list_of_MIDI_patches[10]],
                    ['patch_change', 0, 11, list_of_MIDI_patches[11]],
                    ['patch_change', 0, 12, list_of_MIDI_patches[12]],
                    ['patch_change', 0, 13, list_of_MIDI_patches[13]],
                    ['patch_change', 0, 14, list_of_MIDI_patches[14]],
                    ['patch_change', 0, 15, list_of_MIDI_patches[15]],
                    ['track_name', 0, bytes(track_name, text_encoding)]]

    final_score = output_header + [patch_list + song_f]

    midi_data = TMIDIX.opus2midi(final_score)

    with open(output_file_name + '.mid', 'wb') as midi_file:
        midi_file.write(midi_data)
        midi_file.close()

    print('Done!')

"""# Congrats! You did it! :)"""