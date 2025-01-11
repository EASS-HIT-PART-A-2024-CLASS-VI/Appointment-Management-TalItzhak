// src/components/BookAppointmentList.js
import React, { useState, useEffect } from 'react';
import { useTheme } from '../context/ThemeContext';
import '../styles/BusinessList.css';

const BookAppointmentList = ({ onClose }) => {
  const { isDark } = useTheme();
  const [businesses, setBusinesses] = useState([]);
  const [selectedBusiness, setSelectedBusiness] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    date: '',
    start_time: '',
    title: '',
    customer_name: '',
    customer_phone: ''
  });

  useEffect(() => {
    fetchBusinesses();
    fetchUserData();
  }, []);

  const fetchBusinesses = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/services/public/businesses', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (!response.ok) throw new Error('Failed to fetch businesses');
      const data = await response.json();
      setBusinesses(data);
    } catch (error) {
      setError('Failed to load businesses');
    } finally {
      setLoading(false);
    }
  };

  const fetchUserData = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/shared/me', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const userData = await response.json();
      setFormData(prev => ({
        ...prev,
        customer_name: `${userData.first_name} ${userData.last_name}`,
        customer_phone: userData.phone
      }));
    } catch (error) {
      console.error('Failed to fetch user data');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(
        `http://localhost:8000/api/shared/appointments?business_id=${selectedBusiness.id}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify(formData)
        }
      );

      if (!response.ok) throw new Error('Failed to create appointment');
      
      setSelectedBusiness(null);
      alert('Appointment created successfully!');
      onClose();
    } catch (error) {
      setError(error.message);
    }
  };

  // Generate time slots
  const generateTimeSlots = () => {
    const slots = [];
    for (let hour = 8; hour < 20; hour++) {
      for (let minute of ['00', '30']) {
        slots.push(`${hour.toString().padStart(2, '0')}:${minute}`);
      }
    }
    return slots;
  };

  const timeSlots = generateTimeSlots();
  const today = new Date().toISOString().split('T')[0];

  return (
    <div className={`business-list-container ${!isDark ? 'light-mode' : ''} ${selectedBusiness ? 'show-form' : ''}`}>
      <div className="content-section businesses-section">
        <div className="header">
          <h2>Book an Appointment</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        {error && <div className="error-message">{error}</div>}

        {loading ? (
          <div className="loading">Loading businesses...</div>
        ) : (
          <div className="businesses-grid">
            {businesses.map((business) => (
              <div key={business.id} className="business-card">
                <div className="business-info">
                  <h3>{business.business_name}</h3>
                  <p className="owner-name">{business.first_name} {business.last_name}</p>
                  <p className="services-count">{business.services?.length || 0} services available</p>
                </div>
                <button
                  className="action-button book-button"
                  onClick={() => setSelectedBusiness(business)}
                >
                  Book Appointment
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="content-section form-section">
        {selectedBusiness && (
          <>
            <div className="header">
              <button className="back-button" onClick={() => setSelectedBusiness(null)}>
                ← Back to Businesses
              </button>
              <h2>Book with {selectedBusiness.business_name}</h2>
            </div>

            <form onSubmit={handleSubmit} className="appointment-form">
              <div className="form-grid">
                <div className="form-group">
                  <label>Date</label>
                  <input
                    type="date"
                    min={today}
                    value={formData.date}
                    onChange={(e) => setFormData({...formData, date: e.target.value})}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Time</label>
                  <select
                    value={formData.start_time}
                    onChange={(e) => setFormData({...formData, start_time: e.target.value})}
                    required
                  >
                    <option value="">Select time</option>
                    {timeSlots.map(time => (
                      <option key={time} value={time}>{time}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label>Service</label>
                <select
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  required
                >
                  <option value="">Select a service</option>
                  {selectedBusiness.services?.map(service => (
                    <option key={service.id} value={service.name}>
                      {service.name} - ${service.price} - {service.duration} mins
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-grid">
                <div className="form-group">
                  <label>Your Name</label>
                  <input
                    type="text"
                    value={formData.customer_name}
                    onChange={(e) => setFormData({...formData, customer_name: e.target.value})}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Phone Number</label>
                  <input
                    type="tel"
                    value={formData.customer_phone}
                    onChange={(e) => setFormData({...formData, customer_phone: e.target.value})}
                    required
                  />
                </div>
              </div>

              <button type="submit" className="submit-button">
                Create Appointment
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  );
};

export default BookAppointmentList;