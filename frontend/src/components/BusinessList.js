// src/components/BusinessList.js
import React, { useState, useEffect } from 'react';
import { useTheme } from '../context/ThemeContext';
import '../styles/BusinessList.css';

const BusinessList = ({ onClose }) => {
  const { isDark } = useTheme();
  const [businesses, setBusinesses] = useState([]);
  const [selectedBusiness, setSelectedBusiness] = useState(null);
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [message, setMessage] = useState({ type: '', content: '' });
  const [appointmentData, setAppointmentData] = useState({
    date: '',
    start_time: '',
    title: '',
    customer_name: '',
    customer_phone: ''
  });

  const today = new Date().toISOString().split('T')[0];
  
  const timeSlots = Array.from({ length: 24 }, (_, hour) => 
    [`${hour.toString().padStart(2, '0')}:00`, `${hour.toString().padStart(2, '0')}:30`]
  ).flat();

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

  const fetchServices = async (businessId) => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/services/public/businesses/${businessId}/services`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );
      if (!response.ok) throw new Error('Failed to fetch services');
      const data = await response.json();
      setServices(data);
    } catch (error) {
      setError('Failed to load services');
    }
  };

  const fetchUserData = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/shared/me', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const userData = await response.json();
        setAppointmentData(prev => ({
          ...prev,
          customer_name: `${userData.first_name} ${userData.last_name}`,
          customer_phone: userData.phone
        }));
      }
    } catch (error) {
      console.error('Failed to fetch user data');
    }
  };

  const handleBusinessSelect = async (business) => {
    setSelectedBusiness(business);
    await fetchServices(business.id);
  };

  const handleCreateAppointment = async (e) => {
    e.preventDefault();
    setMessage({ type: '', content: '' });
    
    try {
      const response = await fetch(
        `http://localhost:8000/api/shared/appointments?business_id=${selectedBusiness.id}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify(appointmentData)
        }
      );

      const data = await response.json();
      
      if (!response.ok) {
        if (data.detail === 'Time slot not available' || 
            data.detail === 'Business not available' || 
            data.detail === 'Overlapping appointment') {
          setMessage({
            type: 'error',
            content: 'This time slot is not available. Please select a different time.'
          });
        } else {
          throw new Error(data.detail || 'Unable to create appointment');
        }
        return;
      }

      setMessage({
        type: 'success',
        content: 'Your appointment has been successfully scheduled!'
      });

      // Reset form after successful submission
      setTimeout(() => {
        setSelectedBusiness(null);
        setAppointmentData({
          date: '',
          start_time: '',
          title: '',
          customer_name: '',
          customer_phone: ''
        });
      }, 3000);

    } catch (error) {
      setMessage({
        type: 'error',
        content: error.message || 'Failed to create appointment. Please try again.'
      });
    }
  };

  const handleBack = () => {
    setSelectedBusiness(null);
    setError('');
    setMessage({ type: '', content: '' });
  };

  return (
    <div className={`business-list-container ${!isDark ? 'light-mode' : ''}`}>
      <div className="header">
        <h2>{selectedBusiness ? `Book with ${selectedBusiness.business_name}` : 'Available Businesses'}</h2>
        <button className="close-button" onClick={onClose}>×</button>
      </div>

      {!selectedBusiness ? (
        // Business List View
        <>
          <div className="search-bar">
            <input
              type="text"
              placeholder="Search businesses..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
          </div>

          <div className="businesses-grid">
            {businesses
              .filter(business => 
                business.business_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                business.services?.some(service => 
                  service.name.toLowerCase().includes(searchQuery.toLowerCase())
                )
              )
              .map(business => (
                <div key={business.id} className="business-card">
                  <h3>{business.business_name}</h3>
                  <p className="owner-name">{business.first_name} {business.last_name}</p>
                  <p className="services-count">{business.services?.length || 0} services available</p>
                  <button
                    className="book-button"
                    onClick={() => handleBusinessSelect(business)}
                  >
                    Book Appointment
                  </button>
                </div>
              ))}
          </div>
        </>
      ) : (
        // Appointment Booking View
        <div className="booking-form">
          <button className="back-button" onClick={handleBack}>
            ← Back to Businesses
          </button>

          {error && <div className="error-message">{error}</div>}

          <form onSubmit={handleCreateAppointment}>
            <div className="form-grid">
              <div className="form-group">
                <label>Date</label>
                <input
                  type="date"
                  min={today}
                  value={appointmentData.date}
                  onChange={(e) => setAppointmentData({
                    ...appointmentData,
                    date: e.target.value
                  })}
                  required
                />
              </div>

              <div className="form-group">
                <label>Time</label>
                <select
                  value={appointmentData.start_time}
                  onChange={(e) => setAppointmentData({
                    ...appointmentData,
                    start_time: e.target.value
                  })}
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
                value={appointmentData.title}
                onChange={(e) => setAppointmentData({
                  ...appointmentData,
                  title: e.target.value
                })}
                required
              >
                <option value="">Select a service</option>
                {services.map(service => (
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
                  value={appointmentData.customer_name}
                  onChange={(e) => setAppointmentData({
                    ...appointmentData,
                    customer_name: e.target.value
                  })}
                  required
                />
              </div>

              <div className="form-group">
                <label>Phone Number</label>
                <input
                  type="tel"
                  value={appointmentData.customer_phone}
                  onChange={(e) => setAppointmentData({
                    ...appointmentData,
                    customer_phone: e.target.value
                  })}
                  required
                />
              </div>
            </div>

            <button type="submit" className="submit-button">
              Create Appointment
            </button>

            {message && (
  <div className={`message-banner ${message.type}`}>
    {message.content}
  </div>
)}

            {message.content && (
              <div className={`message-banner ${message.type}`}>
                {message.content}
              </div>
            )}
          </form>
        </div>
      )}
    </div>
  );
};

export default BusinessList;