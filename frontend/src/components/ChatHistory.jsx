import React from 'react';

function ChatHistory({ chatHistory, isOpen }) {
  console.log("ChatHistory rendered. isOpen:", isOpen, "chatHistory length:", chatHistory.length);

  if (!isOpen) return null;

  return (
    <div className="chat-history-sidebar p-10">
      <div className="chat-history-container">
        {chatHistory.map((message, index) => (
          <div key={index} className={`chat-message ${message.role}`}>
            <strong>{message.role === 'user' ? 'You' : 'Assistant'}</strong>
            <p>{message.content}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ChatHistory;
