// src/components/CustomerDashboard.js
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';
import MyAppointmentViewer from './MyAppointmentViewer';
import BusinessList from './BusinessList';
import { Calendar, Building, LogOut, PlusCircle } from 'lucide-react';
import '../styles/CustomerDashboard.css';

const CustomerDashboard = () => {
  const navigate = useNavigate();
  const { isDark } = useTheme();
  const [activeView, setActiveView] = useState('dashboard');
  const [userName, setUserName] = useState('');

  useEffect(() => {
    const fetchUserName = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          console.error('Token is missing or invalid');
          navigate('/login');
          return;
        }

        const response = await fetch('http://localhost:8000/api/shared/me', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          console.error('Failed to fetch user information:', response.status, await response.text());
          return;
        }

        const data = await response.json();
        setUserName(`${data.first_name} ${data.last_name}`);
      } catch (error) {
        console.error('Error fetching user name:', error);
      }
    };

    fetchUserName();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userRole');
    navigate('/login');
  };

  return (
    <div className={`app-container ${!isDark ? 'light-mode' : ''}`}>
      <div className="sidebar">
        <div className="brand">
          <h2>{userName}</h2>
        </div>
        <nav className="nav-menu">
          <button 
            className={`nav-item ${activeView === 'appointments' ? 'active' : ''}`}
            onClick={() => setActiveView('appointments')}
          >
            <Calendar className="nav-icon" />
            <span>My Appointments</span>
          </button>

          <button 
            className={`nav-item ${activeView === 'create-meeting' ? 'active' : ''}`}
            onClick={() => setActiveView('create-meeting')}
          >
            <PlusCircle className="nav-icon" />
            <span>Create Meeting</span>
          </button>

          <button 
            className={`nav-item ${activeView === 'businesses' ? 'active' : ''}`}
            onClick={() => setActiveView('businesses')}
          >
            <Building className="nav-icon" />
            <span>All Businesses</span>
          </button>

          <button className="nav-item logout" onClick={handleLogout}>
            <LogOut className="nav-icon" />
            <span>Logout</span>
          </button>
        </nav>
      </div>
      <div className="main-content">
        {activeView === 'appointments' && (
          <MyAppointmentViewer onClose={() => setActiveView('dashboard')} />
        )}
        {activeView === 'create-meeting' && (
          <BusinessList onClose={() => setActiveView('dashboard')} viewType="create" />
        )}
        {activeView === 'businesses' && (
          <BusinessList onClose={() => setActiveView('dashboard')} viewType="availability" />
        )}
      </div>
    </div>
  );
};

export default CustomerDashboard;