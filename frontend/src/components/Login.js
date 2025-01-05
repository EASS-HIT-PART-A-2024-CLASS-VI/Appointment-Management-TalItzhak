import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { loginUser } from '../services/api';
import { useTheme } from '../context/ThemeContext';
import '../styles/Login.css';

const Login = () => {
  const navigate = useNavigate();
  const { isDark, toggleTheme } = useTheme();
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
    <div className={`login-container ${!isDark ? 'light-mode' : ''}`}>
      <div className="theme-button">
        <button onClick={toggleTheme} className="mode-toggle">
          {isDark ? 'Light Mode' : 'Dark Mode'}
        </button>
      </div>

      <div className="content-wrapper">
        <div className="info-section">
          <h2>Details about us</h2>
          <p>
            Welcome to our appointment scheduling platform. We help connect businesses with their clients efficiently and professionally.
          </p>
        </div>

        <div className="form-section">
          {/* Logo */}
          <div className="logo-container">
            <img src="/logo.png" alt="Platform Logo" className="logo" />
          </div>

          <form onSubmit={handleSubmit}>
            {error && <div className="error">{error}</div>}
            <div className="input-group">
              <input
                type="text"
                placeholder="Username"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                required
              />
              <input
                type="password"
                placeholder="Password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                required
              />
            </div>
            <button type="submit" className="login-button">
              Login
            </button>

            <div className="register-section">
              <p>Don't have an account?</p>
              <button
                type="button"
                onClick={() => navigate('/register')}
                className="register-button"
              >
                Register here
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login;