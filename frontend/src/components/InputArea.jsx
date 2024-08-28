import React from 'react';
import { useChat } from '../context/ChatContext';
import { useAudioRecording } from '../hooks/useAudioRecording';
import '../styles/InputArea.css';

const InputArea = () => {
  const { userInput, setUserInput, handleSend } = useChat();
  const { isRecording, toggleRecording } = useAudioRecording();

  const handleSubmit = (e) => {
    e.preventDefault();
    handleSend();
  };

  return (
    <form className="input-area" onSubmit={handleSubmit}>
      <textarea 
        value={userInput}
        onChange={(e) => setUserInput(e.target.value)}
        placeholder="Type your message..."
      />
      <button type="submit">Send</button>
      <button type="button" onClick={toggleRecording}>
        {isRecording ? 'Stop' : 'Start'} Recording
      </button>
    </form>
  );
};

export default InputArea;