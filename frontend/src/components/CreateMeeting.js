// CreateMeeting.js
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

  // Create arrays for hours and minutes options
  const hours = Array.from({ length: 24 }, (_, i) => i.toString().padStart(2, '0'));
  const minutes = ['00', '10', '20', '30', '40', '50'];

  useEffect(() => {
    fetchServices();
    fetchUserData();
  }, [business.id]);

  const fetchServices = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/services/public/businesses/${business.id}/services`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) throw new Error('Failed to fetch services');
      const data = await response.json();
      setServices(data);
    } catch (error) {
      console.error('Service fetch error:', error);
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
      setFormData(prev => ({
        ...prev,
        customer_name: '',
        customer_phone: ''
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const response = await fetch(`http://localhost:8000/api/shared/appointments?business_id=${business.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();
      
      if (!response.ok) {
        if (typeof data.detail === 'string') {
          if (data.detail.includes('business hours')) {
            setError('This time slot is outside business hours. Please check their availability and try again.');
          } else if (data.detail.includes('conflict')) {
            setError('This time slot is not available. Please select another time.');
          } else {
            setError(data.detail);
          }
        } else if (data.detail?.business_hours) {
          setError(`Available hours: ${data.detail.business_hours.join(', ')}`);
        } else {
          setError('Failed to create appointment');
        }
        return;
      }

      setSuccess('Appointment created successfully!');
      setTimeout(() => {
        onClose();
      }, 2000);

    } catch (error) {
      console.error('Error:', error);
      setError('Failed to create appointment');
    }
  };

  return (
    <div className={`create-meeting ${!isDark ? 'light-mode' : ''}`}>
      <div className="close-button" onClick={onClose}>×</div>
      <h3>Create Appointment with {business.business_name || `${business.first_name} ${business.last_name}'s Business`}</h3>
      
      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}
      
      <form onSubmit={handleSubmit}>
        <input
          type="date"
          value={formData.date}
          onChange={(e) => setFormData({...formData, date: e.target.value})}
          min={new Date().toISOString().split('T')[0]}
          required
        />
        
        <div className="time-selection">
          <select
            value={formData.start_time.split(':')[0] || ''}
            onChange={(e) => {
              const hour = e.target.value;
              const currentMinutes = formData.start_time.split(':')[1] || '00';
              setFormData({...formData, start_time: `${hour}:${currentMinutes}`});
            }}
            required
          >
            <option value="">Hour</option>
            {hours.map(hour => (
              <option key={hour} value={hour}>{hour}</option>
            ))}
          </select>
          :
          <select
            value={formData.start_time.split(':')[1] || ''}
            onChange={(e) => {
              const currentHour = formData.start_time.split(':')[0] || '00';
              const minute = e.target.value;
              setFormData({...formData, start_time: `${currentHour}:${minute}`});
            }}
            required
          >
            <option value="">Min</option>
            {minutes.map(minute => (
              <option key={minute} value={minute}>{minute}</option>
            ))}
          </select>
        </div>
        
        <select
          value={formData.title}
          onChange={(e) => setFormData({...formData, title: e.target.value})}
          required
        >
          <option value="">Select a service</option>
          {services.map(service => (
            <option key={service.id} value={service.name}>
              {service.name} - ${service.price} - {service.duration} mins
            </option>
          ))}
        </select>
        
        <input
          type="text"
          placeholder="Your name"
          value={formData.customer_name}
          onChange={(e) => setFormData({...formData, customer_name: e.target.value})}
          readOnly={userDataLoaded}
          required
        />
        
        <input
          type="tel"
          placeholder="Your phone"
          value={formData.customer_phone}
          onChange={(e) => setFormData({...formData, customer_phone: e.target.value})}
          readOnly={userDataLoaded}
          required
        />
        
        <button type="submit">Create Appointment</button>
      </form>
    </div>
  );
};

export default CreateMeeting;