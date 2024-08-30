import { useState, useCallback, useEffect } from 'react';
import './App.css';
import JarvisContainer from './components/JarvisContainer';
import ChatInterface from './components/ChatInterface';
import ChatHistory from './components/ChatHistory';
import ChatHistoryToggle from './components/ChatHistoryToggle';
import { useChat } from './hooks/useChat';
import TourGuide from './components/TourGuide';

function App() {
  const { chatHistory, isSpeaking, userInput, setUserInput, handleSend, isLoading, currentPage, setCurrentPage, isTourStarted, setIsTourStarted, tourSteps } = useChat();
  const [isChatHistoryOpen, setIsChatHistoryOpen] = useState(false);
  const [isRecording, setIsRecording] = useState(false);

  const toggleChatHistory = useCallback(() => {
    setIsChatHistoryOpen(prev => !prev);
  }, []);

  useEffect(() => {
    console.log("Tour started:", isTourStarted);  // Debug log
  }, [isTourStarted]);

  return (
    <div className="app-container">
      <div className="content-wrapper">
        <JarvisContainer isSpeaking={isSpeaking} isRecording={isRecording} />
        <ChatHistory chatHistory={chatHistory} isOpen={isChatHistoryOpen} isLoading={isLoading} />
        {currentPage && (
          <TourGuide
            currentPage={currentPage}
            setCurrentPage={setCurrentPage}
            isTourStarted={isTourStarted}
            setIsTourStarted={setIsTourStarted}
            tourSteps={tourSteps}
          />
        )}
      </div>
      <ChatInterface 
        userInput={userInput}
        setUserInput={setUserInput}
        handleSend={handleSend}
        isLoading={isLoading}
        isRecording={isRecording}
        setIsRecording={setIsRecording}
        currentPage={currentPage}
      />
      <ChatHistoryToggle 
        isOpen={isChatHistoryOpen} 
        toggleChatHistory={toggleChatHistory} 
      />
    </div>
  );
}

export default App;