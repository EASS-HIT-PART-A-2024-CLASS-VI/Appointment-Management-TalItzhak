import React, { useState, useEffect } from 'react';
import { useTheme } from '../context/ThemeContext';
import '../styles/BusinessAvailability.css';

const DAYS_ORDER = [
  'Sunday',
  'Monday',
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday',
  'Saturday'
];

const BusinessAvailability = ({ businessId, onClose }) => {
  const { isDark } = useTheme();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [businessName, setBusinessName] = useState('');
  const [processedAvailability, setProcessedAvailability] = useState({});

  useEffect(() => {
    fetchAvailability();
  }, [businessId]);

  const fetchAvailability = async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/availability/business/${businessId}/availability`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
      
      if (!response.ok) throw new Error('Failed to fetch availability');
      const data = await response.json();
      setBusinessName(data.business_name);

      // Process availability data into a single entry per day with multiple time slots
      const grouped = data.availability.reduce((acc, slot) => {
        const day = slot.day_of_week;
        if (!acc[day]) {
          acc[day] = [];
        }
        acc[day].push({
          start: slot.start_time,
          end: slot.end_time
        });
        // Sort time slots for each day
        acc[day].sort((a, b) => a.start.localeCompare(b.start));
        return acc;
      }, {});

      setProcessedAvailability(grouped);
    } catch (error) {
      setError('Failed to load availability');
    } finally {
      setLoading(false);
    }
  };

  // Function to get all days sorted with their availability
  const getSortedAvailability = () => {
    return DAYS_ORDER.map(day => ({
      day,
      timeSlots: processedAvailability[day] || []
    })).filter(dayData => dayData.timeSlots.length > 0);
  };

  return (
    <div className={`availability-viewer ${!isDark ? 'light-mode' : ''}`}>
      <div className="header">
        <button className="back-button" onClick={onClose}>
          ← Back to Businesses
        </button>
        <h2>{businessName}'s Availability</h2>
      </div>

      {error && <div className="error-message">{error}</div>}

      {loading ? (
        <div className="loading">Loading availability...</div>
      ) : (
        <div className="availability-grid">
          {getSortedAvailability().map(({ day, timeSlots }) => (
            <div key={day} className="availability-card">
              <div className="day-header">
                <h3 className="day-name">{day}</h3>
              </div>
              <div className="time-slots">
                {timeSlots.map((slot, index) => (
                  <div key={index} className="time-slot">
                    {slot.start.slice(0, 5)} - {slot.end.slice(0, 5)}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default BusinessAvailability;