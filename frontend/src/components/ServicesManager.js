import React, { useState, useEffect } from 'react';
import { useTheme } from '../context/ThemeContext';
import '../styles/ServicesManager.css';

const ServicesManager = ({ onClose }) => {
  const { isDark } = useTheme();
  const [services, setServices] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [formData, setFormData] = useState({
    name: '',
    duration: '',
    price: ''
  });

  useEffect(() => {
    fetchServices();
  }, []);

  const fetchServices = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/services/my-services', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (!response.ok) throw new Error('Failed to fetch services');
      
      const data = await response.json();
      setServices(data);
    } catch (error) {
      setError('Failed to load services');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/api/services/services', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          name: formData.name,
          duration: parseInt(formData.duration),
          price: parseInt(formData.price)
        })
      });

      if (!response.ok) throw new Error('Failed to create service');

      setSuccess('Service created successfully');
      setFormData({ name: '', duration: '', price: '' });
      fetchServices();
    } catch (error) {
      setError('Failed to create service');
    }
  };

  const handleDelete = async (serviceId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/services/services/${serviceId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) throw new Error('Failed to delete service');

      setSuccess('Service deleted successfully');
      fetchServices();
    } catch (error) {
      setError('Failed to delete service');
    }
  };

  return (
    <div className={`services-manager ${!isDark ? 'light-mode' : ''}`}>
      <div className="close-button" onClick={onClose}>×</div>
      
      <h2>Manage Your Services</h2>
      
      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      <div className="services-container">
        <div className="services-list">
          <h3>Your Current Services</h3>
          {services.length === 0 ? (
            <p className="no-services">No services created yet</p>
          ) : (
            services.map(service => (
              <div key={service.id} className="service-card">
                <div className="service-info">
                  <h4>{service.name}</h4>
                  <div className="service-details">
                    <span>Duration: {service.duration} minutes</span>
                    <span>Price: ${service.price}</span>
                  </div>
                </div>
                <button 
                  className="delete-button"
                  onClick={() => handleDelete(service.id)}
                  aria-label="Delete service"
                >
                  ×
                </button>
              </div>
            ))
          )}
        </div>

        <div className="service-form">
          <h3>Add New Service</h3>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Service Name:</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                placeholder="e.g., Haircut"
                required
              />
            </div>

            <div className="form-group">
              <label>Duration (minutes):</label>
              <input
                type="number"
                value={formData.duration}
                onChange={(e) => setFormData({...formData, duration: e.target.value})}
                placeholder="e.g., 30"
                min="1"
                required
              />
            </div>

            <div className="form-group">
              <label>Price ($):</label>
              <input
                type="number"
                value={formData.price}
                onChange={(e) => setFormData({...formData, price: e.target.value})}
                placeholder="e.g., 50"
                min="0"
                required
              />
            </div>

            <button type="submit" className="submit-button">
              Add Service
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ServicesManager;