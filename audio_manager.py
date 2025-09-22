import pyttsx3
import pyaudio
import wave
import os
import webrtcvad
import numpy as np

class audioManager:
    def __init__(self):
        try:
            self.engine = pyttsx3.init()
        except Exception as e: 
            raise RuntimeError(f"Could not initialize TTS engin {e}")
        
        self.is_running = False
        self.pyaudio = pyaudio.PyAudio()
        self.vad = webrtcvad.Vad(3) #

        #audio parameter for voice activation detection 
        self.audio_params = {
            "chunk": 480,
            "sample_format": pyaudio.paInt16,
            "channels": 1,
            "fs": 16000    
        }

        self.VAD_SILENCE_FRAMES = 200
        self.MAX_RRECORDING_TIME_SECOND = 60

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def record_audio_until_silence(self, filename):
        frames = []
        speaking_frames = 0 
        silent_frame = 0 

        stream = self.pyaudio.open(format=self.audio_params["sample_format"],
                                   channels=self.audio_params["channels"],
                                   rate=self.audio_params["fs"],
                                   frames_per_buffer=self.audio_params["chunk"],
                                   input=True)
        
        while self.is_running:
            try:
                data = stream.read(self.audio_params["chunk"])
                frames.append(data)

                is_speech = self.vad.is_speech(data, self.audio_params["fs"])

                if is_speech:
                    silent_frame =0
                    speaking_frames +=1
                elif speaking_frames > 0:
                    silent_frame +=1
                
                if silent_frame > self.VAD_SILENCE_FRAMES:
                    break
            except IOError as e:
                if e.errno == pyaudio.paInputOverflowed:
                    continue
                else:
                    raise
        stream.stop_stream()
        stream.close()

        #saving the recording data 
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.audio_params["channels"])
            wf.setsampwidth(self.pyaudio.get_sample_size(self.audio_params["sample_format"]))
            wf.setframerate(self.audio_params["fs"])
            wf.writeframes(b''.join(frames))
        return filename
    
    def play_audio_file(self, filename):
        if not os.path.exists(filename):
            print(f"File not dound: {filename}")
            return
        try:
            with wave.open(filename, 'rb') as wf:
                stream = self.pyaudio.open(format=self.pyaudio.get_format_from_width(wf.getsampwidth()),
                                           channels=wf.getnchannels(),
                                           rate=wf.getframerate(),
                                           output=True)
                
                data = wf.readframes(self.audio_params["chunk"])
                while data:
                    stream.write(data)
                    data = wf.readframes(self.audio_params["chunk"])

                    stream.stop_stream()
                    stream.close()
        except Exception as e:
            print(f"Error during playback: {e}")

    def shutdown(self):
        self.pyaudio.terminate()