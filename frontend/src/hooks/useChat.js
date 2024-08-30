import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

export function useChat() {
  const [currentPage, setCurrentPage] = useState(null);
  const [userInput, setUserInput] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isTourStarted, setIsTourStarted] = useState(false);

  const [tourSteps, setTourSteps] = useState([]);

  useEffect(() => {
    setChatHistory([{ role: 'assistant', content: "Hello! I'm Echo, your AI assistant. How can I help you today?" }]);
    fetchInitialPage();
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

  const getAIResponse = async (prompt) => {
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
  };

  const speakResponse = (text) => {
    if ('speechSynthesis' in window) {
      // Clear any existing speech synthesis
      speechSynthesis.cancel();

      // Split text into chunks of around 200 characters, preserving whole words
      const chunks = text.match(/\S.{1,199}(?!\S)/g) || [];

      let currentChunk = 0;

      const speakNextChunk = () => {
        if (currentChunk < chunks.length) {
          const utterance = new SpeechSynthesisUtterance(chunks[currentChunk]);
          utterance.rate = 1.2; // Increase speed (1.0 is normal speed)
          
          if (currentChunk === 0) {
            utterance.onstart = () => setIsSpeaking(true);
          }

          utterance.onend = () => {
            currentChunk++;
            if (currentChunk < chunks.length) {
              speakNextChunk();
            } else {
              setIsSpeaking(false);
            }
          };

          speechSynthesis.speak(utterance);
        }
      };

      speakNextChunk();
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

    try {
      const tourCommand = checkForTourCommands(userInput);
      if (tourCommand === 'start') {
        await startTour();
      } else if (tourCommand === 'next') {
        await handleNextStep();
      } else {
        const response = await axios.post('http://localhost:8000/api/chat/', {
          user_input: userInput,
          current_page: currentPage || 'home',
          is_tour_started: isTourStarted
        });

        const newAssistantMessage = { role: 'assistant', content: response.data.response };
        setChatHistory(prevHistory => [...prevHistory, newAssistantMessage]);
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
    } finally {
      setIsLoading(false);
    }
  }, [userInput, currentPage, isTourStarted, checkForTourCommands, startTour, handleNextStep]);

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
    navigateToNextPage
  };
}