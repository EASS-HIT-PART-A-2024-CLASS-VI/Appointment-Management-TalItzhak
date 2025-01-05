import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';
import MyAppointmentViewer from './MyAppointmentViewer';
import BusinessList from './BusinessList';
import '../styles/CustomerDashboard.css';

const CustomerDashboard = () => {
  const navigate = useNavigate();
  const { isDark } = useTheme();
  const [showMyAppointments, setShowMyAppointments] = useState(false);
  const [showAllBusinesses, setShowAllBusinesses] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userRole');
    navigate('/login');
  };

  return (
    <div className={`dashboard-container ${!isDark ? 'light-mode' : ''}`}>
      <div className="dashboard-content">
        <div className="top-bar">
          <button onClick={handleLogout} className="logout-button">
            LogOut
          </button>
        </div>

        <div className="actions-panel">
          <button 
            className="dashboard-button"
            onClick={() => {
              console.log("Opening appointments");  // Debug log
              setShowMyAppointments(true);
            }}
          >
            My Appointments
          </button>
          
          <button 
            className="dashboard-button"
            onClick={() => setShowAllBusinesses(true)}
          >
            All Businesses
          </button>
        </div>
      </div>

      {showMyAppointments && (
        <MyAppointmentViewer 
          onClose={() => setShowMyAppointments(false)} 
        />
      )}

      {showAllBusinesses && (
        <BusinessList 
          onClose={() => setShowAllBusinesses(false)} 
        />
      )}
    </div>
  );
};

export default CustomerDashboard;