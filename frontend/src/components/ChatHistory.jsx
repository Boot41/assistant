import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import DOMPurify from 'dompurify';
import PropTypes from 'prop-types';

function ChatHistory({ chatHistory, isOpen, isLoading }) {
  const chatContainerRef = useRef(null);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTo({
        top: chatContainerRef.current.scrollHeight,
        behavior: 'smooth'
      });
    }
  }, [chatHistory]);

  const formatMessage = (content) => {
    content = content.replace(/(?<=^|[.!?]\s+)[a-z]/g, (c) => c.toUpperCase());
    content = content.replace(/([.!?,;:])(?=\S)/g, '$1 ');
    content = content.replace(/\s+/g, ' ');
    return content;
  };

  const sanitizeAndCreateLinks = (content) => {
    content = formatMessage(content);
    const linkedInRegex = /\[([^\]]+)\]\((https:\/\/www\.linkedin\.com\/[^)]+)\)/g;
    let contentWithLinks = content.replace(linkedInRegex, '<a href="$2" target="_blank" rel="noopener noreferrer" class="linkedin-link">$1</a>');
    contentWithLinks = contentWithLinks.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    const sanitizedContent = DOMPurify.sanitize(contentWithLinks, { ADD_ATTR: ['target'] });
    return { __html: sanitizedContent };
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return isNaN(date.getTime()) ? '' : date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <motion.div
      className={`chat-history-sidebar ${isOpen ? 'open' : 'closed'}`}
      initial={{ x: '100%' }}
      animate={{ x: isOpen ? 0 : '100%' }}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
    >
      <div className="chat-history-header">Chat History</div>
      <div className="chat-history-container" ref={chatContainerRef}>
        <AnimatePresence>
          {chatHistory.map((message, index) => (
            <motion.div
              key={index}
              className={`message-group ${message.role}`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <div className="message-avatar">
                {message.role === 'user' ? '👤' : '🤖'}
              </div>
              <div className="message-content-wrapper">
                <div 
                  className="message-content"
                  dangerouslySetInnerHTML={sanitizeAndCreateLinks(message.content)}
                />
                <div className="message-metadata">
                  <span className="message-timestamp">
                    {formatTimestamp(message.timestamp)}
                  </span>
                  {message.role === 'assistant' && <span className="read-receipt">✓✓</span>}
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        {isLoading && (
          <div className="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        )}
      </div>
    </motion.div>
  );
}

ChatHistory.propTypes = {
  chatHistory: PropTypes.arrayOf(PropTypes.shape({
    role: PropTypes.string.isRequired,
    content: PropTypes.string.isRequired,
    timestamp: PropTypes.string,
  })).isRequired,
  isOpen: PropTypes.bool.isRequired,
  isLoading: PropTypes.bool,
};

ChatHistory.defaultProps = {
  isLoading: false,
};

export default ChatHistory;
