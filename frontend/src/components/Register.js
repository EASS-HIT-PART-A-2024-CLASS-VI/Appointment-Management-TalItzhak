// src/components/Register.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { registerUser } from '../services/api';
import { useTheme } from '../context/ThemeContext';
import '../styles/Register.css';

const Register = () => {
  const navigate = useNavigate();
  const { isDark } = useTheme();
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    username: '',
    phone: '',
    password: '',
    role: '',
    businessName: ''
  });
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.role) {
      setError('Please select a role');
      return;
    }
    try {
      await registerUser({
        first_name: formData.firstName,
        last_name: formData.lastName,
        username: formData.username,
        phone: formData.phone,
        password: formData.password,
        role: formData.role,
        business_name: formData.role === 'business_owner' ? formData.businessName : null
      });
      navigate('/login');
    } catch (err) {
      setError('Registration failed. Please try again.');
    }
  };

  return (
    <div className={`register-container ${!isDark ? 'light-mode' : ''}`}>
      <div className="content-wrapper">
        <div className="logo-section">
          <img 
            src="/logo.png" 
            alt="Appointment Management" 
            className="logo"
          />
          <h1 className="app-title">Appointment Management</h1>
          <p className="app-subtitle">Smart and swift, your time's best gift</p>
        </div>

        <div className="main-content">
          <div className="form-section">
            <form onSubmit={handleSubmit}>
              {error && <div className="error">{error}</div>}
              <div className="input-group">
                <div className="name-row">
                  <input
                    type="text"
                    placeholder="First Name"
                    value={formData.firstName}
                    onChange={(e) => setFormData({...formData, firstName: e.target.value})}
                    required
                    className="form-input"
                  />
                  <input
                    type="text"
                    placeholder="Last Name"
                    value={formData.lastName}
                    onChange={(e) => setFormData({...formData, lastName: e.target.value})}
                    required
                    className="form-input"
                  />
                </div>

                <input
                  type="text"
                  placeholder="Username"
                  value={formData.username}
                  onChange={(e) => setFormData({...formData, username: e.target.value})}
                  required
                  className="form-input"
                />

                <input
                  type="tel"
                  placeholder="Phone"
                  value={formData.phone}
                  onChange={(e) => setFormData({...formData, phone: e.target.value})}
                  required
                  className="form-input"
                />

                <input
                  type="password"
                  placeholder="Password"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  required
                  className="form-input"
                />
              </div>

              <div className="role-buttons">
                <button
                  type="button"
                  className={`role-button ${formData.role === 'customer' ? 'active' : ''}`}
                  onClick={() => setFormData({...formData, role: 'customer'})}
                >
                  Client
                </button>
                <button
                  type="button"
                  className={`role-button ${formData.role === 'business_owner' ? 'active' : ''}`}
                  onClick={() => setFormData({...formData, role: 'business_owner'})}
                >
                  Business Owner
                </button>
              </div>

              {formData.role === 'business_owner' && (
                <div className="input-group">
                  <input
                    type="text"
                    placeholder="Business Name"
                    value={formData.businessName}
                    onChange={(e) => setFormData({...formData, businessName: e.target.value})}
                    required
                    className="form-input"
                  />
                </div>
              )}

              <button type="submit" className="primary-button">
                Register
              </button>

              <div className="divider">
                <span>Already have an account?</span>
              </div>

              <button
                type="button"
                onClick={() => navigate('/login')}
                className="secondary-button"
              >
                Login here
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;