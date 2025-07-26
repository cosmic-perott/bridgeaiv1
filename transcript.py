# NOT PART OF THE ACTUAL CODE, JUST USED THIS FILE TO TRY OUT SOME THINGS

from faster_whisper import WhisperModel

def build_transcript():
    model_size = "small"

    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    segments, info = model.transcribe("audio.mp3", beam_size=5)

    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

    transcript = ""
    for segment in segments:
        print("[%.2fs - %.2fs] %s \n" % (segment.start, segment.end, segment.text))
        transcript += "[%.2fs - %.2fs] %s \n" % (segment.start, segment.end, segment.text)
    
    return transcript
