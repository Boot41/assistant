import { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';

const TourGuide = () => {
  const [tourSteps, setTourSteps] = useState([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [isVisible, setIsVisible] = useState(true);
  const [currentPage, setCurrentPage] = useState('Exploring our services');

  useEffect(() => {
    fetchTourSteps();
  }, []);

  const fetchTourSteps = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/tour-steps/');
      setTourSteps(response.data);
    } catch (error) {
      console.error('Error fetching tour steps:', error);
    }
  };

  const handleNext = () => {
    if (currentStep < tourSteps.length - 1) {
      setIsVisible(false);
      setTimeout(() => {
        setCurrentStep(prev => prev + 1);
        setCurrentPage(tourSteps[currentStep + 1].page_name);
        setIsVisible(true);
      }, 300);
    }
  };

  const handlePrev = () => {
    if (currentStep > 0) {
      setIsVisible(false);
      setTimeout(() => {
        setCurrentStep(prev => prev - 1);
        setCurrentPage(tourSteps[currentStep - 1].page_name);
        setIsVisible(true);
      }, 300);
    }
  };

  const renderTourStep = () => {
    const step = tourSteps[currentStep];
    if (!step) return null;

    return (
      <AnimatePresence>
        {isVisible && (
          <motion.div
            className="tour-step"
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 50 }}
            transition={{ duration: 0.3 }}
          >
            <h3>{step.title}</h3>
            <p>{step.description}</p>
            <p>{step.content}</p>
            <div className="flex justify-between mt-4">
              <button
                onClick={handlePrev}
                disabled={currentStep === 0}
                className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded-l"
              >
                Previous
              </button>
              <button
                onClick={handleNext}
                disabled={currentStep === tourSteps.length - 1}
                className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded-r"
              >
                Next
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    );
  };

  return (
    <>
      {renderTourStep()}
    </>
  );
};

export default TourGuide;
