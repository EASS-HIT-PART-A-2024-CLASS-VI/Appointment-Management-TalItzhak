import React, { useState, useEffect } from 'react';
import { useTheme } from '../context/ThemeContext';
import '../styles/MyAppointmentViewer.css';

const MyAppointmentViewer = ({ onClose }) => {
  const { isDark } = useTheme();
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  useEffect(() => {
    const fetchAppointments = async () => {
      try {
        const response = await fetch(`${API_URL}/api/shared/appointments/search-by-user`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          if (response.status === 404) {
            setAppointments([]);
            return;
          }
          throw new Error('Failed to fetch appointments');
        }
        
        const data = await response.json();
        // Sort appointments by date and time - closest first
        const sortedAppointments = data.sort((a, b) => {
          const dateA = new Date(`${a.date} ${a.start_time}`);
          const dateB = new Date(`${b.date} ${b.start_time}`);
          return dateA - dateB;
        });
        
        setAppointments(sortedAppointments);
      } catch (error) {
        console.error('Error:', error);
        setError('Failed to load appointments');
      } finally {
        setLoading(false);
      }
    };

    fetchAppointments();
  }, [API_URL]);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatTime = (timeString) => {
    return timeString.slice(0, 5);
  };

  // Group appointments by date after they're loaded
  const groupedAppointments = appointments.length > 0 
    ? appointments.reduce((groups, appointment) => {
        const date = appointment.date;
        if (!groups[date]) {
          groups[date] = [];
        }
        groups[date].push(appointment);
        return groups;
      }, {})
    : {};

  return (
    <div className={`appointments-viewer ${!isDark ? 'light-mode' : ''}`}>
      <div className="close-button" onClick={onClose}>×</div>
      
      <h2>My Appointments</h2>
      
      {error && <div className="error-message">{error}</div>}
      
      {loading ? (
        <div className="loading">Loading appointments...</div>
      ) : appointments.length === 0 ? (
        <div className="no-appointments">No appointments found</div>
      ) : (
        <div className="appointments-list">
          {Object.keys(groupedAppointments)
            .sort((a, b) => new Date(a) - new Date(b))
            .map(date => (
              <div key={date} className="date-group">
                <h3 className="date-header">{formatDate(date)}</h3>
                <div className="day-appointments">
                  {groupedAppointments[date].map(appointment => (
                    <div key={appointment.id} className="appointment-card">
                      <div className="appointment-time">
                        {formatTime(appointment.start_time)}
                      </div>
                      <div className="appointment-details">
                        <h4>{appointment.title}</h4>
                        <p className="service-type">
                          <span>Service Type:</span> {appointment.type}
                        </p>
                        <p className="business-info">
                          <span>Business:</span> {appointment.customer_name}
                        </p>
                        <div className="duration-cost">
                          <span>Duration: {appointment.duration}min</span>
                          <span>Cost: ${appointment.cost}</span>
                        </div>
                        <p className="phone">
                          <span>Phone:</span> {appointment.customer_phone}
                        </p>
                        {appointment.notes && (
                          <p className="notes">
                            <span>Notes:</span> {appointment.notes}
                          </p>
                        )}
                      </div>
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

export default MyAppointmentViewer;