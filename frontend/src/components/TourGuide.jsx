import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';

const TourGuide = ({ currentPage, setCurrentPage, isTourStarted, setIsTourStarted, tourSteps }) => {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    if (isTourStarted && tourSteps.length > 0) {
      const stepIndex = tourSteps.findIndex(step => step.page_name === currentPage);
      if (stepIndex !== -1) {
        setCurrentStep(stepIndex);
      }
    }
  }, [isTourStarted, currentPage, tourSteps]);

  const renderTourStep = () => {
    if (!isTourStarted || tourSteps.length === 0) return null;
    const step = tourSteps[currentStep];
    return (
      <div className="tour-step">
        <h3>{step.title}</h3>
        <p>{step.description}</p>
        <p>{step.content}</p>
      </div>
    );
  };

  return (
    <>
      {isTourStarted ? (
        renderTourStep()
      ) : (
        <div>Tour not started. Use the chat to start the tour.</div>
      )}
    </>
  );
};

TourGuide.propTypes = {
  currentPage: PropTypes.string.isRequired,
  setCurrentPage: PropTypes.func.isRequired,
  isTourStarted: PropTypes.bool.isRequired,
  setIsTourStarted: PropTypes.func.isRequired,
  tourSteps: PropTypes.arrayOf(PropTypes.object).isRequired,
};

export default TourGuide;
