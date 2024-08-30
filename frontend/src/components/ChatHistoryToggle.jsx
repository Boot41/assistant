import React from 'react';
import PropTypes from 'prop-types';

function ChatHistoryToggle({ isOpen, toggleChatHistory }) {
  return (
    <button 
      className={`chat-history-toggle ${isOpen ? 'open' : ''}`}
      onClick={toggleChatHistory}
      aria-label={isOpen ? 'Close Chat History' : 'Open Chat History'}
    >
      <span className="toggle-icon">{isOpen ? '×' : '☰'}</span>
      <span className="toggle-text">{isOpen ? 'Close History' : 'Chat History'}</span>
    </button>
  );
}

ChatHistoryToggle.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  toggleChatHistory: PropTypes.func.isRequired,
};

export default ChatHistoryToggle;