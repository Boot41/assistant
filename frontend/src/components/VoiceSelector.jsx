import React, { useState } from 'react';
import PropTypes from 'prop-types';

function VoiceSelector({ voices, selectedVoice, setSelectedVoice }) {
  const [isVisible, setIsVisible] = useState(false);

  const toggleVisibility = () => {
    setIsVisible(!isVisible);
  };

  return (
    <div className="voice-selector-container">
      <button onClick={toggleVisibility} className="voice-selector-toggle">
        {isVisible ? 'Hide Voices' : 'Select Voice'}
      </button>
      {isVisible && (
        <div className="voice-selector">
          <select
            id="voice-select"
            value={selectedVoice ? selectedVoice.name : ''}
            onChange={(e) => {
              const voice = voices.find(v => v.name === e.target.value);
              setSelectedVoice(voice);
            }}
          >
            {voices.map((voice) => (
              <option key={voice.name} value={voice.name}>
                {`${voice.name} (${voice.lang})`}
              </option>
            ))}
          </select>
        </div>
      )}
    </div>
  );
}

VoiceSelector.propTypes = {
  voices: PropTypes.array.isRequired,
  selectedVoice: PropTypes.object,
  setSelectedVoice: PropTypes.func.isRequired,
};

export default VoiceSelector;