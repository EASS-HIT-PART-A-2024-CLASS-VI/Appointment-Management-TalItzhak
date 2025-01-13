// src/components/DailyStatsManager.js
import React, { useState } from 'react';
import { useTheme } from '../context/ThemeContext';
import { Calendar } from 'lucide-react';
import '../styles/DailyStatsManager.css';

const DailyStatsManager = ({ onClose }) => {
  const { isDark } = useTheme();
  const [selectedDate, setSelectedDate] = useState('');
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const formatDateForAPI = (dateString) => {
    const date = new Date(dateString);
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const year = date.getFullYear();
    return `${month}-${day}-${year}`;
  };

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
    <div className={`daily-stats-container ${!isDark ? 'light-mode' : ''}`}>
      <div className="stats-header">
        <div className="header-content">
          <h2>Daily Statistics</h2>
          <div className="date-selector">
            <Calendar className="calendar-icon" size={20} />
            <input
              type="date"
              value={selectedDate}
              onChange={handleDateChange}
              className="date-input"
            />
          </div>
        </div>
        <button className="close-button" onClick={onClose}>×</button>
      </div>

      {loading ? (
        <div className="loading-state">
          <div className="spinner"></div>
          <span>Loading statistics...</span>
        </div>
      ) : error ? (
        <div className="error-message">
          {error}
        </div>
      ) : stats && (
        <div className="stats-content">
          <div className="stats-date">
            {formatDateForDisplay(stats.date)}
          </div>

          <div className="total-revenue-card">
            <div className="card-label">Total Revenue</div>
            <div className="revenue-amount">{formatCurrency(stats.total_revenue)}</div>
          </div>

          <div className="services-grid">
            {Object.entries(stats.services).map(([serviceName, serviceData]) => (
              <div key={serviceName} className="service-card">
                <div className="service-header">
                  <h3>{serviceName}</h3>
                  <span className="appointment-count">
                    {serviceData.count} appointment{serviceData.count !== 1 ? 's' : ''}
                  </span>
                </div>
                <div className="service-revenue">
                  {formatCurrency(serviceData.revenue)}
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