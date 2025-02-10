import React, { useState, useEffect } from 'react';
import { useTheme } from '../context/ThemeContext';
import { MessageCircle } from 'lucide-react';
import '../styles/BusinessList.css';

const BookAppointmentList = ({ onClose }) => {
  const { isDark } = useTheme();
  const [businesses, setBusinesses] = useState([]);
  const [selectedBusiness, setSelectedBusiness] = useState(null);
  const [showMessageForm, setShowMessageForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [formMessage, setFormMessage] = useState({ type: '', content: '' });
  const [formData, setFormData] = useState({
    date: '',
    start_time: '',
    title: '',
    customer_name: '',
    customer_phone: ''
  });
  const [messageData, setMessageData] = useState({
    title: '',
    content: ''
  });

  useEffect(() => {
    fetchBusinesses();
    fetchUserData();
  }, []);

  // Keep all your existing fetch functions and handlers...
  const fetchBusinesses = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/services/public/businesses', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (!response.ok) throw new Error('Failed to fetch businesses');
      const data = await response.json();
      setBusinesses(data);
    } catch (error) {
      setError('Failed to load businesses');
    } finally {
      setLoading(false);
    }
  };

  const fetchUserData = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/shared/me', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const userData = await response.json();
      setFormData(prev => ({
        ...prev,
        customer_name: `${userData.first_name} ${userData.last_name}`,
        customer_phone: userData.phone
      }));
    } catch (error) {
      console.error('Failed to fetch user data');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormMessage({ type: '', content: '' });
    
    try {
      const response = await fetch(
        `http://localhost:8000/api/shared/appointments?business_id=${selectedBusiness.id}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify(formData)
        }
      );

      const data = await response.json();
      
      if (!response.ok) {
        const errorMessage = typeof data.detail === 'string' 
          ? data.detail 
          : 'Appointment cannot be scheduled at this time. Please select different hours.';
          
        setFormMessage({
          type: 'error',
          content: errorMessage
        });
        return;
      }
      
      setFormMessage({
        type: 'success',
        content: 'Appointment created successfully!'
      });

      setTimeout(() => {
        setSelectedBusiness(null);
        onClose();
      }, 2000);

    } catch (error) {
      setFormMessage({
        type: 'error',
        content: 'Failed to create appointment. Please try again later.'
      });
    }
  };

  const handleMessageSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`http://localhost:8000/api/messages/send/${selectedBusiness.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(messageData)
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      setFormMessage({
        type: 'success',
        content: 'Message sent successfully!'
      });

      setTimeout(() => {
        setShowMessageForm(false);
        setSelectedBusiness(null);
        setMessageData({ title: '', content: '' });
      }, 2000);
    } catch (error) {
      setFormMessage({
        type: 'error',
        content: 'Failed to send message. Please try again.'
      });
    }
  };

  const generateTimeSlots = () => {
    const slots = [];
    for (let hour = 6; hour < 22; hour++) {
      for (let minute = 0; minute < 60; minute += 10) {  
        slots.push(
          `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`
        );
      }
    }
    return slots;
  };

  const timeSlots = generateTimeSlots();
  const today = new Date().toISOString().split('T')[0];

  const messageTypes = [
    "Rescheduling an Appointment",
    "Canceling an Appointment",
    "Questions About Services",
    "Payment and Billing Issues",
    "Other Inquiries"
  ];

  return (
    <div className={`business-list-container ${!isDark ? 'light-mode' : ''} ${selectedBusiness ? 'show-form' : ''} ${showMessageForm ? 'show-message' : ''}`}>
      <div className="content-section businesses-section">
        <div className="header">
          <h2>Book an Appointment</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        {error && <div className="error-message">{error}</div>}

        {loading ? (
          <div className="loading">Loading businesses...</div>
        ) : (
          <div className="businesses-grid">
            {businesses.map((business) => (
              <div key={business.id} className="business-card">
                <div className="business-info">
                  <h3>{business.business_name}</h3>
                  <div className="owner-info">
                    <p className="owner-name">{business.first_name} {business.last_name}</p>
                    <button 
                      className="message-button"
                      onClick={() => {
                        setSelectedBusiness(business);
                        setShowMessageForm(true);
                      }}
                    >
                      <MessageCircle size={14} />
                      Message
                    </button>
                  </div>
                  <p className="services-count">{business.services?.length || 0} services available</p>
                </div>
                <button
                  className="action-button book-button"
                  onClick={() => setSelectedBusiness(business)}
                >
                  Book Appointment
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Appointment Form Section */}
      <div className="content-section form-section">
        {selectedBusiness && !showMessageForm && (
          <>
            <div className="header">
              <button className="back-button" onClick={() => setSelectedBusiness(null)}>
                ← Back to Businesses
              </button>
              <h2>Book with {selectedBusiness.business_name}</h2>
            </div>

            <form onSubmit={handleSubmit} className="appointment-form">
              {/* Your existing appointment form fields... */}
              <div className="form-grid">
                <div className="form-group">
                  <label>Date</label>
                  <input
                    type="date"
                    min={today}
                    value={formData.date}
                    onChange={(e) => setFormData({...formData, date: e.target.value})}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Time</label>
                  <select
                    value={formData.start_time}
                    onChange={(e) => setFormData({...formData, start_time: e.target.value})}
                    required
                  >
                    <option value="">Select time</option>
                    {timeSlots.map(time => (
                      <option key={time} value={time}>{time}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label>Service</label>
                <select
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  required
                >
                  <option value="">Select a service</option>
                  {selectedBusiness.services?.map(service => (
                    <option key={service.id} value={service.name}>
                      {service.name} - ${service.price} - {service.duration} mins
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-grid">
                <div className="form-group">
                  <label>Your Name</label>
                  <input
                    type="text"
                    value={formData.customer_name}
                    onChange={(e) => setFormData({...formData, customer_name: e.target.value})}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Phone Number</label>
                  <input
                    type="tel"
                    value={formData.customer_phone}
                    onChange={(e) => setFormData({...formData, customer_phone: e.target.value})}
                    required
                  />
                </div>
              </div>

              <button type="submit" className="submit-button">
                Create Appointment
              </button>

              {formMessage.content && (
                <div className={`message-banner ${formMessage.type}`}>
                  {formMessage.content}
                </div>
              )}
            </form>
          </>
        )}
      </div>

      {/* Message Form Section */}
      <div className="content-section message-form-section">
        {selectedBusiness && showMessageForm && (
          <>
            <div className="header">
              <button 
                className="back-button" 
                onClick={() => {
                  setShowMessageForm(false);
                  setSelectedBusiness(null);
                }}
              >
                ← Back to Businesses
              </button>
              <h2>Message to {selectedBusiness.business_name}</h2>
            </div>

            <form onSubmit={handleMessageSubmit} className="appointment-form">
              <div className="form-group">
                <label>Message Type</label>
                <select
                  value={messageData.title}
                  onChange={(e) => setMessageData({...messageData, title: e.target.value})}
                  required
                >
                  <option value="">Select a message type</option>
                  {messageTypes.map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Message</label>
                <textarea
                  value={messageData.content}
                  onChange={(e) => setMessageData({...messageData, content: e.target.value})}
                  placeholder="Write your message here..."
                  required
                  maxLength={1000}
                />
                <span className="character-count">
                  {messageData.content.length}/1000 characters
                </span>
              </div>

              <button type="submit" className="submit-button">
                Send Message
              </button>

              {formMessage.content && (
                <div className={`message-banner ${formMessage.type}`}>
                  {formMessage.content}
                </div>
              )}
            </form>
          </>
        )}
      </div>
    </div>
  );
};

export default BookAppointmentList;