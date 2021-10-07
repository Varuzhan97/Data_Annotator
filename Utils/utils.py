import os
import time
import csv

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

#Remove Audios That Are Shorter Than 0.5 Seconds And Longer Than 20 Seconds
#Remove Audios That Are Too Short For Transcript
def check_audio(transcript, file, size):
    if ((size / 32000) > 0.5 and (size / 32000) < 20 and transcript != "" and size / len(transcript) > 1400):
        return True
    else:
        print("--->|Invalid file.|<---")
        return False

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
