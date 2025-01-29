import React, { useState } from 'react';
import { Search, Calendar } from 'lucide-react';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const SmartBusinessSearch = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    try {
      setLoading(true);
      setError('');
      
      const searchResponse = await fetch(`${API_URL}/api/services/smart-service-search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: searchQuery.trim() })
      });

      if (!searchResponse.ok) {
        throw new Error('Search failed');
      }

      const data = await searchResponse.json();
      setResults(Array.isArray(data.matches) ? data.matches : []);
      
    } catch (err) {
      console.error('Search error:', err);
      setError(err.message || 'Search failed, please try again');
    } finally {
      setLoading(false);
    }
  };

  const highlightMatches = (text, searchTerms) => {
    if (!text || !searchTerms) return text;
    const terms = searchTerms.toLowerCase().split(' ');
    let result = text;
    terms.forEach(term => {
      if (term.length > 2) {
        const regex = new RegExp(`(${term})`, 'gi');
        result = result.replace(regex, '<mark>$1</mark>');
      }
    });
    return result;
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6">
      <form onSubmit={handleSearch} className="flex gap-4 mb-8">
        <div className="relative flex-1">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="What service are you looking for? (e.g., 'house cleaning', 'screen repair')"
            className="w-full p-3 pl-10 border rounded-lg dark:bg-gray-800 dark:border-gray-700 focus:ring-2 focus:ring-blue-500"
          />
          <Search className="absolute left-3 top-3 text-gray-400" size={20} />
        </div>
        <button 
          type="submit"
          disabled={loading || !searchQuery.trim()}
          className={`px-6 py-3 rounded-lg font-medium flex items-center gap-2
            ${loading ? 'bg-gray-400' : 'bg-blue-600 hover:bg-blue-700'} text-white transition-colors`}
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {error && (
        <div className="mb-6 p-4 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-200 rounded-lg">
          {error}
        </div>
      )}

      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {results && results.length > 0 ? (
            results.map((business) => (
              <div key={business.id} className="bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-shadow p-6">
                <h3 className="text-lg font-semibold mb-2"
                  dangerouslySetInnerHTML={{
                    __html: highlightMatches(
                      business.business_name || `${business.first_name} ${business.last_name}`,
                      searchQuery
                    )
                  }}
                />
                
                {business.services?.length > 0 && (
                  <div className="space-y-3">
                    <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100">
                      Available Services:
                    </h4>
                    <ul className="space-y-2">
                      {business.services.map((service) => (
                        <li key={service.id} className="text-sm border-b dark:border-gray-700 pb-2">
                          <div dangerouslySetInnerHTML={{
                            __html: highlightMatches(service.name, searchQuery)
                          }} />
                          <div className="flex justify-between mt-1 text-gray-600 dark:text-gray-400">
                            <span>${service.price}</span>
                            <span>{service.duration} min</span>
                          </div>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                <button 
                  onClick={() => {
                    const event = new CustomEvent('bookAppointment', {
                      detail: { businessId: business.id }
                    });
                    window.dispatchEvent(event);
                  }}
                  className="w-full mt-4 flex items-center justify-center gap-2 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                >
                  <Calendar size={16} />
                  Book Appointment
                </button>
              </div>
            ))
          ) : searchQuery.trim() && !loading ? (
            <div className="col-span-full text-center text-gray-600 dark:text-gray-400 py-8">
              No businesses found matching your search. Try different keywords!
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
};

export default SmartBusinessSearch;