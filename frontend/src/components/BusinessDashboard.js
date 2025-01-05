import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';
import AvailabilityManager from './AvailabilityManager';
import AppointmentsManager from './AppointmentsManager';
import ServicesManager from './ServicesManager';
import ClientSearchManager from './ClientSearchManager';
import DailyStatsManager from './DailyStatsManager';
import '../styles/BusinessDashboard.css';

const BusinessDashboard = () => {
  const navigate = useNavigate();
  const { isDark, toggleTheme } = useTheme();
  const [showAvailability, setShowAvailability] = useState(false);
  const [showAppointments, setShowAppointments] = useState(false);
  const [showServices, setShowServices] = useState(false);
  const [showClientSearch, setShowClientSearch] = useState(false);
  const [showDailyStats, setShowDailyStats] = useState(false);
  const [exportLoading, setExportLoading] = useState(false);
  const [exportError, setExportError] = useState('');
  const [exportSuccess, setExportSuccess] = useState('');

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

      console.log('Starting export...');

      // Updated URL to match backend endpoint
      const response = await fetch('http://localhost:8000/api/business/appointments/export', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
      });

      console.log('Response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Server response:', errorText);
        throw new Error('Failed to export appointments');
      }

      const blob = await response.blob();
      console.log('Blob size:', blob.size);

      if (blob.size === 0) {
        throw new Error('No appointments data available');
      }

      // Get filename from response headers or use default
      const contentDisposition = response.headers.get('Content-Disposition');
      const filename = contentDisposition
        ? contentDisposition.split('filename=')[1].replace(/"/g, '')
        : `appointments_${new Date().toISOString().split('T')[0]}.xlsx`;

      // Create download link
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = filename;

      // Trigger download
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);

      setExportSuccess('Appointments exported successfully!');
      setTimeout(() => setExportSuccess(''), 3000);
    } catch (error) {
      console.error('Export error:', error);
      setExportError(error.message || 'Failed to export appointments. Please try again.');
    } finally {
      setExportLoading(false);
    }
};

  return (
    <div className={`dashboard-container ${!isDark ? 'light-mode' : ''}`}>
      <div className="dashboard-content">
        <div className="top-bar">
          <button onClick={handleLogout} className="logout-button">
            LogOut
          </button>
          <button onClick={toggleTheme} className="mode-toggle">
            {isDark ? 'Light Mode' : 'Dark Mode'}
          </button>
        </div>

        <div className="actions-panel">
          <button 
            className="dashboard-button"
            onClick={() => setShowAppointments(true)}
          >
            MY appointments
          </button>
          
          <button 
            className="dashboard-button"
            onClick={() => setShowServices(true)}
          >
            My Services
          </button>

          <button 
            className="dashboard-button"
            onClick={() => setShowClientSearch(true)}
          >
            Search Client
          </button>
          
          <button 
            className="dashboard-button"
            onClick={() => setShowAvailability(true)}
          >
            Make availability
          </button>
          
          <button 
            className="dashboard-button"
            onClick={() => setShowDailyStats(true)}
          >
            Search daily statistic
          </button>
          
          <button 
            className={`dashboard-button ${exportLoading ? 'loading' : ''}`}
            onClick={handleExportToExcel}
            disabled={exportLoading}
          >
            {exportLoading ? 'Exporting...' : 'Export appointments to Excel'}
          </button>
          
          {exportError && (
            <div className="error-message">
              {exportError}
            </div>
          )}
          
          {exportSuccess && (
            <div className="success-message">
              {exportSuccess}
            </div>
          )}
        </div>
      </div>

      {showAvailability && (
        <AvailabilityManager onClose={() => setShowAvailability(false)} />
      )}

      {showAppointments && (
        <AppointmentsManager onClose={() => setShowAppointments(false)} />
      )}

      {showServices && (
        <ServicesManager onClose={() => setShowServices(false)} />
      )}

      {showClientSearch && (
        <ClientSearchManager 
          onClose={() => setShowClientSearch(false)} 
        />
      )}

      {showDailyStats && (
        <DailyStatsManager onClose={() => setShowDailyStats(false)} />
      )}
    </div>
  );
};

export default BusinessDashboard;