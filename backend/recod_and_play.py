import os
import sounddevice as sd 
import wavio as wv 


currentDir = "./recordings"
freq=44100

def micRecordining (duration):

    recordining = sd.rec(int(duration * freq),samplerate=freq, channels=1)
    sd.wait()
    return recordining

os.makedirs(currentDir, exist_ok=True)
print("Directory:",currentDir)
filename_counter = 1

while True:
    user_input = input("Press 'q' to stop or quit\n :")
    if user_input.lower() == 'q':
        print("Exitining recording")
        break

    duration = int(user_input)

    filename = f"recording{filename_counter}.wav"
    file_path = os.path.join(currentDir, filename)

    record_audio = micRecordining(duration)
    wv.write(file_path, record_audio, freq, sampwidth=2)
    print(f"Audio save to: {file_path}")
    print("recording comepleted")
    
    filename_counter +=1


# duration = 5 
# freq= 44100
# myRecording = sd.rec(int(duration* freq),samplerate= freq, channels=1)
# sd.wait()
# wv.write("rec1.wav", myRecording, freq, sampwidth=2)
