// BusinessList.js
import React, { useState, useEffect } from 'react';
import { useTheme } from '../context/ThemeContext';
import BusinessAvailability from './BusinessAvailability';
import CreateMeeting from './CreateMeeting';
import '../styles/BusinessList.css';

const BusinessList = ({ onClose }) => {
  const { isDark } = useTheme();
  const [businesses, setBusinesses] = useState([]);
  const [selectedBusiness, setSelectedBusiness] = useState(null);
  const [showAvailability, setShowAvailability] = useState(false);
  const [showCreateMeeting, setShowCreateMeeting] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchBusinesses();
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
      console.log('Businesses:', data); // Debug log
      setBusinesses(data);
    } catch (error) {
      console.error('Error:', error);
      setError('Failed to load businesses');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`business-list ${!isDark ? 'light-mode' : ''}`}>
      <div className="close-button" onClick={onClose}>×</div>

      <h2>Available Businesses</h2>

      {error && <div className="error-message">{error}</div>}

      {loading ? (
        <div className="loading">Loading businesses...</div>
      ) : (
        <div className="businesses-grid">
          {businesses.map((business) => (
            <div key={business.id} className="business-card">
              <h3 className="business-name">{business.business_name || 'Business Name Not Provided'}</h3>
              <p className="owner-name">
                {`${business.first_name} ${business.last_name}`}
              </p>
              <p className="business-details">
                {business.services?.length || 0} services available
              </p>
              <div className="business-actions">
                <button
                  className="action-button"
                  onClick={() => {
                    setSelectedBusiness(business);
                    setShowAvailability(true);
                  }}
                >
                  Show availability
                </button>
                <button
                  className="action-button"
                  onClick={() => {
                    setSelectedBusiness(business);
                    setShowCreateMeeting(true);
                  }}
                >
                  Create a meeting
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showAvailability && selectedBusiness && (
        <BusinessAvailability
          businessId={selectedBusiness.id}
          onClose={() => setShowAvailability(false)}
        />
      )}

      {showCreateMeeting && selectedBusiness && (
        <CreateMeeting
          business={selectedBusiness}
          onClose={() => setShowCreateMeeting(false)}
        />
      )}
    </div>
  );
};

export default BusinessList;
