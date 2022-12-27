import os
import time
import csv
import re
import sox
import subprocess

SAMPLE_RATE = 16000
MAX_SECS = 15
CHANNELS = 1

def check_audio(transcript, wav_filename, items_counter):
    file_size = -1
    frames = 0
    if os.path.exists(wav_filename):
        file_size = os.path.getsize(wav_filename)
        frames = int(subprocess.check_output(["soxi", "-s", wav_filename], stderr=subprocess.STDOUT))

    items_counter["all"] += 1
    items_counter["total_time"] += frames

    if file_size == -1:
        # Excluding samples that failed upon conversion
        items_counter["failed"] += 1
        return False, file_size
    elif transcript is None:
        # Excluding samples that failed on label validation
        items_counter["invalid_label"] += 1
        return False, file_size
    elif int(frames / SAMPLE_RATE * 1000 / 10 / 2) < len(str(transcript)):
        # Excluding samples that are too short to fit the transcript
        items_counter["too_short"] += 1
        return False, file_size
    elif frames / SAMPLE_RATE > MAX_SECS:
        # Excluding very long samples to keep a reasonable batch-size
        items_counter["too_long"] += 1
        return False, file_size
    else:
        # This one is good - keep it for the target CSV
        items_counter["imported_time"] += frames

    return True, file_size

def secs_to_hours(secs):
    hours, remainder = divmod(secs, 3600)
    minutes, seconds = divmod(remainder, 60)
    return '%d:%02d:%02d' % (hours, minutes, seconds)

def get_imported_samples(counter):
    return counter['all'] - counter['failed'] - counter['too_short'] - counter['too_long'] - counter['invalid_label']

def print_import_report(counter, max_secs):
    result = ""
    result += ('Successfully recorded %d samples.' % get_imported_samples(counter) + '\n')
    result += ('Skipped %d samples that failed upon conversion.' % counter['failed'] + '\n')
    result += ('Skipped %d samples that failed on transcript validation.' % counter['invalid_label'] + '\n')
    result += ('Skipped %d samples that were too short to match the transcript.' % counter['too_short'] + '\n')
    result += ('Skipped %d samples that were longer than %d seconds.' % (counter['too_long'], max_secs) + '\n')
    result += ('Final amount of imported audio: %s from %s.' % (secs_to_hours(counter['imported_time'] / SAMPLE_RATE), secs_to_hours(counter['total_time'] / SAMPLE_RATE)) + '\n')
    return result

def write_to_csv(file_name, file_size, transcription, output_folder):
    validated_file_path = os.path.join(output_folder, 'validated.csv')

    if os.path.isfile(validated_file_path):
        with open(validated_file_path, 'a') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter = ',')
            csvwriter.writerow([os.path.basename(file_name), str(file_size), transcription])
    else:
        csv_header = ['wav_filename','wav_filesize','transcript']
        with open(validated_file_path, 'w') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter = ',')
            csvwriter.writerow(csv_header)
            csvwriter.writerow([os.path.basename(file_name), str(file_size), transcription])

    return validated_file_path

def generate_alphabet(csv_file_path, output_file_path):
    output_file = os.path.join(output_file_path, 'alphabet.txt')
    all_text = set()
    with open(csv_file_path, "r") as csv_file:
        reader = csv.reader(csv_file)
        # Skip The File Header
        next(reader, None)
        for row in reader:
            all_text |= set(row[2])
    header_text = ['# Each line in this file represents the Unicode codepoint (UTF-8 encoded)\n', '# associated with a numeric label.\n', '# A line that starts with # is a comment. You can escape it with \# if you wish\n', '# to use \'#\' as a label.\n']
    footer_text = ['# The last (non-comment) line needs to end with a newline.\n']
    with open(output_file, "w") as alphabet_file:
        alphabet_file.writelines(header_text)
        for char in list(all_text):
            alphabet_file.write(char + '\n')
        alphabet_file.writelines(footer_text)
    print('Alphabet Path: %s.' %output_file)
