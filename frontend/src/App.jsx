import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import './App.css'
import gsap from 'gsap';

function App() {
  const appStyle = {
    color: '#ffffff'  // White text for better contrast on dark background
  };

  const tourTextStyle = {
    color: '#4da6ff'  // Lighter blue color for better visibility
  };

  const chatStyle = {
    color: '#000000'  // Black text for chat messages (assuming light background)
  };

  const [tourStep, setTourStep] = useState(null)
  const [userInput, setUserInput] = useState('')
  const [chatHistory, setChatHistory] = useState([])
  const [currentPage, setCurrentPage] = useState('Home')
  const [mediaContent, setMediaContent] = useState(null)
  const [tourProgress, setTourProgress] = useState(0)
  const [allTourSteps, setAllTourSteps] = useState([])
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [quizActive, setQuizActive] = useState(false)
  const [quizQuestion, setQuizQuestion] = useState(null)
  const [error, setError] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const inputRef = useRef(null)

  useEffect(() => {
    getTourProgress()
    getAllTourSteps()
    startTour()  // Add this line if you want the tour to start automatically
  }, [])

  const getAllTourSteps = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/tour/steps/')
      setAllTourSteps(res.data)
      if (res.data.length === 0) {
        setError('No tour steps available. Please add some tour steps.')
      }
    } catch (error) {
      console.error('Error getting tour steps:', error.response?.data || error.message)
      setError('Failed to fetch tour steps. Please try again.')
    }
  }

  const getTourProgress = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/tour/progress/', { params: { user_id: 'test_user' } })
      if (res.data.current_step && res.data.progress_percentage !== undefined) {
        setTourStep(res.data.current_step)
        setTourProgress(res.data.progress_percentage)
      } else if (res.data.total_steps === 0) {
        setError(res.data.message || 'No tour steps available. Please add some tour steps.')
      } else {
        console.error('Invalid response format for tour progress')
        setError('Failed to fetch tour progress. Please try again.')
      }
    } catch (error) {
      console.error('Error getting tour progress:', error.response?.data || error.message)
      setError(error.response?.data?.message || 'Failed to fetch tour progress. Please try again.')
    }
  }

  const handleUserInput = async (e) => {
    e.preventDefault();
    if (!userInput.trim()) return;

    try {
      setIsLoading(true);
      const res = await axios.post('http://localhost:8000/api/tour-guide/', {
        user_id: 'test_user',
        user_input: userInput,
        current_page: currentPage,
        current_step: tourStep ? tourStep.order : null
      });
      setChatHistory(prevHistory => [...prevHistory, 
        { role: 'user', content: userInput },
        { role: 'assistant', content: res.data.response }
      ]);
      handleActions(res.data.actions);

      // Check if the user input contains a navigation request
      const navigationMatch = userInput.match(/navigate to (\w+)/i);
      if (navigationMatch) {
        const pageName = navigationMatch[1];
        await navigateToPage(pageName);
      }

      setUserInput('');
      // Safely focus the input
      if (inputRef.current) {
        inputRef.current.focus();
      }
    } catch (error) {
      console.error('Error processing interaction:', error);
      setError('Failed to process your input. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const navigateToPage = async (pageName) => {
    try {
      const res = await axios.post('http://localhost:8000/api/tour/navigate/', {
        user_id: 'test_user',
        page_name: pageName
      });
      if (res.data.current_step) {
        setTourStep(res.data.current_step);
        setCurrentPage(res.data.current_step.page_name);
        setTourProgress(res.data.progress_percentage);
      }
    } catch (error) {
      console.error('Error navigating to page:', error);
      setError('Failed to navigate to the requested page. Please try again.');
    }
  };

  const startTour = async () => {
    setIsLoading(true);
    try {
      const res = await axios.post('http://localhost:8000/api/tour/start/', { user_id: 'test_user' });
      if (res.data.tour_started) {
        setTourStep(res.data.current_step);
        setCurrentPage(res.data.current_step.page_name);
        setTourProgress(0);
        setChatHistory([]);
      } else {
        setError(res.data.message || 'Failed to start the tour. Please try again.');
      }
    } catch (error) {
      console.error('Error starting tour:', error.response?.data || error.message);
      setError(error.response?.data?.message || 'Failed to start the tour. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const goToStep = async (stepOrder) => {
    try {
      const res = await axios.post('http://localhost:8000/api/tour/go-to-step/', { 
        user_id: 'test_user',
        step_order: stepOrder
      })
      setTourStep(res.data.current_step)
      setCurrentPage(res.data.current_step.page_name)
      setTourProgress(res.data.progress_percentage)
    } catch (error) {
      console.error('Error going to step:', error)
    }
  }

  const nextTourStep = async () => {
    try {
      const res = await axios.post('http://localhost:8000/api/tour/next/', { user_id: 'test_user' })
      if (res.data.message === "Tour completed") {
        setChatHistory(prevHistory => [...prevHistory, 
          { role: 'assistant', content: "Tour completed! Feel free to ask any questions." }
        ])
        setTourStep(null)
        setTourProgress(100)
      } else if (res.data.current_step) {
        setTourStep(res.data.current_step)
        setCurrentPage(res.data.current_step.page_name)
        setTourProgress(res.data.progress_percentage)
        speak(res.data.current_step.description)
        
        // Update chat history with the new step information
        setChatHistory(prevHistory => [...prevHistory, 
          { role: 'assistant', content: `Welcome to ${res.data.current_step.page_name}: ${res.data.current_step.title}\n\n${res.data.current_step.description}` }
        ])

        if (res.data.quiz_question) {
          setQuizQuestion(res.data.quiz_question)
          setQuizActive(true)
        } else {
          setQuizQuestion(null)
          setQuizActive(false)
        }
      } else {
        console.error('Invalid response format for next tour step')
        setError('Failed to fetch the next tour step. Please try again.')
      }
    } catch (error) {
      console.error('Error getting next step:', error.response?.data?.error || error.message)
      setError('Failed to fetch the next tour step. Please try again.')
    }
  }

  const prevTourStep = async () => {
    try {
      const res = await axios.post('http://localhost:8000/api/tour/previous/', { user_id: 'test_user' });
      if (res.data.current_step) {
        setTourStep(res.data.current_step);
        setCurrentPage(res.data.current_step.page_name);
        setTourProgress(res.data.progress_percentage);
        speak(res.data.current_step.description);
      } else if (res.data.message === "No previous step") {
        setError('You are at the beginning of the tour.');
      } else {
        console.error('Invalid response format for previous tour step');
        setError('Failed to fetch the previous tour step. Please try again.');
      }
    } catch (error) {
      if (error.response && error.response.status === 404) {
        console.error('Previous step endpoint not found. Ensure it is implemented on the backend.');
        setError('Previous step functionality is not available.');
      } else {
        console.error('Error getting previous step:', error.response?.data?.error || error.message);
        setError('Failed to fetch the previous tour step. Please try again.');
      }
    }
  };

  const handleQuizAnswer = async (answer) => {
    try {
      const res = await axios.post('http://localhost:8000/api/tour/quiz-answer/', {
        user_id: 'test_user',
        question_id: quizQuestion.id,
        answer: answer
      })
      setChatHistory(prevHistory => [...prevHistory,
        { role: 'assistant', content: res.data.feedback }
      ])
      setQuizActive(false)
      setQuizQuestion(null)
    } catch (error) {
      console.error('Error submitting quiz answer:', error)
    }
  }

  const handleActions = (actions) => {
    actions.forEach(action => {
      switch (action.type) {
        case 'navigate':
          navigateToPage(action.target);
          break;
        case 'show_video':
        case 'show_image':
          setMediaContent(action.content);
          break;
        default:
          console.log('Unknown action:', action);
      }
    });
  }

  const speak = (text) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text)
      speechSynthesis.speak(utterance)
      setIsSpeaking(true)
      utterance.onend = () => setIsSpeaking(false)
    }
  }

  useEffect(() => {
    const handleKeyPress = (event) => {
      if (event.key === 'ArrowRight') {
        nextTourStep()
      } else if (event.key === 'ArrowLeft') {
        prevTourStep()
      }
    }
    window.addEventListener('keydown', handleKeyPress)
    return () => {
      window.removeEventListener('keydown', handleKeyPress)
    }
  }, [])

  useEffect(() => {
    if (chatHistory.length > 0) {
      gsap.from(".chat-message:last-child", {
        opacity: 0,
        y: 20,
        duration: 0.5,
        ease: "power2.out"
      });
    }
  }, [chatHistory]);

  const renderTourStep = () => {
    if (!tourStep) return null;
    const darkTextStyle = { color: '#333333' }; // Dark gray color
    return (
      <div className="tour-step">
        <h2 style={{ ...tourTextStyle, ...darkTextStyle }}>{tourStep.title}</h2>
        <p style={darkTextStyle}>Current Page: {currentPage}</p>
        <p style={darkTextStyle}>{tourStep.description}</p>
        {tourStep.content_type === 'image' && <img src={tourStep.content} alt={tourStep.title} className="tour-image" />}
        {tourStep.content_type === 'video' && <video src={tourStep.content} controls className="tour-video" />}
        {tourStep.content_type === 'blog' && <div className="tour-blog-content" style={darkTextStyle}>{tourStep.content}</div>}
        {tourStep.content_type === 'interactive' && (
          <div className="interactive-content">
            {handleInteractiveContent(tourStep.content)}
          </div>
        )}
        <div className="tour-navigation">
          <button className="tour-button" onClick={prevTourStep} disabled={tourProgress === 0}>Previous</button>
          <button className="tour-button" onClick={nextTourStep} disabled={tourProgress === 100}>Next</button>
        </div>
      </div>
    );
  };

  const handleInteractiveContent = (content) => {
    switch (content.type) {
      case '3d_model':
        // Implement 3D model viewer
        break;
      case 'interactive_diagram':
        // Implement interactive diagram
        break;
      // Add more interactive content types as needed
    }
  };

  const renderChatHistory = () => {
    return (
      <div className="chat-container">
        {chatHistory.map((message, index) => (
          <div key={index} className={`chat-message ${message.role}-message`} style={chatStyle}>
            {message.content}
          </div>
        ))}
      </div>
    );
  };

  const renderProgressBar = () => {
    return (
      <div className="progress-bar">
        <div className="progress-bar-fill" style={{ width: `${tourProgress}%` }}></div>
      </div>
    );
  };

  return (
    <div className="app-container" style={appStyle}>
      <h1 style={tourTextStyle}>Interactive Tour Guide</h1>
      {isLoading ? (
        <div className="loading-spinner"></div>
      ) : (
        <>
          {renderProgressBar()}
          {renderTourStep()}
          {renderChatHistory()}
          <div className="chat-input-container">
            <form onSubmit={handleUserInput} className="chat-form">
              <input
                ref={inputRef}
                type="text"
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                placeholder="Ask a question or type a command..."
                className="chat-input"
                disabled={isLoading}
              />
              <button type="submit" className="chat-submit-button" disabled={isLoading}>
                {isLoading ? 'Sending...' : 'Send'}
              </button>
            </form>
          </div>
          {quizActive && (
            <div className="quiz-container">
              <h3 style={tourTextStyle}>{quizQuestion.question}</h3>
              {quizQuestion.options.map((option, index) => (
                <button key={index} onClick={() => handleQuizAnswer(option)}>
                  {option}
                </button>
              ))}
            </div>
          )}
          {error && <div className="error-message" style={{color: '#ff4d4d'}}>{error}</div>}
        </>
      )}
    </div>
  )
}

export default App