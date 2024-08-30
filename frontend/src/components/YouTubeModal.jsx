import React, { useState, useEffect, useRef } from "react";
import ReactPlayer from "react-player";
import Jarvis from "./blob";
import "../styles/YouTubeModal.css";

function YouTubeModal({ videoUrl, isOpen, onClose }) {
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isMinimized, setIsMinimized] = useState(false);
  const [isClosing, setIsClosing] = useState(false);
  const playerRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      setIsLoading(true);
      setError(null);
      setIsClosing(false);
      setTimeout(() => setIsMinimized(true), 100);
    } else {
      setIsMinimized(false);
    }
  }, [isOpen]);

  const handleReady = () => {
    setIsLoading(false);
  };

  const handleError = (e) => {
    setError("Failed to load the video. Please try again.");
    setIsLoading(false);
    console.error("Error loading video:", e);
  };

  const handleClose = () => {
    setIsClosing(true);
    setIsMinimized(false);
    setTimeout(() => {
      onClose();
      setIsClosing(false);
    }, 500); // Adjust this timing to match your transition duration
  };

  if (!isOpen && !isClosing) return null;

  return (
    <div className={`youtube-modal-overlay ${isClosing ? 'closing' : ''}`}>
      <div className={`youtube-modal ${isClosing ? 'closing' : ''}`}>
        <button className="close-button" onClick={handleClose}>&times;</button>
        {isLoading && <div className="loading">Loading video...</div>}
        {error && <div className="error">{error}</div>}
        <div className="video-player-container" ref={playerRef}>
          <ReactPlayer
            url={videoUrl}
            width="100%"
            height="100%"
            controls={true}
            playing={true}
            onReady={handleReady}
            onError={handleError}
          />
        </div>
      </div>
      <Jarvis 
        isRecording={false} 
        isMinimized={isMinimized}
        isClosing={isClosing}
        playerRef={playerRef}
      />
    </div>
  );
}

export default YouTubeModal;