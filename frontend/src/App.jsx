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
import StopSpeakingButton from './components/StopSpeakingButton';
import TranscriptView from './components/TranscriptView';

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
    stopSpeaking,
    transcript,
    setSearchTerm,
    setStartDate,
    setEndDate,
    exportTranscript
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
        <TranscriptView
          transcript={transcript}
          setSearchTerm={setSearchTerm}
          setStartDate={setStartDate}
          setEndDate={setEndDate}
          exportTranscript={exportTranscript}
        />
        <StopSpeakingButton isSpeaking={isSpeaking} stopSpeaking={stopSpeaking} />
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