import React from 'react';

function ChatHistoryToggle({ isOpen, toggleChatHistory }) {
  return (
    <button 
      className="chat-history-toggle" 
      onClick={toggleChatHistory}
    >
      {isOpen ? 'Close History' : 'Chat History'}
    </button>
  );
}

export default ChatHistoryToggle;