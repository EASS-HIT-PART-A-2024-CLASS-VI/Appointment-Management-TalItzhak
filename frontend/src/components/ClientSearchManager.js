import React, { useState } from 'react';
import { useTheme } from '../context/ThemeContext';
import '../styles/ClientSearchManager.css';

const ClientSearchManager = ({ onClose }) => {
 const { isDark } = useTheme();
 const [searchResults, setSearchResults] = useState([]);
 const [loading, setLoading] = useState(false);
 const [error, setError] = useState('');
 const [phone, setPhone] = useState('');

 const handleSearch = async (e) => {
   e.preventDefault();
   try {
     setLoading(true);
     setError('');
     const response = await fetch(`http://localhost:8000/api/business/appointments/search/${phone}`, {
       headers: {
         'Authorization': `Bearer ${localStorage.getItem('token')}`
       }
     });

     if (!response.ok) {
       const data = await response.json();
       throw new Error(data.detail || 'Search failed');
     }
     
     const data = await response.json();
     // Sort appointments by date and time - closest first
     const sortedResults = data.sort((a, b) => {
       const dateA = new Date(`${a.date} ${a.start_time}`);
       const dateB = new Date(`${b.date} ${b.start_time}`);
       return dateA - dateB;
     });
     
     setSearchResults(sortedResults);
   } catch (error) {
     setError(error.message);
     setSearchResults([]);
   } finally {
     setLoading(false);
   }
 };

 const formatDate = (dateString) => {
   return new Date(dateString).toLocaleDateString('en-US', {
     year: 'numeric',
     month: 'long',
     day: 'numeric'
   });
 };

 const formatTime = (timeString) => {
   return timeString.slice(0, 5);
 };

 // Group appointments by date after they're loaded
 const groupedAppointments = searchResults.length > 0 
   ? searchResults.reduce((groups, appointment) => {
       const date = appointment.date;
       if (!groups[date]) {
         groups[date] = [];
       }
       groups[date].push(appointment);
       return groups;
     }, {})
   : {};

 return (
   <div className={`client-search-manager ${!isDark ? 'light-mode' : ''}`}>
     <div className="close-button" onClick={onClose}>×</div>
     
     <h2>Search Client Appointments</h2>

     <div className="search-container">
       <form onSubmit={handleSearch} className="search-form">
         <input
           type="text"
           placeholder="Phone Number"
           value={phone}
           onChange={(e) => setPhone(e.target.value)}
           required
         />
         <button type="submit" className="search-button">
           Search
         </button>
       </form>

       {error && <div className="error-message">{error}</div>}
       {loading && <div className="loading">Searching...</div>}

       {searchResults.length > 0 && (
         <div className="results-container">
           <h3>Search Results</h3>
           {Object.keys(groupedAppointments)
             .sort((a, b) => new Date(a) - new Date(b))
             .map(date => (
               <div key={date} className="date-group">
                 <h3 className="date-header">{formatDate(date)}</h3>
                 <div className="day-appointments">
                   {groupedAppointments[date].map(appointment => (
                     <div key={appointment.id} className="appointment-card">
                       <div className="appointment-header">
                         <div className="date-time">
                           <span className="time">{formatTime(appointment.start_time)}</span>
                           <span className="duration">{appointment.duration} minutes</span>
                         </div>
                       </div>
                       <div className="appointment-details">
                         <h4>{appointment.title}</h4>
                         <p className="customer-info">
                           <span>Client: </span>{appointment.customer_name}
                         </p>
                         <p className="customer-info">
                           <span>Phone: </span>{appointment.customer_phone}
                         </p>
                         <p className="price">
                           <span>Cost: </span>${appointment.cost}
                         </p>
                         {appointment.notes && (
                           <p className="notes">
                             <span>Notes: </span>{appointment.notes}
                           </p>
                         )}
                       </div>
                     </div>
                   ))}
                 </div>
               </div>
             ))}
         </div>
       )}
     </div>
   </div>
 );
};

export default ClientSearchManager;