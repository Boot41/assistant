import { useState } from 'react';
import PropTypes from 'prop-types';
import './TranscriptView.css';

function TranscriptView({ transcript, setSearchTerm, setStartDate, setEndDate, exportTranscript }) {
  const [isVisible, setIsVisible] = useState(false);

  return (
    <div className="transcript-wrapper">
      <div className="transcript-toggle-container">
        <button className="transcript-toggle" onClick={() => setIsVisible(!isVisible)}>
          {isVisible ? 'Hide Transcript' : 'Show Transcript'}
        </button>
      </div>
      <div className={`transcript-container ${isVisible ? 'visible' : 'hidden'}`}>
        {isVisible && (
          <div className="transcript-content">
            <h3>Transcript</h3>
            <div className="transcript-controls">
              <input
                type="text"
                placeholder="Search transcript..."
                onChange={(e) => setSearchTerm(e.target.value)}
              />
              <input
                type="date"
                onChange={(e) => setStartDate(new Date(e.target.value).getTime())}
              />
              <input
                type="date"
                onChange={(e) => setEndDate(new Date(e.target.value).getTime())}
              />
              <button onClick={exportTranscript}>Export Transcript</button>
            </div>
            <div className="transcript-messages">
              {transcript.map((entry, index) => (
                <div key={index} className={`transcript-entry ${entry.speaker.toLowerCase()}`}>
                  <span className="transcript-timestamp">{new Date(entry.timestamp).toLocaleString()}</span>
                  <span className="transcript-speaker">{entry.speaker}:</span>
                  <span className="transcript-text">{entry.text}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

TranscriptView.propTypes = {
  transcript: PropTypes.arrayOf(PropTypes.shape({
    speaker: PropTypes.string.isRequired,
    text: PropTypes.string.isRequired,
    timestamp: PropTypes.number.isRequired,
  })).isRequired,
  setSearchTerm: PropTypes.func.isRequired,
  setStartDate: PropTypes.func.isRequired,
  setEndDate: PropTypes.func.isRequired,
  exportTranscript: PropTypes.func.isRequired,
};

export default TranscriptView;
