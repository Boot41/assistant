import { useState } from 'react';
import axios from 'axios';

export const useChatInteraction = () => {
  const [userInput, setUserInput] = useState('');
  const [chatHistory, setChatHistory] = useState([]);

  const handleSend = async () => {
    if (!userInput.trim()) return;

    try {
      setChatHistory(prev => [...prev, { role: 'user', content: userInput }]);
      const response = await axios.post('http://localhost:8000/api/chat/', { user_input: userInput });
      setChatHistory(prev => [...prev, { role: 'assistant', content: response.data.response }]);
      setUserInput('');
    } catch (error) {
      console.error('Error sending message:', error);
      setChatHistory(prev => [...prev, { role: 'assistant', content: "I'm sorry, I encountered an error. Please try again." }]);
    }
  };

  return { userInput, setUserInput, chatHistory, handleSend };
};