// src/components/Login.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { loginUser } from '../services/api';
import { useTheme } from '../context/ThemeContext';
import '../styles/Login.css';

const Login = () => {
  const navigate = useNavigate();
  const { isDark } = useTheme();
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const data = await loginUser(formData.username, formData.password);
      if (data.token) {
        if (data.role === 'customer') {
          navigate('/customer-dashboard', { replace: true });
        } else if (data.role === 'business_owner') {
          navigate('/business-dashboard', { replace: true });
        } else {
          setError('Invalid user role');
        }
      } else {
        setError('Login failed - no token received');
      }
    } catch (err) {
      setError('Invalid credentials or server error');
    }
  };

  return (
    <div className={`login-container ${isDark ? 'dark-mode' : ''}`}>
      <div className="content-wrapper">
        <div className="logo-section">
          <div className="logo-container"> {/* Added container div */}
            <img 
              src="/logo.png" 
              alt="Appointment Management" 
              style={{ width: '400px', height: 'auto' }} // Added inline style
              className="logo"
            />
          </div>
          <h1 className="app-title">APPOINTMENT MANAGEMENT</h1>
          <p className="app-subtitle">Smart and swift, your time's best gift</p>
        </div>

        <div className="form-container">
          <form onSubmit={handleSubmit} className="login-form">
            {error && <div className="error-message">{error}</div>}
            
            <div className="input-group">
              <input
                type="text"
                placeholder="Username"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                required
                className="form-input"
              />
              <input
                type="password"
                placeholder="Password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                required
                className="form-input"
              />
            </div>

            <button type="submit" className="primary-button">
              Login
            </button>

            <div className="divider">
              <span>Don't have an account?</span>
            </div>

            <button
              type="button"
              onClick={() => navigate('/register')}
              className="secondary-button"
            >
              Register here
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login;