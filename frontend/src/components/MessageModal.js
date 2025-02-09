// src/components/MessageModal.js
import React, { useState } from 'react';
import { useTheme } from '../context/ThemeContext';
import '../styles/MessageModal.css';

const MessageModal = ({ business, onClose }) => {
  const { isDark } = useTheme();
  const [messageData, setMessageData] = useState({
    title: '',
    content: ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const messageTypes = [
    "Rescheduling an Appointment",
    "Canceling an Appointment",
    "Questions About Services",
    "Payment and Billing Issues",
    "Other Inquiries"
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      const response = await fetch(`http://localhost:8000/api/messages/send/${business.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(messageData)
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to send message');
      }

      setSuccess('Message sent successfully!');
      setTimeout(() => {
        onClose();
      }, 1500);
    } catch (error) {
      setError(error.message);
    }
  };

  return (
    <div className={`modal-overlay ${!isDark ? 'light-mode' : ''}`}>
      <div className="modal-content">
        <div className="modal-header">
          <h3>Send Message to {business.business_name}</h3>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        <form onSubmit={handleSubmit} className="message-form">
          <div className="form-group">
            <label>Message Type</label>
            <select
              value={messageData.title}
              onChange={(e) => setMessageData({ ...messageData, title: e.target.value })}
              required
              className="form-input"
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
              onChange={(e) => setMessageData({ ...messageData, content: e.target.value })}
              required
              className="form-input message-textarea"
              placeholder="Write your message here..."
              rows={5}
            />
          </div>

          <button type="submit" className="submit-button">
            Send Message
          </button>
        </form>
      </div>
    </div>
  );
};

export default MessageModal;