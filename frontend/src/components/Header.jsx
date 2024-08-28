import React from 'react';
import ThemeToggle from './ThemeToggle';
import '../styles/Header.css';

const Header = () => (
  <header className="app-header">
    <h1>Jarvis AI Assistant</h1>
    <ThemeToggle />
  </header>
);

export default Header;