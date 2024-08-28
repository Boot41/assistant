import React, { useEffect, useRef } from 'react';
import { useChat } from '../context/ChatContext';
import '../styles/ChatHistory.css';

const ChatHistory = () => {
  const { chatHistory } = useChat();
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  return (
    <div className="chat-history">
      {chatHistory.map((message, index) => (
        <div key={index} className={`message ${message.role}`}>
          {message.content}
        </div>
      ))}
      <div ref={chatEndRef} />
    </div>
  );
};

export default ChatHistory;