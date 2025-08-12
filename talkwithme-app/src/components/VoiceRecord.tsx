import React, {useState, useRef, useEffect} from "react";

declare global{
  interface Window{
    webkitSpeechRecognition:any;
  }
}


const VoiceRecord = () => {
  
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [recordingComepleted, setRecordingComepleted] = useState<boolean>(false);
  const [transcript, setTranscripts] = useState<string>("");

  const recognitionRef = useRef<any>(null);

  const startRec =() =>{
    setIsRecording(true);
    
    recognitionRef.current = new window.webkitSpeechRecognition();
    recognitionRef.current.continuous = true;
    recognitionRef.current.interimResults = true;

    recognitionRef.current.onresult =(event:any) =>{
      const { transcript} = event.results [event.results.length - 1][0];
      
      console.log(event.results);
      setTranscripts(transcript);
    }
    recognitionRef.current.start()
  }

  useEffect(() =>{
    return () =>{
      if(recognitionRef.current){
        recognitionRef.current.stop();
      }
    };
  },[])

  const stopRec =()=>{
    if (recognitionRef.current){
      setRecordingComepleted(true)
    }
  }

  const handleTroggleRec =()=>{
    setIsRecording(!isRecording)
    if(!isRecording){
      startRec();
    }else{
      stopRec();
    }
  }

  return (
    <>
    <div className="flex items-center justify-center h-screen w-full">
      
      {/* transcript section */}

          <div className="w-full">
            {(isRecording || transcript)&&(
              <div className="w-1/2 m-auto rounded-md border p-4 bg-blue-500">
                <div className="flex-1 flex w-full justify-between">
                  <div className="space-y-1">
                    <div className="flex space-x-2">
                       {isRecording &&(
                  <div className=" m-0 p-0 rounded-full bg-red-500 w-4 h-4 animate-pulse"></div>
                  )}
                    <p className="text-sm font-medium leading-none">
                      {recordingComepleted ? "Recorded" : "Recording"}
                    </p>
                    </div>
                    <p className="text-sm">
                      {recordingComepleted ? "Has been recored" : "Speak away..."}
                    </p>

                  </div>
                </div>

                {transcript &&(
                <div className=" border rounded-md p-2 m-4">
                <p className="mb-0">{transcript}</p>  
                </div>)}
                </div>
            )}

            {/* btn for rec */}

            <div className="flex items-center w-full">
              {isRecording? (
                <button onClick={handleTroggleRec}
                className="mt-10 m-auto flex items-center justify-center rounded-full bg-red-500 hover:bg-red-800">
                  <svg xmlns="http://www.w3.org/2000/svg" 
                  className="h-8 w-8"
                  viewBox="0 0 21 21" fill="#ffffff"><g fill="none" fill-rule="evenodd" stroke="#ffffff" stroke-linecap="round" stroke-linejoin="round"><path d="m10.39 2.615l.11-.004a2.893 2.893 0 0 1 3 2.891V9.5a3 3 0 1 1-6 0V5.613a3 3 0 0 1 2.89-2.998z"/><path d="M15.5 9.5a5 5 0 0 1-9.995.217L5.5 9.5m5 5v4"/></g></svg>
                </button>):(
                <button onClick={handleTroggleRec}
                className="mt-10 m-auto flex item-center justify-center rounded-full bg-red-500 hover:bg-red-800">
                  <svg xmlns="http://www.w3.org/2000/svg" 
                  className="h-8 w-8" 
                  viewBox="0 0 24 24" 
                  fill="#ffffff"><path fill="#ffffff" d="M9 6a1 1 0 0 1 1 1v10a1 1 0 1 1-2 0V7a1 1 0 0 1 1-1zm6 0a1 1 0 0 1 1 1v10a1 1 0 1 1-2 0V7a1 1 0 0 1 1-1z"/></svg>
                </button>       
              )}
            </div>
          </div>
    </div>
    </>
  )
}

export default VoiceRecord
