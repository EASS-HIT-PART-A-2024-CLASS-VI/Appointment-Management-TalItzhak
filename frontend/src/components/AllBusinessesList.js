import React, { useState, useEffect } from 'react';
import { useTheme } from '../context/ThemeContext';
import '../styles/BusinessList.css';

const AllBusinessesList = ({ onClose }) => {
  const { isDark } = useTheme();
  const [businesses, setBusinesses] = useState([]);
  const [selectedBusiness, setSelectedBusiness] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [availability, setAvailability] = useState([]);

  useEffect(() => {
    fetchBusinesses();
  }, []);

  const fetchBusinesses = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/services/public/businesses', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch businesses');
      }
      
      const data = await response.json();
      setBusinesses(Array.isArray(data) ? data : []);
      
    } catch (error) {
      console.error('Error fetching businesses:', error);
      setError('Failed to load businesses');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e?.preventDefault(); 
    
    if (!searchQuery.trim()) {
      fetchBusinesses();
      return;
    }

    try {
      setLoading(true);
      setError('');
      const response = await fetch('http://localhost:8000/api/services/smart-service-search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ query: searchQuery.trim() })
      });

      if (!response.ok) {
        throw new Error('Search failed');
      }
      
      const data = await response.json();
      setBusinesses(data.matches || []); 
      
    } catch (error) {
      console.error('Search error:', error);
      setError('Search failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fetchAvailability = async (businessId) => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/availability/business/${businessId}/availability`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch availability');
      }
      
      const data = await response.json();
      setAvailability(data.availability || []);
      
    } catch (error) {
      console.error('Availability error:', error);
      setError('Failed to load availability');
    } finally {
      setLoading(false);
    }
  };

  const handleViewAvailability = async (business) => {
    setSelectedBusiness(business);
    await fetchAvailability(business.id);
  };

  return (
    <div className={`business-list-container ${!isDark ? 'light-mode' : ''} ${selectedBusiness ? 'show-form' : ''}`}>
      <div className="content-section businesses-section">
        <div className="header">
          <h2>Available Businesses</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSearch} className="search-container">
          <input
            type="text"
            placeholder="What service are you looking for? (e.g., 'I need a haircut')"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
          <button type="submit" className="search-button">
            Search
          </button>
        </form>

        {error && <div className="error-message">{error}</div>}

        {loading ? (
          <div className="loading">Loading businesses...</div>
        ) : businesses.length > 0 ? (
          <div className="businesses-grid">
            {businesses.map((business) => (
              <div key={business.id} className="business-card">
                <div className="business-info">
                  <h3>{business.business_name || `${business.first_name}'s Business`}</h3>
                  <p className="owner-name">{business.first_name} {business.last_name}</p>
                  <p className="services-count">
                    {business.services?.length || 0} services available
                  </p>
                </div>
                <button
                  className="action-button availability-button"
                  onClick={() => handleViewAvailability(business)}
                >
                  Show Availability
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="no-results">
            {searchQuery.trim() ? 'No businesses found matching your search' : 'No businesses available'}
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
              <h2>{selectedBusiness.business_name || `${selectedBusiness.first_name}'s Business`}'s Availability</h2>
            </div>

            <div className="availability-content">
              {availability.length > 0 ? (
                <div className="availability-grid">
                  {availability.map((slot, index) => (
                    <div key={index} className="availability-slot">
                      <h3 className="day-name">{slot.day_of_week}</h3>
                      <div className="time-range">
                        <span>{slot.start_time?.slice(0, 5)}</span>
                        <span> - </span>
                        <span>{slot.end_time?.slice(0, 5)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="no-availability">
                  No availability set for this business
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default AllBusinessesList;