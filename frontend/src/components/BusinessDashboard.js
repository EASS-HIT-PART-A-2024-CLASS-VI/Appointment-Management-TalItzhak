// src/components/BusinessDashboard.js
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';
import AvailabilityManager from './AvailabilityManager';
import AppointmentsManager from './AppointmentsManager';
import ServicesManager from './ServicesManager';
import ClientSearchManager from './ClientSearchManager';
import DailyStatsManager from './DailyStatsManager';
import { Calendar, Briefcase, Search, Clock, BarChart2, FileDown, LogOut } from 'lucide-react';
import '../styles/BusinessDashboard.css';

const BusinessDashboard = () => {
  const navigate = useNavigate();
  const { isDark } = useTheme();
  const [activeView, setActiveView] = useState('dashboard');
  const [businessInfo, setBusinessInfo] = useState(null);
  const [exportLoading, setExportLoading] = useState(false);
  const [exportError, setExportError] = useState('');
  const [exportSuccess, setExportSuccess] = useState('');

  useEffect(() => {
    const fetchBusinessInfo = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/shared/me', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (response.ok) {
          const data = await response.json();
          setBusinessInfo(data);
        }
      } catch (error) {
        console.error('Error fetching business info:', error);
      }
    };

    fetchBusinessInfo();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userRole');
    navigate('/login');
  };

  const handleExportToExcel = async () => {
    try {
      setExportLoading(true);
      setExportError('');
      setExportSuccess('');

      const response = await fetch('http://localhost:8000/api/business/appointments/export', {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
          Accept: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        },
      });

      if (!response.ok) throw new Error('Failed to export appointments');

      const blob = await response.blob();
      if (blob.size === 0) throw new Error('No appointments data available');

      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = 'appointments.xlsx';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);

      setExportSuccess('Appointments exported successfully!');
      setTimeout(() => setExportSuccess(''), 3000);
    } catch (error) {
      setExportError(error.message || 'Failed to export appointments');
    } finally {
      setExportLoading(false);
    }
  };

  return (
    <div className={`app-container ${!isDark ? 'light-mode' : ''}`}>
      {/* Sidebar */}
      <div className="sidebar">
        <div className="brand">
          {businessInfo ? (
            <h2>{businessInfo.business_name}</h2>
          ) : (
            <div className="loading-spinner">
              <span>Fetching business name...</span>
            </div>
          )}
        </div>
        
        <nav className="nav-menu">
          <button 
            className={`nav-item ${activeView === 'calendar' ? 'active' : ''}`}
            onClick={() => setActiveView('calendar')}
          >
            <Calendar className="nav-icon" />
            <span>My Appointments</span>
          </button>

          <button 
            className={`nav-item ${activeView === 'services' ? 'active' : ''}`}
            onClick={() => setActiveView('services')}
          >
            <Briefcase className="nav-icon" />
            <span>Services</span>
          </button>

          <button 
            className={`nav-item ${activeView === 'clients' ? 'active' : ''}`}
            onClick={() => setActiveView('clients')}
          >
            <Search className="nav-icon" />
            <span>Clients</span>
          </button>

          <button 
            className={`nav-item ${activeView === 'availability' ? 'active' : ''}`}
            onClick={() => setActiveView('availability')}
          >
            <Clock className="nav-icon" />
            <span>Availability</span>
          </button>

          <button 
            className={`nav-item ${activeView === 'stats' ? 'active' : ''}`}
            onClick={() => setActiveView('stats')}
          >
            <BarChart2 className="nav-icon" />
            <span>Statistics</span>
          </button>

          <button
            className={`nav-item ${activeView === 'export' ? 'active' : ''}`}
            onClick={handleExportToExcel}
            disabled={exportLoading}
          >
            <FileDown className="nav-icon" />
            <span>{exportLoading ? 'Exporting...' : 'Export to Excel'}</span>
          </button>

          <button className="nav-item logout" onClick={handleLogout}>
            <LogOut className="nav-icon" />
            <span>Logout</span>
          </button>
        </nav>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {exportError && <div className="error-message">{exportError}</div>}
        {exportSuccess && <div className="success-message">{exportSuccess}</div>}
        {activeView === 'calendar' && <AppointmentsManager onClose={() => setActiveView('dashboard')} />}
        {activeView === 'services' && <ServicesManager onClose={() => setActiveView('dashboard')} />}
        {activeView === 'clients' && <ClientSearchManager onClose={() => setActiveView('dashboard')} />}
        {activeView === 'availability' && <AvailabilityManager onClose={() => setActiveView('dashboard')} />}
        {activeView === 'stats' && <DailyStatsManager onClose={() => setActiveView('dashboard')} />}
      </div>
    </div>
  );
};

export default BusinessDashboard;