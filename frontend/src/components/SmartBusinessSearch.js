import React, { useState } from 'react';
import { Search, Calendar } from 'lucide-react';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const LLM_URL = process.env.REACT_APP_LLM_URL || 'http://localhost:8001';

const SmartBusinessSearch = () => {
 const [searchQuery, setSearchQuery] = useState('');
 const [results, setResults] = useState([]);
 const [loading, setLoading] = useState(false);
 const [error, setError] = useState('');

 const getAuthHeader = () => ({
   'Authorization': `Bearer ${localStorage.getItem('token')}`
 });

 const handleSearch = async (e) => {
   e.preventDefault();
   if (!searchQuery.trim()) return;
 
   try {
     setLoading(true);
     setError('');
     
     const businessesResponse = await fetch(`${API_URL}/api/services/public/businesses`, {
       headers: getAuthHeader()
     });
 
     if (!businessesResponse.ok) throw new Error('Failed to fetch businesses');
     const businesses = await businessesResponse.json();
 
     const llmResponse = await fetch(`${API_URL}/api/services/smart-service-search`, {
       method: 'POST',
       headers: { 
         'Content-Type': 'application/json',
         ...getAuthHeader()
       },
       body: JSON.stringify({ query: searchQuery.trim() })
     });
 
     if (!llmResponse.ok) throw new Error('Failed to analyze search');
     const result = await llmResponse.json();
     setResults(result.matches || []);
   } catch (err) {
     setError(err.message || 'Search failed');
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
           placeholder="What service are you looking for? (e.g., 'fix cracked phone screen')"
           className="w-full p-3 pr-10 border rounded-lg dark:bg-gray-800 
             dark:border-gray-700 focus:ring-2 focus:ring-blue-500"
         />
         <Search className="absolute right-3 top-3 text-gray-400" size={20} />
       </div>
       <button 
         type="submit"
         disabled={loading || !searchQuery.trim()}
         className={`px-6 py-3 rounded-lg font-medium flex items-center gap-2
           ${loading ? 'bg-gray-400' : 'bg-blue-600 hover:bg-blue-700'} 
           text-white transition-colors`}
       >
         {loading ? 'Searching...' : 'Search'}
       </button>
     </form>

     {error && (
       <div className="mb-6 p-4 bg-red-100 dark:bg-red-900/30 text-red-700 
         dark:text-red-200 rounded-lg">
         {error}
       </div>
     )}

     <div className="space-y-6">
       {results.length > 0 && (
         <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
           {results.map((business) => (
             <div key={business.id} className="bg-white dark:bg-gray-800 rounded-lg 
               shadow-md hover:shadow-lg transition-shadow p-6">
               <h3 className="text-lg font-semibold mb-2"
                 dangerouslySetInnerHTML={{
                   __html: highlightMatches(
                     business.business_name || `${business.first_name}'s Business`,
                     searchQuery
                   )
                 }}
               />
               <p className="text-gray-600 dark:text-gray-400 text-sm mb-4">
                 {business.first_name} {business.last_name}
               </p>
               
               {business.services?.length > 0 && (
                 <div className="space-y-3">
                   <h4 className="text-sm font-medium text-gray-900 
                     dark:text-gray-100">
                     Available Services:
                   </h4>
                   <ul className="space-y-2">
                     {business.services.map((service) => (
                       <li key={service.id} className="text-sm border-b 
                         dark:border-gray-700 pb-2">
                         <div dangerouslySetInnerHTML={{
                           __html: highlightMatches(service.name, searchQuery)
                         }} />
                         <div className="flex justify-between mt-1 
                           text-gray-600 dark:text-gray-400">
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
                 className="w-full mt-4 flex items-center justify-center gap-2 
                   py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg 
                   transition-colors"
               >
                 <Calendar size={16} />
                 Book Appointment
               </button>
             </div>
           ))}
         </div>
       )}
       
       {searchQuery.trim() && !loading && results.length === 0 && (
         <p className="text-center text-gray-600 dark:text-gray-400 py-8">
           No businesses found matching your search. Try different keywords!
         </p>
       )}
     </div>
   </div>
 );
};

export default SmartBusinessSearch;