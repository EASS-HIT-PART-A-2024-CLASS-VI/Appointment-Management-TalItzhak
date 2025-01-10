import React, { useState } from 'react';
import { useTheme } from '../context/ThemeContext';
import '../styles/DailyStatsManager.css';

const DailyStatsManager = ({ onClose }) => {
  const { isDark } = useTheme();
  const [selectedDate, setSelectedDate] = useState('');
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchDailyStats = async (date) => {
    try {
      setLoading(true);
      setError('');
      const formattedDate = formatDateForAPI(date);
      
      const response = await fetch(`http://localhost:8000/api/business/appointments/stats/${formattedDate}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch statistics');
      }

      const data = await response.json();
      setStats(data);
    } catch (error) {
      setError(error.message);
      setStats(null);
    } finally {
      setLoading(false);
    }
  };

  const formatDateForAPI = (dateString) => {
    const date = new Date(dateString);
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const year = date.getFullYear();
    return `${month}-${day}-${year}`;
  };

  const formatDateForDisplay = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const handleDateChange = (e) => {
    const date = e.target.value;
    setSelectedDate(date);
    if (date) {
      fetchDailyStats(date);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  return (
    <div className={`daily-stats-manager ${!isDark ? 'light-mode' : ''}`}>
      <div className="close-button" onClick={onClose}>×</div>
      
      <h2>Daily Statistics</h2>

      <div className="date-selector">
        <label>Select Date:</label>
        <input
          type="date"
          value={selectedDate}
          onChange={handleDateChange}
        />
      </div>

      {loading && (
        <div className="loading-state">
          Loading statistics...
        </div>
      )}

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {stats && (
        <div className="stats-container">
          <div className="stats-header">
            <h3>{formatDateForDisplay(stats.date)}</h3>
          </div>

          <div className="stats-grid">
            <div className="stat-card total-revenue">
              <div className="stat-title">Total Revenue</div>
              <div className="stat-value">{formatCurrency(stats.total_revenue)}</div>
            </div>

            {Object.entries(stats.services).map(([serviceName, serviceData]) => (
              <div key={serviceName} className="stat-card">
                <div className="stat-title">{serviceName}</div>
                <div className="stat-details">
                  <div>Appointments: {serviceData.count}</div>
                  <div>Revenue: {formatCurrency(serviceData.revenue)}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DailyStatsManager;