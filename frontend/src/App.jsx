import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'
import TourAnalytics from './components/TourAnalytics';

function App() {
  const [tourStep, setTourStep] = useState(null)
  const [userInput, setUserInput] = useState('')
  const [chatHistory, setChatHistory] = useState([])
  const [currentPage, setCurrentPage] = useState('Home')
  const [showMedia, setShowMedia] = useState(false)
  const [mediaContent, setMediaContent] = useState(null)
  const [tourProgress, setTourProgress] = useState(0)
  const [allTourSteps, setAllTourSteps] = useState([])
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [quizActive, setQuizActive] = useState(false)
  const [quizQuestion, setQuizQuestion] = useState(null)

  useEffect(() => {
    getTourProgress()
    getAllTourSteps()
  }, [])

  const getAllTourSteps = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/tour/steps/')
      setAllTourSteps(res.data)
    } catch (error) {
      console.error('Error getting tour steps:', error)
    }
  }

  const getTourProgress = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/tour/progress/', { params: { user_id: 'test_user' } })
      setTourStep(res.data.current_step)
      setTourProgress(res.data.progress_percentage)
    } catch (error) {
      console.error('Error getting tour progress:', error)
    }
  }

  const handleUserInput = async (e) => {
    e.preventDefault()
    try {
      const res = await axios.post('http://localhost:8000/api/tour-guide/', {
        user_id: 'test_user',
        user_input: userInput,
        current_page: currentPage
      })
      setChatHistory(prevHistory => [...prevHistory, 
        { role: 'user', content: userInput },
        { role: 'assistant', content: res.data.response }
      ])
      handleActions(res.data.actions)
      setUserInput('')
    } catch (error) {
      console.error('Error processing interaction:', error)
    }
  }

  const startTour = async () => {
    try {
      const res = await axios.post('http://localhost:8000/api/tour/start/', { user_id: 'test_user' })
      setTourStep(res.data.current_step)
      setCurrentPage(res.data.current_step.page_name)
      setTourProgress(0)
      setChatHistory([])
    } catch (error) {
      console.error('Error starting tour:', error)
    }
  }

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
      } else {
        setTourStep(res.data.current_step)
        setCurrentPage(res.data.current_step.page_name)
        setTourProgress(res.data.progress_percentage)
        speak(res.data.current_step.description)
        if (res.data.quiz_question) {
          setQuizQuestion(res.data.quiz_question)
          setQuizActive(true)
        } else {
          setQuizQuestion(null)
          setQuizActive(false)
        }
      }
    } catch (error) {
      console.error('Error getting next step:', error.response?.data?.error || error.message)
      // Optionally, you can set an error state and display it to the user
      // setError('Failed to fetch the next tour step. Please try again.');
    }
  }

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
          setCurrentPage(action.target)
          break
        case 'show_video':
        case 'show_image':
          setShowMedia(true)
          setMediaContent(action.content)
          break
        default:
          console.log('Unknown action:', action)
      }
    })
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
        // Implement previous step functionality
      }
    }
    window.addEventListener('keydown', handleKeyPress)
    return () => {
      window.removeEventListener('keydown', handleKeyPress)
    }
  }, [])

  return (
    <div className="App">
      <header>
        <h1>Interactive Tour Guide</h1>
        <p>Current Page: {currentPage}</p>
        <div className="tour-progress-bar">
          <div className="progress" style={{width: `${tourProgress}%`}}></div>
        </div>
      </header>
      <div className="main-content">
        <aside className="tour-steps-sidebar">
          <h3>Tour Steps</h3>
          <ul>
            {allTourSteps.map(step => (
              <li key={step.order} 
                  className={tourStep && step.order === tourStep.order ? 'active' : ''}
                  onClick={() => goToStep(step.order)}>
                {step.title}
              </li>
            ))}
          </ul>
        </aside>
        <main>
          {!tourStep && <button onClick={startTour}>Start Tour</button>}
          {tourStep && (
            <div className="tour-step">
              <h2>{tourStep.title}</h2>
              <p>{tourStep.description}</p>
              {tourStep.image && <img src={tourStep.image} alt={tourStep.title} className="tour-image" />}
              {tourStep.video && (
                <video src={tourStep.video} controls className="tour-video">
                  Your browser does not support the video tag.
                </video>
              )}
              <button onClick={nextTourStep}>Next Step</button>
              <button onClick={() => speak(tourStep.description)} disabled={isSpeaking}>
                {isSpeaking ? 'Speaking...' : 'Read Aloud'}
              </button>
            </div>
          )}
          {quizActive && quizQuestion && (
            <div className="quiz-container">
              <h3>Quick Quiz</h3>
              <p>{quizQuestion.question}</p>
              {quizQuestion.options.map((option, index) => (
                <button key={index} onClick={() => handleQuizAnswer(option)}>
                  {option}
                </button>
              ))}
            </div>
          )}
          <div className="chat-area">
            {chatHistory.map((message, index) => (
              <div key={index} className={`message ${message.role}`}>
                <p>{message.content}</p>
              </div>
            ))}
          </div>
          <form onSubmit={handleUserInput} className="user-input">
            <input
              type="text"
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              placeholder="Ask a question or give a command"
            />
            <button type="submit">Send</button>
          </form>
          {showMedia && (
            <div className="media-modal">
              {mediaContent.includes('video') ? (
                <video src={mediaContent} controls />
              ) : (
                <img src={mediaContent} alt="Tour content" />
              )}
              <button onClick={() => setShowMedia(false)}>Close</button>
            </div>
          )}
        </main>
      </div>
      <TourAnalytics />
    </div>
  )
}

export default App