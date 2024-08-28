import React from 'react';
import Jarvis from './blob';

function JarvisContainer({ isSpeaking }) {
  return (
    <div className="jarvis-container">
      <Jarvis isSpeaking={isSpeaking} />
    </div>
  );
}

export default JarvisContainer;