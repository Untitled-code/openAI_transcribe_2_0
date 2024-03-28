import os
from openai import OpenAI
from pydub import AudioSegment

# Set up OpenAI API key
# client = OpenAI(api_key=os.environ.get('OPENAIKEY'))
client = OpenAI(api_key=os.environ.get('OPENAIAPI_CJI'))
def main(audio_file, directory, timestamp):
# Load the audio file
    transcriptions = []
    audio = AudioSegment.from_mp3(audio_file)
    # Split audio file into chunks
    chunk_length_ms = 60000  # 60 seconds
    chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]

    # Transcribe each chunk
    print('Transcribing chunks')
    for i, chunk in enumerate(chunks):
        chunk_file = f"chunk_{i}.mp3"
        print(chunk_file)
        chunk.export(chunk_file, format="mp3")

        #Transcribe the audio chunk with the Whisper ASR API
        try:
            with open(chunk_file, "rb") as audio_file:
                response = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                    # response_format="verbose_json",
                    # timestamp_granularities=["word"]
                )

            # transcription = response['choices'][0]['text']
            print(response)
            # transcription = response['text']
            transcriptions.append(response)

            # Remove temporary chunk file
            os.remove(chunk_file)
        except Exception as e:
            print(e)
    # Combine transcriptions
    full_transcription = " ".join(transcriptions)
    with open(f'./{directory}/audio_{timestamp}.txt', "w+") as f:
        f.write(full_transcription)

if __name__ == "__main__":
    # filename='dir_959676595_Oleg_d09ed0bbd0b5d0b3/18 Efuge Efuge.mp3'
    # directory = 'dir_959676595_Oleg_d09ed0bbd0b5d0b3'
    # timestamp='1232432'
    main(filename, directory, timestamp)