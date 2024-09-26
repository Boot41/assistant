import { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import { useTranscript } from './useTranscript';

export function useChat() {
  const [currentPage, setCurrentPage] = useState(null);
  const [userInput, setUserInput] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isTourStarted, setIsTourStarted] = useState(false);

  const [tourSteps, setTourSteps] = useState([]);

  const [youtubeVideoUrl, setYoutubeVideoUrl] = useState(null);
  const [isYoutubeModalOpen, setIsYoutubeModalOpen] = useState(false);

  const [voices, setVoices] = useState([]);
  const [selectedVoice, setSelectedVoice] = useState(null);
  const speechSynthesisRef = useRef(window.speechSynthesis);
  const stopSpeakingRef = useRef(null);

  const { transcript, addToTranscript, clearTranscript, getTranscriptAsJSON, setSearchTerm, setStartDate, setEndDate, exportTranscript } = useTranscript();

  const stopSpeaking = useCallback(() => {
    if (stopSpeakingRef.current) {
      stopSpeakingRef.current();
    }
  }, []);

  useEffect(() => {
    setChatHistory([{ role: 'assistant', content: "Hello! I'm Echo, your AI assistant. How can I help you today?" }]);
    fetchInitialPage();

    const loadVoices = () => {
      const availableVoices = speechSynthesisRef.current.getVoices();
      setVoices(availableVoices);
      const preferredVoice = availableVoices.find(voice => voice.name === 'Google UK English Female') ||
                             availableVoices.find(voice => voice.lang === 'en-GB') ||
                             availableVoices[0];
      setSelectedVoice(preferredVoice);
    };

    loadVoices();
    if (speechSynthesisRef.current.onvoiceschanged !== undefined) {
      speechSynthesisRef.current.onvoiceschanged = loadVoices;
    }
  }, []);

  const fetchInitialPage = useCallback(async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/initial-page/');
      console.log('Initial page response:', response.data);
      setCurrentPage(response.data.initial_page || 'home');
    } catch (error) {
      console.error('Error fetching initial page:', error);
      setCurrentPage('home');
    }
  }, []);

  const getAIResponse = useCallback(async (prompt) => {
    try {
      const response = await axios.post('http://localhost:8000/api/chat/', {
        user_input: prompt,
        current_page: currentPage || 'home',
        is_tour_started: isTourStarted
      });
      return response.data.response;
    } catch (error) {
      console.error('Error getting AI response:', error);
      return 'I apologize, but I encountered an error. Could you please try again?';
    }
  }, [currentPage, isTourStarted]);

  const speakResponse = useCallback((text) => {
    if (speechSynthesisRef.current) {
      speechSynthesisRef.current.cancel();

      const processedText = preprocessTextForSpeech(text);
      const sentences = processedText.split(/(?<=[.!?])\s+/);

      let currentSentence = 0;
      let isStopped = false;

      stopSpeakingRef.current = () => {
        isStopped = true;
        speechSynthesisRef.current.cancel();
        setIsSpeaking(false);
      };

      const speakNextSentence = () => {
        if (isStopped) return;

        if (currentSentence < sentences.length) {
          const utterance = new SpeechSynthesisUtterance(sentences[currentSentence]);
          
          utterance.voice = selectedVoice;
          utterance.rate = 0.9 + (Math.random() * 0.2);
          utterance.pitch = 1 + (Math.random() * 0.1 - 0.05);

          if (currentSentence === 0) {
            utterance.onstart = () => setIsSpeaking(true);
          }

          utterance.onend = () => {
            currentSentence++;
            if (currentSentence < sentences.length) {
              const pauseLength = getPauseLength(sentences[currentSentence - 1]);
              setTimeout(speakNextSentence, pauseLength);
            } else {
              setIsSpeaking(false);
            }
          };

          speechSynthesisRef.current.speak(utterance);
        }
      };

      speakNextSentence();
    }
  }, [selectedVoice]);

  const preprocessTextForSpeech = (text) => {
    // Remove emojis
    text = text.replace(/[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F1E0}-\u{1F1FF}]/gu, '');
    
    // Remove markdown links
    text = text.replace(/\[([^\]]+)\]\([^\)]+\)/g, '$1');
    
    // Remove extra spaces
    text = text.replace(/\s+/g, ' ').trim();
    
    return text;
  };

  const getPauseLength = (sentence) => {
    if (sentence.endsWith('?')) {
      return 500 + Math.random() * 300;
    } else if (sentence.endsWith('!')) {
      return 400 + Math.random() * 200;
    } else {
      return 300 + Math.random() * 200;
    }
  };

  const navigateToNextPage = useCallback(async () => {
    try {
      const response = await axios.post('http://localhost:8000/api/tour/navigate/', {
        current_page: currentPage
      });
      return response.data;
    } catch (error) {
      console.error('Error navigating to next page:', error);
      throw error;
    }
  }, [currentPage]);

  const handleStartTour = useCallback(async () => {
    try {
      const startPrompt = "The user has just started a tour of Think41. Give an enthusiastic greeting and briefly mention what the tour will cover.";
      const startMessage = await getAIResponse(startPrompt);
      setChatHistory(prevHistory => [
        ...prevHistory,
        { role: 'user', content: 'Start the tour' },
        { role: 'assistant', content: startMessage }
      ]);
      speakResponse(startMessage);
    } catch (error) {
      console.error('Error starting tour:', error);
      const errorMessage = await getAIResponse("There was an error starting the tour. Provide an apologetic response and suggest trying again.");
      setChatHistory(prevHistory => [...prevHistory, { role: 'assistant', content: errorMessage }]);
    }
  }, []);

  const handleNextStep = useCallback(async () => {
    try {
      const nextPageData = await navigateToNextPage();
      if (nextPageData.current_step) {
        setCurrentPage(nextPageData.current_step.page_name);
        const nextStepPrompt = `The user wants to move to the next step of the tour. The next step is about ${nextPageData.current_step.title}. Provide an enthusiastic response and briefly introduce this step.`;
        const nextStepMessage = await getAIResponse(nextStepPrompt);
        setChatHistory(prevHistory => [
          ...prevHistory,
          { role: 'user', content: 'Next step' },
          { role: 'assistant', content: nextStepMessage }
        ]);
        speakResponse(nextStepMessage);
      } else {
        const endTourPrompt = "We've reached the end of the tour. Provide a concluding message and ask if the user has any questions.";
        const endTourMessage = await getAIResponse(endTourPrompt);
        setChatHistory(prevHistory => [
          ...prevHistory,
          { role: 'user', content: 'Next step' },
          { role: 'assistant', content: endTourMessage }
        ]);
        speakResponse(endTourMessage);
      }
    } catch (error) {
      console.error('Error navigating to next step:', error);
      const errorMessage = await getAIResponse("There was an error moving to the next step. Provide an apologetic response and suggest trying again.");
      setChatHistory(prevHistory => [...prevHistory, { role: 'assistant', content: errorMessage }]);
    }
  }, [navigateToNextPage, getAIResponse, speakResponse]);

  const startTour = useCallback(async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/tour-steps/');
      setTourSteps(response.data);
      setIsTourStarted(true);
      console.log("Tour started, steps fetched:", response.data);
      await handleStartTour();
    } catch (error) {
      console.error('Error fetching tour steps:', error);
    }
  }, [handleStartTour]);

  const checkForTourCommands = useCallback((input) => {
    const lowerInput = input.toLowerCase().trim();
    if (lowerInput.includes('start') && lowerInput.includes('tour')) {
      return 'start';
    }
    if (isTourStarted && (lowerInput.includes('next') || lowerInput.includes('continue'))) {
      return 'next';
    }
    return null;
  }, [isTourStarted]);

  const handleSend = useCallback(async () => {
    if (userInput.trim() === '') return;

    setIsLoading(true);
    const newUserMessage = { role: 'user', content: userInput };
    setChatHistory(prevHistory => [...prevHistory, newUserMessage]);
    addToTranscript('User', userInput, Date.now());

    try {
      const tourCommand = checkForTourCommands(userInput);
      if (tourCommand === 'start') {
        await startTour();
      } else if (tourCommand === 'next') {
        await handleNextStep();
      } else if (userInput.toLowerCase().includes('youtube')) {
        const youtubeResponse = await handleYouTubeCommand(userInput);
        const newAssistantMessage = { role: 'assistant', content: youtubeResponse };
        setChatHistory(prevHistory => [...prevHistory, newAssistantMessage]);
        addToTranscript('Assistant', youtubeResponse, Date.now());
        speakResponse(youtubeResponse);
      } else {
        const response = await axios.post('http://localhost:8000/api/chat/', {
          user_input: userInput,
          current_page: currentPage || 'home',
          is_tour_started: isTourStarted
        });

        const newAssistantMessage = { role: 'assistant', content: response.data.response };
        setChatHistory(prevHistory => [...prevHistory, newAssistantMessage]);
        addToTranscript('Assistant', response.data.response, Date.now());
        speakResponse(response.data.response);

        if (response.data.current_page && response.data.current_page !== currentPage) {
          setCurrentPage(response.data.current_page);
        }

        if (response.data.is_tour_started !== undefined) {
          setIsTourStarted(response.data.is_tour_started);
        }
      }

      setUserInput('');
    } catch (error) {
      console.error('Error sending message:', error);
      setChatHistory(prevHistory => [...prevHistory, { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' }]);
      addToTranscript('Assistant', 'Sorry, I encountered an error. Please try again.', Date.now());
    } finally {
      setIsLoading(false);
    }
  }, [userInput, currentPage, isTourStarted, checkForTourCommands, startTour, handleNextStep, addToTranscript]);

  const handleYouTubeCommand = async (input) => {
    try {
      const response = await axios.post('http://localhost:8000/api/youtube/', {
        query: input  // Change 'user_input' to 'query'
      });
      console.log('YouTube URL:', response.data.youtube_url);
      setYoutubeVideoUrl(response.data.youtube_url);
      setIsYoutubeModalOpen(true);
      return `I've found a video for "${response.data.search_term}". It's now playing in a popup window.`;
    } catch (error) {
      console.error('Error handling YouTube command:', error);
      return 'Sorry, I encountered an error while processing your YouTube request.';
    }
  };

  return {
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
    startTour,
    navigateToNextPage,
    youtubeVideoUrl,
    setYoutubeVideoUrl,
    isYoutubeModalOpen,
    setIsYoutubeModalOpen,
    voices,
    selectedVoice,
    setSelectedVoice,
    stopSpeaking,
    transcript,
    clearTranscript,
    getTranscriptAsJSON,
    setSearchTerm,
    setStartDate,
    setEndDate,
    exportTranscript,
  };
}