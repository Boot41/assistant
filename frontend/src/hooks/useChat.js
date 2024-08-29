import { useState, useEffect } from 'react';
import axios from 'axios';

export function useChat() {
  const [currentPage, setCurrentPage] = useState('Exploring our services');
  const [userInput, setUserInput] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);

  useEffect(() => {
    setChatHistory([{ role: 'assistant', content: "Hello! I'm Jarvis, your AI assistant. How can I help you today?" }]);
  }, []);

  const handleSend = async () => {
    if (userInput.trim() === '') return;

    setIsLoading(true);
    const newMessage = { role: 'user', content: userInput };
    setChatHistory(prevHistory => [...prevHistory, newMessage]);

    try {
      const response = await axios.post('http://localhost:8000/api/chat/', {
        user_input: userInput,
        current_page: currentPage
      });

      setChatHistory(prevHistory => [...prevHistory, { role: 'assistant', content: response.data.response }]);
      speakResponse(response.data.response);

      setUserInput('');
    } catch (error) {
      console.error('Error sending message:', error);
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

  return {
    chatHistory,
    isSpeaking,
    userInput,
    setUserInput,
    handleSend,
    isLoading,
    currentPage,
    setCurrentPage
  };
}