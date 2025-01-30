import React, { useState } from 'react';
import { Search, Clock, DollarSign, Phone, User, X, Calendar } from 'lucide-react';
import '../styles/ClientSearchManager.css';

const ClientSearchManager = ({ onClose }) => {
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [phone, setPhone] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError('');
      const response = await fetch(`http://localhost:8000/api/business/appointments/search/${phone}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Search failed');
      }
      
      const data = await response.json();
      const sortedResults = data.sort((a, b) => {
        const dateA = new Date(`${a.date} ${a.start_time}`);
        const dateB = new Date(`${b.date} ${b.start_time}`);
        return dateA - dateB;
      });
      
      setSearchResults(sortedResults);
    } catch (error) {
      setError(error.message);
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  };

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

  const groupedAppointments = searchResults.reduce((groups, appointment) => {
    const date = appointment.date;
    if (!groups[date]) {
      groups[date] = [];
    }
    groups[date].push(appointment);
    return groups;
  }, {});

  return (
    <div className="client-search-manager">
      <button className="close-button" onClick={onClose}>
        <X size={20} />
      </button>
      
      <div className="header-search-section">
        <div className="title-section">
          <h2>Client Appointment History</h2>
        </div>

        <form onSubmit={handleSearch} className="search-form">
          <div className="search-input-container">
            <Phone className="search-icon" size={18} />
            <input
              type="text"
              placeholder="Enter phone number..."
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              required
            />
          </div>
          <button type="submit" className="search-button" disabled={loading}>
            <Search size={18} />
            {loading ? 'Searching...' : 'Search'}
          </button>
        </form>
      </div>

      <div className="appointments-container">
        {error && (
          <div className="error-message">
            <X size={16} />
            {error}
          </div>
        )}

        {Object.keys(groupedAppointments)
          .sort((a, b) => new Date(a) - new Date(b))
          .map(date => (
            <div key={date} className="date-group">
              <div className="date-header">
                <Calendar size={16} />
                <h3>{formatDate(date)}</h3>
              </div>
              
              <div className="appointments-timeline">
                {groupedAppointments[date].map(appointment => (
                  <div key={appointment.id} className="appointment-card">
                    <div className="appointment-time">
                      <Clock size={16} />
                      <span className="time">{formatTime(appointment.start_time)}</span>
                      <span className="duration">{appointment.duration} min</span>
                    </div>

                    <div className="appointment-content">
                      <h4 className="appointment-title">{appointment.title}</h4>
                      <div className="info-item">
                        <User size={16} />
                        <span>{appointment.customer_name}</span>
                      </div>
                      <div className="info-item">
                        <Phone size={16} />
                        <span>{appointment.customer_phone}</span>
                      </div>
                      <div className="info-item">
                        <DollarSign size={16} />
                        <span>${appointment.cost}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}

        {!loading && searchResults.length === 0 && phone && (
          <div className="no-results">
            <div className="no-results-icon">🔍</div>
            <h3>No appointments found</h3>
            <p>Try searching with a different phone number</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ClientSearchManager;