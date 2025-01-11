import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../styles/SmartBusinessSearch.css';

const SmartBusinessSearch = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!searchQuery.trim()) return;

    try {
      setLoading(true);
      setError('');
      
      const response = await axios({
        method: 'POST',
        url: 'http://localhost:8000/api/services/smart-service-search',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        data: {
          query: searchQuery.trim()
        }
      });

      if (response.data) {
        setResults(response.data);
      }
    } catch (err) {
      console.error('Search error:', err);
      setError(err.response?.data?.detail || 'Failed to perform search');
    } finally {
      setLoading(false);
    }
  };

  const highlightMatches = (text, searchTerms) => {
    const terms = searchTerms.toLowerCase().split(' ');
    let result = text;
    terms.forEach(term => {
      const regex = new RegExp(`(${term})`, 'gi');
      result = result.replace(regex, '<mark>$1</mark>');
    });
    return <span dangerouslySetInnerHTML={{ __html: result }} />;
  };

  return (
    <div className="smart-search">
      <form onSubmit={handleSearch} className="search-container">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="What service are you looking for? (e.g., 'fix phone screen')"
          className="search-input"
        />
        <button 
          type="submit"
          disabled={loading || !searchQuery.trim()}
          className="search-button"
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="results-container">
        {results.length > 0 ? (
          <>
            <h3>Found Services</h3>
            <div className="results-grid">
              {results.map((business) => (
                <div key={business.id} className="business-card">
                  <h4>{highlightMatches(business.business_name || `${business.first_name}'s Business`, searchQuery)}</h4>
                  <p className="owner-name">{business.first_name} {business.last_name}</p>
                  
                  {business.services?.length > 0 && (
                    <div className="services-list">
                      <h5>Matching Services:</h5>
                      <ul>
                        {business.services.map((service) => (
                          <li key={service.id} className="service-item">
                            <div className="service-name">
                              {highlightMatches(service.name, searchQuery)}
                            </div>
                            <div className="service-details">
                              <span className="service-price">${service.price}</span>
                              <span className="service-duration">{service.duration} min</span>
                            </div>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  <button 
                    onClick={() => navigate(`/create-meeting/${business.id}`)}
                    className="book-button"
                  >
                    Book Appointment
                  </button>
                </div>
              ))}
            </div>
          </>
        ) : searchQuery.trim() && !loading && (
          <p className="no-results">No businesses found matching your search. Try different keywords!</p>
        )}
      </div>
    </div>
  );
};

export default SmartBusinessSearch;