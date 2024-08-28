import React, { useRef, useEffect } from 'react';
import { useChat } from '../hooks/useChat';
import { useSpeechRecognition } from '../hooks/useSpeechRecognition';

function ChatInterface({ userInput, setUserInput, handleSend, isLoading }) {
  const { isRecording, toggleRecording, recordedText } = useSpeechRecognition();
  const inputRef = useRef(null);

  useEffect(() => {
    if (recordedText) {
      setUserInput(recordedText);
    }
  }, [recordedText, setUserInput]);

  const handleSubmit = (e) => {
    e.preventDefault();
    handleSend();
  };

  return (
    <div className="input-container">
      <form onSubmit={handleSubmit} className="chat-form">
        <input
          ref={inputRef}
          type="text"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          placeholder="Type your message..."
          className="chat-input"
          disabled={isLoading || isRecording}
        />
        <div className="chat-controls">
          <button type="submit" className="chat-submit-button" disabled={isLoading || isRecording}>
            {isLoading ? 'Sending...' : 'Send'}
          </button>
          <button type="button" onClick={toggleRecording} className="record-button">
            {isRecording ? 'Stop Recording' : 'Start Recording'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default ChatInterface;