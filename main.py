import os
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence  


filename = "./recordings/test.wav"

recognition = sr.Recognizer()


#small files 
def small_speech():
    with sr.AudioFile(filename) as source:
        print("Reading data...")
        auido_data = recognition.record(source)
        text = recognition.recognize_google(auido_data)
        print(text)


def transscribe_audio(path):
    print ("Reading data...")
    with sr.AudioFile(path) as source:
        auido_listened = recognition.record(source)
        text = recognition.recognize_google(auido_listened)
    return text

#chuncking on slicence 
def transscribe_large_audio_with_chuncking(path):
    sound = AudioSegment.from_file(path)
    chunks_audio = split_on_silence(sound,
                              min_silence_len = 500,
                              silence_thresh = sound.dBFS-14,
                              keep_silence=500,)
    
    folder_name = "audio-chunks"
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    whole_text =""
    
    for i, audio_chunk in enumerate(chunks_audio, start=1):
        chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format ="wav")

        try:
            text=transscribe_audio(chunk_filename)
        except sr.UnknownValueErrror as e:
            print("Error:", str(e))
        else:
            text=f"{text}."
            print(chunk_filename, ":", text)
            whole_text += text
        return whole_text
    

path = filename
print("\nFull text:", transscribe_large_audio_with_chuncking(path))