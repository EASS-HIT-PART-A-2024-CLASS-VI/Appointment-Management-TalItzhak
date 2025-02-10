import React, { useState } from 'react';
import { MessageCircle } from 'lucide-react';
import '../styles/MessageModal.css';

const MessageModal = ({ businessId, businessName, onClose }) => {
  const [messageData, setMessageData] = useState({
    title: '',
    content: ''
  });
  const [isLoading, setIsLoading] = useState(false);
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
    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await fetch(`http://localhost:8000/api/messages/send/${businessId}`, {
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

      setSuccess('Message sent successfully!');
      setMessageData({ title: '', content: '' });
      setTimeout(() => {
        onClose();
      }, 2000);
    } catch (err) {
      setError('Failed to send message. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="business-list-container">
      <div className="content-section">
        <div className="header">
          <button className="back-button" onClick={onClose}>
            ← Back to Businesses
          </button>
          <h2>Message to {businessName}</h2>
        </div>

        <form onSubmit={handleSubmit} className="appointment-form">
          {error && <div className="error-message">{error}</div>}
          {success && <div className="success-message">{success}</div>}

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

          <button
            type="submit"
            className="submit-button"
            disabled={isLoading}
          >
            {isLoading ? 'Sending...' : 'Send Message'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default MessageModal;