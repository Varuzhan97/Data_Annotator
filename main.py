import os
import sys
import argparse
from datetime import datetime
from Utils import utils
from Utils import vad


#For disabling terminal logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

def parse_args():
    parser = argparse.ArgumentParser(description='Arguments and Their Descriptions.')
    parser.add_argument('--language_name', default = None,
                        help='An Argument For The Google Translate\'s API (En, De, Ru, etc.).')
    parser.add_argument('--text_data', default = None,
                        help='An Argument For The Absolute Path Of Input Text File.')
    args = parser.parse_args()
    if (args.language_name is None) or (args.text_data is None):
        print('Please Specify --language_name Argument.')
        sys.exit()
    return args

if __name__ == "__main__":
    params = parse_args()
    main_dir = os.getcwd()

    #Start the course
    #Make data collection path for language
    collection_folder = os.path.join(main_dir, "Collection")
    output_folder = os.path.join(collection_folder, params.language_name + "-" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    os.makedirs(output_folder, exist_ok=True)
    # Start audio with VAD
    vad_audio = vad.VADAudio(aggressiveness = 3, input_rate=16000)
    input_data = open(params.text_data, "r")
    file_data = input_data.readlines()

    for line in file_data:
        #Remove spaces from both side(begining and end) of string and return
        line = line.strip()
        #Load user speech
        file_name = str()
        file_size = str()
        file_name, file_size = vad.listen_audio(vad_audio, line, output_folder)
        #Check for audio length and update csv
        if utils.check_audio(line, file_name, file_size):
            #Update collected data in csv
            utils.write_to_csv(file_name, file_size, line, output_folder)
        else:
            print("--->|File is not valid.|<---")
            os.remove(file_name)

    csv_file_path = os.path.join(output_folder, "validated.csv")
    utils.generate_alphabet(csv_file_path, output_folder)
