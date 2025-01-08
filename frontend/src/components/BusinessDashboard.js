// BusinessDashboard.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';
import AvailabilityManager from './AvailabilityManager';
import AppointmentsManager from './AppointmentsManager';
import ServicesManager from './ServicesManager';
import ClientSearchManager from './ClientSearchManager';
import DailyStatsManager from './DailyStatsManager';
import '../styles/BusinessDashboard.css';

import { 
  Calendar,
  Briefcase,
  Search,
  Clock,
  BarChart2,
  FileDown,
  LogOut
} from 'lucide-react';

const BusinessDashboard = () => {
  const navigate = useNavigate();
  const { isDark } = useTheme();
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

      const response = await fetch('http://localhost:8000/api/business/appointments/export', {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
          Accept: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        },
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error('Failed to export appointments');
      }

      const blob = await response.blob();
      if (blob.size === 0) {
        throw new Error('No appointments data available');
      }

      const contentDisposition = response.headers.get('Content-Disposition');
      const filename = contentDisposition
        ? contentDisposition.split('filename=')[1].replace(/"/g, '')
        : `appointments_${new Date().toISOString().split('T')[0]}.xlsx`;

      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = filename;

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);

      setExportSuccess('Appointments exported successfully!');
      setTimeout(() => setExportSuccess(''), 3000);
    } catch (error) {
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
            <LogOut size={18} className="button-icon" />
            <span>LogOut</span>
          </button>
        </div>

        <div className="actions-panel">
          <button
            className="dashboard-button"
            onClick={() => setShowAppointments(true)}
          >
            <Calendar size={18} className="button-icon" />
            <span>My Appointments</span>
          </button>

          <button
            className="dashboard-button"
            onClick={() => setShowServices(true)}
          >
            <Briefcase size={18} className="button-icon" />
            <span>My Services</span>
          </button>

          <button
            className="dashboard-button"
            onClick={() => setShowClientSearch(true)}
          >
            <Search size={18} className="button-icon" />
            <span>Search Client</span>
          </button>

          <button
            className="dashboard-button"
            onClick={() => setShowAvailability(true)}
          >
            <Clock size={18} className="button-icon" />
            <span>Make Availability</span>
          </button>

          <button
            className="dashboard-button"
            onClick={() => setShowDailyStats(true)}
          >
            <BarChart2 size={18} className="button-icon" />
            <span>Daily Statistics</span>
          </button>

          <button
            className={`dashboard-button ${exportLoading ? 'loading' : ''}`}
            onClick={handleExportToExcel}
            disabled={exportLoading}
          >
            <FileDown size={18} className="button-icon" />
            <span>{exportLoading ? 'Exporting...' : 'Export Appointments to Excel'}</span>
          </button>

          {exportError && <div className="error-message">{exportError}</div>}
          {exportSuccess && <div className="success-message">{exportSuccess}</div>}
        </div>
      </div>

      {showAvailability && <AvailabilityManager onClose={() => setShowAvailability(false)} />}
      {showAppointments && <AppointmentsManager onClose={() => setShowAppointments(false)} />}
      {showServices && <ServicesManager onClose={() => setShowServices(false)} />}
      {showClientSearch && <ClientSearchManager onClose={() => setShowClientSearch(false)} />}
      {showDailyStats && <DailyStatsManager onClose={() => setShowDailyStats(false)} />}
    </div>
  );
};

export default BusinessDashboard;