import React, { useState, useEffect, useCallback } from 'react';
import { useTheme } from '../context/ThemeContext';
import '../styles/AppointmentsManager.css';

const AppointmentsManager = ({ onClose }) => {
 const { isDark } = useTheme();
 const [appointments, setAppointments] = useState([]);
 const [loading, setLoading] = useState(true);
 const [error, setError] = useState('');
 const [editingAppointment, setEditingAppointment] = useState(null);
 const [successMessage, setSuccessMessage] = useState('');
 const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

 const fetchAppointments = useCallback(async () => {
   try {
     const response = await fetch(`${API_URL}/api/business/my-appointments`, {
       headers: {
         'Authorization': `Bearer ${localStorage.getItem('token')}`
       }
     });
     
     if (!response.ok) {
       if (response.status === 404) {
         setAppointments([]);
         return;
       }
       throw new Error('Failed to fetch appointments');
     }
     
     const data = await response.json();
     const sortedAppointments = data.sort((a, b) => {
       const dateA = new Date(`${a.date} ${a.start_time}`);
       const dateB = new Date(`${b.date} ${b.start_time}`);
       return dateA - dateB;
     });
     
     setAppointments(sortedAppointments);
   } catch (error) {
     console.error('Error:', error);
     setError('Failed to load appointments');
   } finally {
     setLoading(false);
   }
 }, [API_URL]);

 useEffect(() => {
   fetchAppointments();
 }, [fetchAppointments]);

 const handleDelete = async (appointmentId) => {
   if (!window.confirm('Are you sure you want to delete this appointment?')) {
     return;
   }

   try {
     const response = await fetch(`${API_URL}/api/shared/appointments/${appointmentId}`, {
       method: 'DELETE',
       headers: {
         'Authorization': `Bearer ${localStorage.getItem('token')}`
       }
     });

     if (!response.ok) throw new Error('Failed to delete appointment');

     setAppointments(appointments.filter(apt => apt.id !== appointmentId));
     setSuccessMessage('Appointment deleted successfully');
     setTimeout(() => setSuccessMessage(''), 3000);
   } catch (error) {
     setError('Failed to delete appointment');
     setTimeout(() => setError(''), 3000);
   }
 };

 const handleUpdate = async (appointmentId, updatedData) => {
   try {
     const response = await fetch(`${API_URL}/api/shared/appointments/${appointmentId}`, {
       method: 'PUT',
       headers: {
         'Content-Type': 'application/json',
         'Authorization': `Bearer ${localStorage.getItem('token')}`
       },
       body: JSON.stringify(updatedData)
     });

     if (!response.ok) throw new Error('Failed to update appointment');

     setAppointments(appointments.map(apt => 
       apt.id === appointmentId ? { ...apt, ...updatedData } : apt
     ));
     setEditingAppointment(null);
     setSuccessMessage('Appointment updated successfully');
     setTimeout(() => setSuccessMessage(''), 3000);
   } catch (error) {
     setError('Failed to update appointment');
     setTimeout(() => setError(''), 3000);
   }
 };

 const formatDate = (dateString) => {
   return new Date(dateString).toLocaleDateString('en-US', {
     weekday: 'long',
     year: 'numeric',
     month: 'long',
     day: 'numeric'
   });
 };

 const formatTime = (timeString) => {
   return timeString.slice(0, 5);
 };

 const groupedAppointments = appointments.length > 0 
   ? appointments.reduce((groups, appointment) => {
       const date = appointment.date;
       if (!groups[date]) {
         groups[date] = [];
       }
       groups[date].push(appointment);
       return groups;
     }, {})
   : {};

 return (
   <div className={`appointments-manager ${!isDark ? 'light-mode' : ''}`}>
     <div className="manager-header">
       <h2>My Business Appointments</h2>
       <button className="close-button" onClick={onClose}>×</button>
     </div>
     
     {error && <div className="error-message">{error}</div>}
     {successMessage && <div className="success-message">{successMessage}</div>}
     
     {loading ? (
       <div className="loading">Loading appointments...</div>
     ) : appointments.length === 0 ? (
       <div className="no-appointments">No appointments scheduled</div>
     ) : (
       <div className="appointments-list">
         {Object.keys(groupedAppointments)
           .sort((a, b) => new Date(a) - new Date(b))
           .map(date => (
             <div key={date} className="date-group">
               <h3 className="date-header">{formatDate(date)}</h3>
               <div className="day-appointments">
                 {groupedAppointments[date].map(appointment => (
                   <div key={appointment.id} className="appointment-card">
                     {editingAppointment?.id === appointment.id ? (
                       <div className="edit-form">
                         <div className="form-group">
                           <label>Time:</label>
                           <input
                             type="time"
                             value={editingAppointment.start_time}
                             onChange={(e) => setEditingAppointment({
                               ...editingAppointment,
                               start_time: e.target.value
                             })}
                             step="600"
                             required
                           />
                         </div>
                         <div className="form-group">
                           <label>Notes:</label>
                           <input
                             type="text"
                             value={editingAppointment.notes || ''}
                             onChange={(e) => setEditingAppointment({
                               ...editingAppointment,
                               notes: e.target.value
                             })}
                             placeholder="Add notes"
                           />
                         </div>
                         <div className="edit-actions">
                           <button 
                             onClick={() => handleUpdate(appointment.id, editingAppointment)}
                             className="save-button"
                           >
                             Save Changes
                           </button>
                           <button 
                             onClick={() => setEditingAppointment(null)}
                             className="cancel-button"
                           >
                             Cancel
                           </button>
                         </div>
                       </div>
                     ) : (
                       <>
                         <div className="appointment-time">
                           {formatTime(appointment.start_time)}
                         </div>
                         <div className="appointment-details">
                           <h4>{appointment.title}</h4>
                           <div className="info-group">
                             <p className="customer-info">
                               <span>Customer:</span> {appointment.customer_name}
                             </p>
                             <p className="customer-info">
                               <span>Phone:</span> {appointment.customer_phone}
                             </p>
                           </div>
                           <div className="duration-cost">
                             <div><span>Duration:</span> {appointment.duration} min</div>
                             <div><span>Cost:</span> ${appointment.cost}</div>
                           </div>
                           {appointment.notes && (
                             <div className="notes">
                               <span>Notes:</span> {appointment.notes}
                             </div>
                           )}
                           <div className="appointment-actions">
                             <button 
                               onClick={() => setEditingAppointment(appointment)}
                               className="edit-button"
                             >
                               Edit
                             </button>
                             <button 
                               onClick={() => handleDelete(appointment.id)}
                               className="delete-button"
                             >
                               Delete
                             </button>
                           </div>
                         </div>
                       </>
                     )}
                   </div>
                 ))}
               </div>
             </div>
           ))}
       </div>
     )}
   </div>
 );
};

export default AppointmentsManager;