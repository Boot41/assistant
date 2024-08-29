import React from 'react';
import { motion } from 'framer-motion';

function ChatHistory({ chatHistory, isOpen }) {
  return (
    <motion.div
      className={`chat-history-sidebar ${isOpen ? '' : 'closed'}`}
      initial={{ x: '100%' }}
      animate={{ x: isOpen ? 0 : '100%' }}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
    >
      <div className="chat-history-container">
        {chatHistory.map((message, index) => (
          <motion.div
            key={index}
            className={`chat-message ${message.role}`}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <strong>{message.role === 'user' ? 'You' : 'Assistant'}</strong>
            <p>{message.content}</p>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}

export default ChatHistory;
