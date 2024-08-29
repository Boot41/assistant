import PropTypes from 'prop-types';
import Jarvis from './blob';

function JarvisContainer({ isSpeaking, isRecording }) {
  return (
    <div className="jarvis-container">
      <Jarvis isSpeaking={isSpeaking} isRecording={isRecording} />
    </div>
  );
}

JarvisContainer.propTypes = {
  isSpeaking: PropTypes.bool.isRequired,
  isRecording: PropTypes.bool.isRequired,
};

export default JarvisContainer;