import React from 'react';
import { useTheme } from '../context/ThemeContext';
import '../styles/Layout.css';

const Layout = ({ children }) => {
  const { isDark, toggleTheme } = useTheme();

  return (
    <div className={`layout ${!isDark ? 'light-mode' : ''}`}>
      <div className="theme-button">
        <button onClick={toggleTheme} className="mode-toggle">
          {isDark ? '☀️ Light Mode' : '🌙 Dark Mode'}
        </button>
      </div>
      {children}
    </div>
  );
};

export default Layout;