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
      // Clear any existing speech synthesis
      speechSynthesis.cancel();

      // Split text into chunks of around 200 characters, preserving whole words
      const chunks = text.match(/\S.{1,199}(?!\S)/g) || [];

      let currentChunk = 0;

      const speakNextChunk = () => {
        if (currentChunk < chunks.length) {
          const utterance = new SpeechSynthesisUtterance(chunks[currentChunk]);
          utterance.rate = 1.2; // Increase speed (1.0 is normal speed)
          
          if (currentChunk === 0) {
            utterance.onstart = () => setIsSpeaking(true);
          }

          utterance.onend = () => {
            currentChunk++;
            if (currentChunk < chunks.length) {
              speakNextChunk();
            } else {
              setIsSpeaking(false);
            }
          };

          speechSynthesis.speak(utterance);
        }
      };

      speakNextChunk();
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