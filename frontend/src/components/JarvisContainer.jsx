import PropTypes from 'prop-types';
import Jarvis from './blob';

function JarvisContainer({ isSpeaking, isRecording, isMinimized, isClosing, playerRef, presentationData, isPresentationModalOpen, setIsPresentationModalOpen }) {
  return (
    <div className="jarvis-container">
      <Jarvis 
        isSpeaking={isSpeaking} 
        isRecording={isRecording}
        isMinimized={isMinimized}
        isClosing={isClosing}
        playerRef={playerRef}
        presentationData={presentationData}
        isPresentationModalOpen={isPresentationModalOpen}
        setIsPresentationModalOpen={setIsPresentationModalOpen}
      />
    </div>
  );
}

JarvisContainer.propTypes = {
  isSpeaking: PropTypes.bool.isRequired,
  isRecording: PropTypes.bool.isRequired,
  isMinimized: PropTypes.bool,
  isClosing: PropTypes.bool,
  playerRef: PropTypes.object,
  presentationData: PropTypes.object,
  isPresentationModalOpen: PropTypes.bool,
  setIsPresentationModalOpen: PropTypes.func,
};

export default JarvisContainer;