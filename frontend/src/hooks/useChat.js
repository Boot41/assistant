import { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import { useTranscript } from './useTranscript';

export function useChat() {
  const [userInput, setUserInput] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [youtubeVideoUrl, setYoutubeVideoUrl] = useState(null);
  const [isYoutubeModalOpen, setIsYoutubeModalOpen] = useState(false);
  const [voices, setVoices] = useState([]);
  const [selectedVoice, setSelectedVoice] = useState(null);
  const speechSynthesisRef = useRef(window.speechSynthesis);
  const stopSpeakingRef = useRef(null);
  const { transcript, addToTranscript, clearTranscript, getTranscriptAsJSON, setSearchTerm, setStartDate, setEndDate, exportTranscript, getRecentContext } = useTranscript();
  const [conversationHistory, setConversationHistory] = useState([]);

  const stopSpeaking = useCallback(() => {
    if (stopSpeakingRef.current) {
      stopSpeakingRef.current();
    }
  }, []);

  useEffect(() => {
    setChatHistory([{ role: 'assistant', content: "Hello! I'm Echo, your AI assistant. How can I help you today?" }]);

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

  const getAIResponse = useCallback(async (prompt) => {
    try {
      const response = await axios.post('http://localhost:8000/api/chat/', {
        user_input: prompt
      });
      return response.data.response;
    } catch (error) {
      console.error('Error getting AI response:', error);
      return 'I apologize, but I encountered an error. Could you please try again?';
    }
  }, []);

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
    text = text.replace(/[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F1E0}-\u{1F1FF}]/gu, '');
    text = text.replace(/\[([^\]]+)\]\([^\)]+\)/g, '$1');
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

  const handleSend = useCallback(async () => {
    if (userInput.trim() === '') return;

    setIsLoading(true);
    const newUserMessage = { role: 'user', content: userInput };
    setChatHistory(prevHistory => [...prevHistory, newUserMessage]);
    setConversationHistory(prevHistory => [...prevHistory, newUserMessage]);

    try {
      if (userInput.toLowerCase().includes('youtube')) {
        const youtubeResponse = await handleYouTubeCommand(userInput);
        const newAssistantMessage = { role: 'assistant', content: youtubeResponse };
        setChatHistory(prevHistory => [...prevHistory, newAssistantMessage]);
        setConversationHistory(prevHistory => [...prevHistory, newAssistantMessage]);
        addToTranscript('Assistant', youtubeResponse, Date.now());
        speakResponse(youtubeResponse);
      } else {
        const response = await axios.post('http://localhost:8000/api/chat/', {
          user_input: userInput,
          context: conversationHistory.slice(-5) // Get last 5 messages for context
        });

        const newAssistantMessage = { role: 'assistant', content: response.data.response };
        setChatHistory(prevHistory => [...prevHistory, newAssistantMessage]);
        setConversationHistory(prevHistory => [...prevHistory, newAssistantMessage]);
        addToTranscript('Assistant', response.data.response, Date.now());
        speakResponse(response.data.response);
      }

      setUserInput('');
    } catch (error) {
      console.error('Error sending message:', error);
      setChatHistory(prevHistory => [...prevHistory, { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' }]);
      addToTranscript('Assistant', 'Sorry, I encountered an error. Please try again.', Date.now());
    } finally {
      setIsLoading(false);
    }
  }, [userInput, addToTranscript, speakResponse,conversationHistory]);

  const handleYouTubeCommand = async (input) => {
    try {
      const response = await axios.post('http://localhost:8000/api/youtube/', {
        query: input
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
    conversationHistory,
  };
}