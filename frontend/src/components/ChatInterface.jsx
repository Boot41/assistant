import { useRef, useEffect } from 'react';
import PropTypes from 'prop-types';
import { useChat } from '../hooks/useChat';
import { useSpeechRecognition } from '../hooks/useSpeechRecognition';

function ChatInterface({ userInput, setUserInput, handleSend, isLoading, isRecording, setIsRecording, currentPage }) {
  const { toggleRecording, recordedText } = useSpeechRecognition();
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

  const handleToggleRecording = () => {
    toggleRecording();
    if (typeof setIsRecording === 'function') {
      setIsRecording(prev => !prev);
    } else {
      console.error('setIsRecording is not a function');
    }
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
          <button type="button" onClick={handleToggleRecording} className="record-button">
            {isRecording ? 'Stop Recording' : 'Start Recording'}
          </button>
        </div>
      </form>
    </div>
  );
}

ChatInterface.propTypes = {
  userInput: PropTypes.string.isRequired,
  setUserInput: PropTypes.func.isRequired,
  handleSend: PropTypes.func.isRequired,
  isLoading: PropTypes.bool.isRequired,
  isRecording: PropTypes.bool.isRequired,
  setIsRecording: PropTypes.func.isRequired,
};

export default ChatInterface;