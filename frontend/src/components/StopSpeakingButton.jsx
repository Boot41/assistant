// frontend/src/components/StopSpeakingButton.jsx
import React from 'react';
import PropTypes from 'prop-types';

function StopSpeakingButton({ isSpeaking, stopSpeaking }) {
  if (!isSpeaking) return null;

  return (
    <button
      className="stop-speaking-button"
      onClick={stopSpeaking}
      aria-label="Stop Speaking"
    >
      Stop Speaking
    </button>
  );
}

StopSpeakingButton.propTypes = {
  isSpeaking: PropTypes.bool.isRequired,
  stopSpeaking: PropTypes.func.isRequired,
};

export default StopSpeakingButton;