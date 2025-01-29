import React, { useState, useEffect } from 'react';
import { useTheme } from '../context/ThemeContext';
import '../styles/CreateMeeting.css';

const CreateMeeting = ({ business, onClose }) => {
  const { isDark } = useTheme();
  const [services, setServices] = useState([]);
  const [formData, setFormData] = useState({
    date: '',
    start_time: '',
    title: '',
    customer_name: '',
    customer_phone: ''
  });
  const [userDataLoaded, setUserDataLoaded] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Get today's date in YYYY-MM-DD format
  const today = new Date().toISOString().split('T')[0];
  
  // Create time slots in 30-minute intervals
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

  useEffect(() => {
    fetchServices();
    fetchUserData();
  }, [business.id]);

  const fetchServices = async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/services/public/businesses/${business.id}/services`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
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
      
      if (!response.ok) throw new Error('Failed to fetch user data');
      
      const userData = await response.json();
      setFormData(prev => ({
        ...prev,
        customer_name: `${userData.first_name} ${userData.last_name}`,
        customer_phone: userData.phone
      }));
      setUserDataLoaded(true);
    } catch (error) {
      console.error('User data fetch error:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    
    try {
      const response = await fetch(
        `http://localhost:8000/api/shared/appointments?business_id=${business.id}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify(formData)
        }
      );

      const data = await response.json();
      
      if (!response.ok) {
        if (data.detail === 'Time slot not available') {
          throw new Error('The selected time is not available. Please choose another time.');
        } else if (data.detail === 'Business not available') {
          throw new Error('Business is not available during these hours. Please select a different time.');
        } else if (data.detail === 'Overlapping appointment') {
          throw new Error('There is another appointment at this time. Please select a different time.');
        } else {
          throw new Error(data.detail || 'Unable to create appointment. Please try again.');
        }
      }

      setSuccess('Appointment created successfully!');
      setTimeout(() => {
        onClose();
      }, 2000);

    } catch (error) {
      setError(error.message);
    }
  };

  return (
    <div className={`create-meeting-modal ${!isDark ? 'light-mode' : ''}`}>
      <div className="modal-header">
        <h3>Create Appointment with {business.business_name}</h3>
        <button className="close-button" onClick={onClose}>×</button>
      </div>

      {error && (
        <div className="alert alert-error">
          {error}
        </div>
      )}

      {success && (
        <div className="alert alert-success">
          {success}
        </div>
      )}

      <form onSubmit={handleSubmit} className="appointment-form">
        <div className="form-grid">
          <div className="form-group">
            <label>Date</label>
            <input
              type="date"
              value={formData.date}
              onChange={(e) => setFormData({...formData, date: e.target.value})}
              min={today}
              required
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label>Time</label>
            <select
              value={formData.start_time}
              onChange={(e) => setFormData({...formData, start_time: e.target.value})}
              required
              className="form-input"
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
            className="form-input"
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
              value={formData.customer_name}
              onChange={(e) => setFormData({...formData, customer_name: e.target.value})}
              readOnly={userDataLoaded}
              required
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label>Phone Number</label>
            <input
              type="tel"
              value={formData.customer_phone}
              onChange={(e) => setFormData({...formData, customer_phone: e.target.value})}
              readOnly={userDataLoaded}
              required
              className="form-input"
            />
          </div>
        </div>

        <button type="submit" className="submit-button">
          Create Appointment
        </button>
      </form>
    </div>
  );
};

export default CreateMeeting;