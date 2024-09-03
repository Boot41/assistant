import { useState, useCallback, useEffect } from 'react';
import './App.css';

import JarvisContainer from './components/JarvisContainer';
import ChatInterface from './components/ChatInterface';
import ChatHistory from './components/ChatHistory';
import ChatHistoryToggle from './components/ChatHistoryToggle';
import { useChat } from './hooks/useChat';
import TourGuide from './components/TourGuide';
import YouTubeModal from './components/YouTubeModal';
import VoiceSelector from './components/VoiceSelector';

function App() {
  const { 
    chatHistory, 
    isSpeaking, 
    userInput, 
    setUserInput, 
    handleSend, 
    isLoading, 
    currentPage, 
    setCurrentPage, 
    isTourStarted, 
    setIsTourStarted, 
    tourSteps, 
    youtubeVideoUrl, 
    setYoutubeVideoUrl, 
    isYoutubeModalOpen, 
    setIsYoutubeModalOpen, 
    voices, 
    selectedVoice, 
    setSelectedVoice,
    presentationData,
    isPresentationModalOpen,
    setIsPresentationModalOpen
  } = useChat();
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
      <div className="header">
        <VoiceSelector
          voices={voices}
          selectedVoice={selectedVoice}
          setSelectedVoice={setSelectedVoice}
        />
      </div>
      <div className="content-wrapper">
        <JarvisContainer 
          isSpeaking={isSpeaking} 
          isRecording={isRecording}
          presentationData={presentationData}
          isPresentationModalOpen={isPresentationModalOpen}
          setIsPresentationModalOpen={setIsPresentationModalOpen}
        />
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
      <YouTubeModal
        videoUrl={youtubeVideoUrl}
        isOpen={isYoutubeModalOpen}
        onClose={() => {
          setIsYoutubeModalOpen(false);
          setYoutubeVideoUrl(null);
        }}
      />
    </div>
  );
}

export default App;