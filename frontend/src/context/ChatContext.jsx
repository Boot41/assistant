import React, { createContext, useState, useContext } from 'react';
import { useChatInteraction } from '../hooks/useChatInteraction';

const ChatContext = createContext();

export const ChatProvider = ({ children }) => {
  const chatInteraction = useChatInteraction();

  return (
    <ChatContext.Provider value={chatInteraction}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => useContext(ChatContext);