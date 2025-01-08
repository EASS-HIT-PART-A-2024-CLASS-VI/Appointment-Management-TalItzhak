// src/components/DarkModeButton.js
import React from 'react';
import { useTheme } from '../context/ThemeContext';
import '../styles/DarkModeButton.css';

const DarkModeButton = () => {
  const { isDark, toggleTheme } = useTheme();

  return (
    <button onClick={toggleTheme} className="dark-mode-toggle">
      {isDark ? '☀️ Light Mode' : '🌙 Dark Mode'}
    </button>
  );
};

export default DarkModeButton;