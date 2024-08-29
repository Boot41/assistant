import React from 'react';
import Jarvis from './blob';

function JarvisContainer({ isSpeaking, isRecording }) {
  return (
    <div className="jarvis-container">
      <Jarvis isSpeaking={isSpeaking} isRecording={isRecording} />
    </div>
  );
}

export default JarvisContainer;