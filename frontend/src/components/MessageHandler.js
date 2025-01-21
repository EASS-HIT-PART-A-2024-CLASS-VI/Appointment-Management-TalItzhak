import React, { useState } from 'react';
import { useTheme } from '../context/ThemeContext';
import { MessageCircle } from 'lucide-react';
import '../styles/MessageHandler.css';

const MessageHandler = ({ appointmentId, appointmentDetails, onClose }) => {
  const { isDark } = useTheme();
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      // Get current user info for customerId
      const userResponse = await fetch('http://localhost:8000/api/shared/me', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const userData = await userResponse.json();

      const response = await fetch('http://localhost:8001/api/customer-service/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          message: message,
          customerId: userData.id.toString(),  // Make sure it's a string
          businessId: appointmentDetails.business_id.toString(), // Make sure it's a string
          context: {
            appointmentId: appointmentId.toString(),
            serviceType: appointmentDetails.type,
            previousMessages: []
          }
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to send message');
      }
      
      const data = await response.json();
      console.log("Message analysis:", data); // For debugging
      
      // Save message to database
      await saveMessageToDatabase(message, data.analysis, appointmentId);
      
      setSuccess('Message sent successfully!');
      setMessage('');
      
    } catch (error) {
      console.error('Error:', error);
      setError('Failed to send message. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const saveMessageToDatabase = async (message, analysis, appointmentId) => {
    try {
      await fetch('http://localhost:8000/api/shared/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          message,
          appointmentId,
          analysis,
          senderRole: 'customer'
        })
      });
    } catch (error) {
      console.error('Failed to save message:', error);
    }
  };

  return (
    <div className="message-handler">
      <div className="message-header">
        <h3>Send Message</h3>
        {onClose && <button className="close-button" onClick={onClose}>×</button>}
      </div>

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      <form onSubmit={handleSubmit} className="message-form">
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type your message here..."
          className="message-input"
          rows={4}
          required
        />
        
        <button type="submit" className="send-button" disabled={loading}>
          {loading ? 'Sending...' : 'Send Message'}
          <MessageCircle size={18} />
        </button>
      </form>
    </div>
  );
};

export default MessageHandler;