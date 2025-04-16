import os
import whisper

model = whisper.load_model("large")
def main(audio_file, directory, timestamp):

    result = model.transcribe(audio_file)
    print(result["text"])

    # Create a WriteSRT instance using the transcription segments
    srt_writer = whisper.utils.get_writer("all", directory)
    srt_writer(result, audio_file, {})

    # # Combine transcriptions
    # with open(f'./{directory}/audio_{timestamp}.txt', "w+") as f:
    #         f.write(full_transcription)

if __name__ == "__main__":
    # filename='dir_959676595_Oleg_d09ed0bbd0b5d0b3/35 The Fall.mp3'
    # directory = 'dir_959676595_Oleg_d09ed0bbd0b5d0b3'
    # timestamp='1232432'
    main(filename, directory, timestamp)