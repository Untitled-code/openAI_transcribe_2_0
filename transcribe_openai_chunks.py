import os

from openai import OpenAI
from pydub import AudioSegment


client = OpenAI(api_key=os.environ.get("OPENAIKEY"))


def _format_timestamp(seconds):
    total_milliseconds = max(0, int(round(seconds * 1000)))
    hours, remainder = divmod(total_milliseconds, 3600000)
    minutes, remainder = divmod(remainder, 60000)
    secs, milliseconds = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{milliseconds:03d}"


def _response_text(response):
    if isinstance(response, str):
        return response.strip()
    if hasattr(response, "text") and response.text:
        return response.text.strip()
    if isinstance(response, dict):
        return str(response.get("text", "")).strip()
    return ""


def _response_segments(response):
    if hasattr(response, "segments") and response.segments is not None:
        return response.segments
    if isinstance(response, dict):
        return response.get("segments", []) or []
    return []


def _segment_value(segment, key, default=None):
    if isinstance(segment, dict):
        return segment.get(key, default)
    return getattr(segment, key, default)


def main(audio_file, directory, timestamp):
    transcriptions = []
    timestamped_lines = []
    audio = AudioSegment.from_mp3(audio_file)

    chunk_length_ms = 60000
    chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]

    print("Transcribing chunks")
    for i, chunk in enumerate(chunks):
        chunk_file = f"chunk_{i}.mp3"
        chunk_offset_seconds = (i * chunk_length_ms) / 1000
        print(chunk_file)
        chunk.export(chunk_file, format="mp3")

        try:
            with open(chunk_file, "rb") as chunk_audio_file:
                response = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=chunk_audio_file,
                    response_format="verbose_json",
                )

            text = _response_text(response)
            if text:
                transcriptions.append(text)

            segments = _response_segments(response)
            if segments:
                for segment in segments:
                    segment_text = str(_segment_value(segment, "text", "")).strip()
                    if not segment_text:
                        continue
                    start = float(_segment_value(segment, "start", 0.0)) + chunk_offset_seconds
                    end = float(_segment_value(segment, "end", start)) + chunk_offset_seconds
                    timestamped_lines.append(
                        f"[{_format_timestamp(start)} - {_format_timestamp(end)}] {segment_text}"
                    )
            elif text:
                start = chunk_offset_seconds
                end = chunk_offset_seconds + (len(chunk) / 1000)
                timestamped_lines.append(
                    f"[{_format_timestamp(start)} - {_format_timestamp(end)}] {text}"
                )

            print(text)
        except Exception as e:
            print(e)
        finally:
            if os.path.exists(chunk_file):
                os.remove(chunk_file)

    full_transcription = "\n\n".join(transcriptions)
    with open(f"./{directory}/audio_{timestamp}.txt", "w+", encoding="utf-8") as f:
        f.write(full_transcription)

    with open(f"./{directory}/audio_{timestamp}_timecodes.txt", "w+", encoding="utf-8") as f:
        f.write("\n".join(timestamped_lines))


if __name__ == "__main__":
    filename = "dir_959676595_Oleg_d09ed0bbd0b5d0b3/Frank Sinatra – New York, New York.mp3"
    directory = "dir_959676595_Oleg_d09ed0bbd0b5d0b3"
    timestamp = "1232432"
    main(filename, directory, timestamp)
