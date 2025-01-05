import React, { useState, useEffect } from 'react';
import { useTheme } from '../context/ThemeContext';
import '../styles/BusinessAvailability.css';

const BusinessAvailability = ({ businessId, onClose }) => {
  const { isDark } = useTheme();
  const [availability, setAvailability] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAvailability();
  }, [businessId]);

  const fetchAvailability = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/availability/business/${businessId}/availability`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      
      if (!response.ok) throw new Error('Failed to fetch availability');
      const data = await response.json();
      setAvailability(data.availability || []);
    } catch (error) {
      setError('Failed to load availability');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`availability-viewer ${!isDark ? 'light-mode' : ''}`}>
      <div className="close-button" onClick={onClose}>×</div>
      <h3>Business Availability</h3>
      
      {error && <div className="error-message">{error}</div>}
      
      {loading ? (
        <div className="loading">Loading availability...</div>
      ) : availability.length === 0 ? (
        <div className="no-availability">No availability set</div>
      ) : (
        <div className="availability-grid">
          {availability.map((slot, index) => (
            <div key={index} className="availability-slot">
              <h4>{slot.day_of_week}</h4>
              <p>{slot.start_time.slice(0, 5)} - {slot.end_time.slice(0, 5)}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default BusinessAvailability;