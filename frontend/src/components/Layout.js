// src/components/Layout.js
import React from 'react';
import DarkModeButton from './DarkModeButton';
import { useTheme } from '../context/ThemeContext';
import '../styles/Layout.css';

const Layout = ({ children }) => {
  const { isDark } = useTheme();

  return (
    <div className={`layout ${!isDark ? 'light-mode' : ''}`}>
      <DarkModeButton />
      <div className="layout-content">
        {children}
      </div>
    </div>
  );
};

export default Layout;