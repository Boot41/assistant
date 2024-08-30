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
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        width: '500px', // Increased width to 350px
        backgroundColor: '#1e1e1e',
        color: '#ffffff'
      }}
    >
      <div className="chat-history-header" style={{ padding: '10px', borderBottom: '1px solid #333' }}>Chat History</div>
      <div 
        className="chat-history-container" 
        ref={chatContainerRef}
        style={{ 
          padding: '15px', 
          overflowY: 'auto', 
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          gap: '12px'
        }}
      >
        <AnimatePresence>
          {chatHistory.map((message, index) => (
            <motion.div
              key={index}
              className={`message-group ${message.role}`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              style={{ 
                padding: '10px', 
                backgroundColor: message.role === 'user' ? '#2c2c2c' : '#3a3a3a',
                color: '#ffffff',
                borderRadius: "10px",
                marginLeft: "30px",
                maxWidth: '100%',
                wordWrap: 'break-word',
                fontSize: '0.95em',
                boxShadow: '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)'
              }}
            >
              <div className="message-content-wrapper">
                <div 
                  className="message-content"
                  dangerouslySetInnerHTML={sanitizeAndCreateLinks(message.content)}
                />
                <div className="message-metadata" style={{ marginTop: '5px', fontSize: '0.8em', color: '#aaa' }}>
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
n