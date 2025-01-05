import React, { useState, useEffect } from 'react';
import { useTheme } from '../context/ThemeContext';
import '../styles/AvailabilityManager.css';

const DAYS_OF_WEEK = [
  "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"
];

const AvailabilityManager = ({ onClose }) => {
  const { isDark } = useTheme();
  const [availabilities, setAvailabilities] = useState({});
  const [selectedDay, setSelectedDay] = useState(null);
  const [timeForm, setTimeForm] = useState({
    start_time: '',
    end_time: ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Fetch existing availabilities
  useEffect(() => {
    fetchAvailabilities();
  }, []);

  const fetchAvailabilities = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/availability/my-availability', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      
      // Convert array to object grouped by day with multiple slots
      const availabilityByDay = data.reduce((acc, curr) => {
        if (!acc[curr.day_of_week]) {
          acc[curr.day_of_week] = [];
        }
        acc[curr.day_of_week].push(curr);
        return acc;
      }, {});
      
      setAvailabilities(availabilityByDay);
    } catch (error) {
      setError('Failed to fetch availabilities');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedDay) return;

    try {
      const response = await fetch('http://localhost:8000/api/availability/availability', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          day_of_week: selectedDay,
          start_time: timeForm.start_time,
          end_time: timeForm.end_time
        })
      });

      if (!response.ok) throw new Error('Failed to set availability');

      setSuccess(`Time slot added for ${selectedDay}`);
      fetchAvailabilities();
      setTimeForm({ start_time: '', end_time: '' });
    } catch (error) {
      setError('Failed to set availability');
    }
  };

  const handleDelete = async (availabilityId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/availability/availability/${availabilityId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) throw new Error('Failed to delete availability');

      setSuccess('Time slot deleted successfully');
      fetchAvailabilities();
    } catch (error) {
      setError('Failed to delete availability');
    }
  };

  const formatTime = (time) => {
    return time.slice(0, 5); // Format HH:mm from HH:mm:ss
  };

  return (
    <div className={`availability-manager ${!isDark ? 'light-mode' : ''}`}>
      <div className="close-button" onClick={onClose}>×</div>
      
      <h2>Set Your Availability</h2>
      
      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      <div className="days-grid">
        {DAYS_OF_WEEK.map(day => (
          <div 
            key={day}
            className={`day-card ${selectedDay === day ? 'selected' : ''} 
                       ${availabilities[day]?.length ? 'has-availability' : ''}`}
            onClick={() => setSelectedDay(day)}
          >
            <h3>{day}</h3>
            <div className="time-slots">
              {availabilities[day]?.map((slot, index) => (
                <div key={slot.id} className="time-slot">
                  <span>{formatTime(slot.start_time)} - {formatTime(slot.end_time)}</span>
                  <button 
                    className="delete-button"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(slot.id);
                    }}
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {selectedDay && (
        <form onSubmit={handleSubmit} className="time-form">
          <h3>Add time slot for {selectedDay}</h3>
          <div className="time-inputs">
            <div className="time-input-group">
              <label>Start Time:</label>
              <input
                type="time"
                value={timeForm.start_time}
                onChange={(e) => setTimeForm({...timeForm, start_time: e.target.value})}
                required
              />
            </div>
            <div className="time-input-group">
              <label>End Time:</label>
              <input
                type="time"
                value={timeForm.end_time}
                onChange={(e) => setTimeForm({...timeForm, end_time: e.target.value})}
                required
              />
            </div>
          </div>
          <button type="submit" className="save-button">Add Time Slot</button>
        </form>
      )}
    </div>
  );
};

export default AvailabilityManager;