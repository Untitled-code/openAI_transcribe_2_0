# -*- coding: utf-8 -*-

from pathlib import Path
import datetime
import logging
import subprocess
import transcribe_openai_chunks
import os
logging.basicConfig(filename='transcriber_bot.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

API_TOKEN = os.environ.get('AUDIOOPENAI')
print(API_TOKEN)
def audio():
    """Prepairing folder"""
    """Prepairing directory with chat_id and output file with timestamp"""
    TIMESTAMP = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3] #with miliseconds
    directory = 'toTranscribe'
    print(f'Directory: {directory}')
    logging.debug(f'Directory: {directory}')
    Path(directory).mkdir(exist_ok=True)  # creating a new directory if not exist
    print(f'Directory is made... {directory}')
    logging.debug(f'Directory is made... {directory}')
    fileName = '20230401-003000-VLE122-program.mp3 '
    filename = f"{directory}/{fileName}"
    print(filename, directory, TIMESTAMP)
    logging.debug(filename, directory, TIMESTAMP)
    if filename.endswith('mp3'):
        print("It is mp3")
        newFile = filename
    else:
        newFile = f"{directory}/audio_{TIMESTAMP}.mp3"
        try:
            print(f"Start converting {filename} to {newFile}")
            logging.debug(f"Start converting {filename} to {newFile}")
            subprocess.call(['bash', 'audioConvert.sh', filename, newFile])
        except:
            print("something wrong with the conversion")

    transcribe_openai_chunks.main(newFile, directory, TIMESTAMP)
    output_file = f'./{directory}/audio_{TIMESTAMP}.txt'
    print(f'File is ready... {output_file}')
    logging.debug(f'File is ready... {output_file}')

    os.remove(filename)
    print(f"Files {filename}, {newFile} were removed")
    logging.debug(f"Files {filename}, {newFile} were removed")


    """End of program"""

audio()