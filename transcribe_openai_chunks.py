import os
import openai
from pydub import AudioSegment

# Set up OpenAI API key
openai.api_key = os.environ.get('OPENAIKEY')
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
        chunk.export(chunk_file, format="mp3")

        #Transcribe the audio chunk with the Whisper ASR API
        try:
            with open(chunk_file, "rb") as audio_file:
                response = openai.Audio.transcribe("whisper-1", audio_file, {
                    "response-format": "text"})
                    #"language": "uk"})

            # transcription = response['choices'][0]['text']
            transcription = response['text']
            print(transcription)
            transcriptions.append(transcription)

            # Remove temporary chunk file
            os.remove(chunk_file)
        except Exception as e:
            print(e)
    # Combine transcriptions
    full_transcription = " ".join(transcriptions)
    with open(f'./{directory}/audio_{timestamp}.txt', "w+") as f:
        f.write(full_transcription)

if __name__ == "__main__":
    main(filename, directory, timestamp)
