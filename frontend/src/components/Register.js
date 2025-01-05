import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { registerUser } from '../services/api';
import { useTheme } from '../context/ThemeContext';
import '../styles/Register.css';

const Register = () => {
  const navigate = useNavigate();
  const { isDark, toggleTheme } = useTheme();
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
      <div className="theme-button">
        <button onClick={toggleTheme} className="mode-toggle">
          {isDark ? '☀️ Light Mode' : '🌙 Dark Mode'}
        </button>
      </div>

      <div className="content-wrapper">
        <div className="info-section">
          <h2>Details about us</h2>
          <p>Welcome to our appointment scheduling platform. We help connect businesses with their clients efficiently and professionally.</p>
        </div>
        
        <div className="form-section">
          <form onSubmit={handleSubmit}>
            {error && <div className="error">{error}</div>}
            <div className="input-group">
              <div className="name-row">
                <input
                  type="text"
                  placeholder="FirstName"
                  value={formData.firstName}
                  onChange={(e) => setFormData({...formData, firstName: e.target.value})}
                  required
                />
                <input
                  type="text"
                  placeholder="LastName" 
                  value={formData.lastName}
                  onChange={(e) => setFormData({...formData, lastName: e.target.value})}
                  required
                />
              </div>

              <input
                type="text"
                placeholder="Username"
                value={formData.username}
                onChange={(e) => setFormData({...formData, username: e.target.value})}
                required
              />

              <input
                type="tel"
                placeholder="Phone"
                value={formData.phone}
                onChange={(e) => setFormData({...formData, phone: e.target.value})}
                required
              />

              <input
                type="password"
                placeholder="Password"
                value={formData.password}
                onChange={(e) => setFormData({...formData, password: e.target.value})}
                required
              />
            </div>

            <div className="role-buttons">
              <button
                type="button"
                className={formData.role === 'customer' ? 'active' : ''}
                onClick={() => setFormData({...formData, role: 'customer'})}
              >
                Client
              </button>
              <button
                type="button" 
                className={formData.role === 'business_owner' ? 'active' : ''}
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
                />
              </div>
            )}

            <button type="submit" className="register-button">Register</button>
            
            <div className="login-section">
              <p>Already have an account?</p>
              <button 
                type="button" 
                onClick={() => navigate('/login')} 
                className="login-link"
              >
                Login here
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Register;