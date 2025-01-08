import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';
import MyAppointmentViewer from './MyAppointmentViewer';
import BusinessList from './BusinessList';
import { Calendar, Building, LogOut, PlusCircle } from 'lucide-react';
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

  const handleCreateMeeting = () => {
    // Navigate to business list with a flag indicating we're creating a meeting
    setShowAllBusinesses(true);
  };

  return (
    <div className={`dashboard-container ${!isDark ? 'light-mode' : ''}`}>
      <div className="dashboard-content">
        <div className="top-bar">
          <button onClick={handleLogout} className="logout-button">
            <LogOut size={18} className="button-icon" />
            LogOut
          </button>
        </div>

        <div className="actions-panel">
          <button 
            className="dashboard-button"
            onClick={() => setShowMyAppointments(true)}
          >
            <Calendar size={18} className="button-icon" />
            My Appointments
          </button>
          
          <button 
            className="dashboard-button"
            onClick={handleCreateMeeting}
          >
            <PlusCircle size={18} className="button-icon" />
            Create Meeting
          </button>

          <button 
            className="dashboard-button"
            onClick={() => setShowAllBusinesses(true)}
          >
            <Building size={18} className="button-icon" />
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
          isCreatingMeeting={true}  // Add this prop to BusinessList
        />
      )}
    </div>
  );
};

export default CustomerDashboard;