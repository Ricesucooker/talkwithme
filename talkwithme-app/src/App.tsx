import React from 'react';
import './App.css';
import VoiceRecord from './components/VoiceRecord';


function App() {
  return (
    <div className="App">
      <div>
        <h1 className=" text-3xl font-bold">Welcome to TalkWithMe app</h1>
      <p>An open source self tape application, please note that this is still working progess so feedback are all welcome. Please note that it's just me, currently working on this project so update or bug fixed may be a little slow.</p>
      </div>
    <div>
      <VoiceRecord />
    </div>
    </div>
  
  );
}

export default App;
