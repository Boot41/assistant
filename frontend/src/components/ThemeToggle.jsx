import React from 'react';
import { useTheme } from '../context/ThemeContext';
import '../styles/ThemeToggle.css';

const ThemeToggle = () => {
  const { isDarkMode, toggleTheme } = useTheme();

  return (
    <button className="theme-toggle" onClick={toggleTheme}>
      {isDarkMode ? '☀️' : '🌙'}
    </button>
  );
};

export default ThemeToggle;