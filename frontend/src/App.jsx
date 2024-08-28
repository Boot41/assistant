import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';
import gsap from 'gsap';
import Jarvis from './components/blob';
import ChatHistory from './components/ChatHistory';

function App() {
  const [userInput, setUserInput] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [recognition, setRecognition] = useState(null);
  const inputRef = useRef(null);
  const [isChatHistoryOpen, setIsChatHistoryOpen] = useState(false);

  useEffect(() => {
    // Initial greeting from Jarvis
    setChatHistory([{ role: 'assistant', content: "Hello! I'm Jarvis, your AI assistant. How can I help you today?" }]);
  }, []);

  const handleUserInput = async (e) => {
    e.preventDefault();
    if (!userInput.trim()) return;

    try {
      setIsLoading(true);
      setChatHistory(prevHistory => [...prevHistory, { role: 'user', content: userInput }]);
      
      const res = await axios.post('http://localhost:8000/api/chat/', { user_input: userInput });
      
      setChatHistory(prevHistory => [...prevHistory, { role: 'assistant', content: res.data.response }]);
      speakResponse(res.data.response);

      setUserInput('');
      if (inputRef.current) {
        inputRef.current.focus();
      }
    } catch (error) {
      console.error('Error processing interaction:', error);
      setChatHistory(prevHistory => [...prevHistory, { role: 'assistant', content: "I'm sorry, I encountered an error. Could you please try again?" }]);
    } finally {
      setIsLoading(false);
    }
  };

  const speak = (text) => {
    if ('speechSynthesis' in window) {
      speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);
      speechSynthesis.speak(utterance);
    }
  }

  const speakResponse = (response) => {
    speak(response);
  };

  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const startRecording = () => {
    if ('webkitSpeechRecognition' in window) {
      const newRecognition = new window.webkitSpeechRecognition();
      newRecognition.continuous = true;
      newRecognition.interimResults = true;

      newRecognition.onstart = () => {
        setIsRecording(true);
      };

      newRecognition.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map(result => result[0].transcript)
          .join('');
        setUserInput(transcript);
      };

      newRecognition.onerror = (event) => {
        console.error('Speech recognition error', event.error);
        setIsRecording(false);
      };

      newRecognition.onend = () => {
        setIsRecording(false);
      };

      newRecognition.start();
      setRecognition(newRecognition);
    } else {
      console.error('Speech recognition not supported');
    }
  };

  const stopRecording = () => {
    if (recognition) {
      recognition.stop();
      setRecognition(null);
    }
  };

  const toggleChatHistory = () => {
    console.log("Toggling chat history. Current state:", isChatHistoryOpen);
    setIsChatHistoryOpen(!isChatHistoryOpen);
  };

  return (
    <div className="app-container">
      <div className="content-wrapper">
        <div className="jarvis-container">
          <Jarvis isSpeaking={isSpeaking} />
        </div>
        
        <ChatHistory chatHistory={chatHistory} isOpen={isChatHistoryOpen} />
      </div>
      
      <div className="input-container">
        <form onSubmit={handleUserInput} className="chat-form">
          <input
            ref={inputRef}
            type="text"
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="Type your message..."
            className="chat-input"
            disabled={isLoading}
          />
          <div className="chat-controls">
            <button type="submit" className="chat-submit-button" disabled={isLoading}>
              {isLoading ? 'Sending...' : 'Send'}
            </button>
            <button type="button" onClick={toggleRecording} className="record-button">
              {isRecording ? 'Stop Recording' : 'Start Recording'}
            </button>
          </div>
        </form>
      </div>
      <button 
        className="chat-history-toggle" 
        onClick={toggleChatHistory}
      >
        {isChatHistoryOpen ? 'Close History' : 'Chat History'}
      </button>
    </div>
  )
}

export default App