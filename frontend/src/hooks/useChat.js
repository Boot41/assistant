import { useState, useEffect } from 'react';
import axios from 'axios';

export const useChat = () => {
  const [userInput, setUserInput] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);

  useEffect(() => {
    setChatHistory([{ role: 'assistant', content: "Hello! I'm Jarvis, your AI assistant. How can I help you today?" }]);
  }, []);

  const handleSend = async () => {
    if (!userInput.trim()) return;

    try {
      setIsLoading(true);
      setChatHistory(prevHistory => [...prevHistory, { role: 'user', content: userInput }]);
      
      const response = await axios.post('http://localhost:8000/api/chat/', { user_input: userInput });
      
      setChatHistory(prevHistory => [...prevHistory, { role: 'assistant', content: response.data.response }]);
      speakResponse(response.data.response);

      setUserInput('');
    } catch (error) {
      console.error('Error processing interaction:', error);
      setChatHistory(prevHistory => [...prevHistory, { role: 'assistant', content: "I'm sorry, I encountered an error. Could you please try again?" }]);
    } finally {
      setIsLoading(false);
    }
  };

  const speakResponse = (text) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);
      speechSynthesis.speak(utterance);
    }
  };

  return { userInput, setUserInput, chatHistory, isLoading, isSpeaking, handleSend, speakResponse };
};