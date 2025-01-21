// frontend/src/components/MessagesViewer.js
import React, { useState, useEffect } from 'react';
import { useTheme } from '../context/ThemeContext';
import '../styles/MessagesViewer.css';

const MessagesViewer = ({ onClose }) => {
  const { isDark } = useTheme();
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedAppointment, setSelectedAppointment] = useState(null);

  useEffect(() => {
    fetchMessages();
  }, []);

  const fetchMessages = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/business/messages', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) throw new Error('Failed to fetch messages');
      
      const data = await response.json();
      // Group messages by appointment
      const groupedMessages = groupMessagesByAppointment(data);
      setMessages(groupedMessages);
    } catch (error) {
      setError('Failed to load messages');
    } finally {
      setLoading(false);
    }
  };

  const groupMessagesByAppointment = (messages) => {
    return messages.reduce((groups, message) => {
      const appointmentId = message.appointmentId;
      if (!groups[appointmentId]) {
        groups[appointmentId] = {
          appointmentDetails: message.appointmentDetails,
          messages: []
        };
      }
      groups[appointmentId].messages.push(message);
      return groups;
    }, {});
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className={`messages-viewer ${!isDark ? 'light-mode' : ''}`}>
      <div className="viewer-header">
        <h2>Customer Messages</h2>
        <button className="close-button" onClick={onClose}>×</button>
      </div>

      {error && <div className="error-message">{error}</div>}
      
      {loading ? (
        <div className="loading">Loading messages...</div>
      ) : Object.keys(messages).length === 0 ? (
        <div className="no-messages">No messages found</div>
      ) : (
        <div className="messages-list">
          {Object.entries(messages).map(([appointmentId, data]) => (
            <div key={appointmentId} className="appointment-messages">
              <div className="appointment-header" 
                   onClick={() => setSelectedAppointment(
                     selectedAppointment === appointmentId ? null : appointmentId
                   )}>
                <div className="appointment-info">
                  <h3>{data.appointmentDetails.title}</h3>
                  <p>
                    {formatDate(data.appointmentDetails.date)}
                    {' '}| Customer: {data.appointmentDetails.customer_name}
                  </p>
                </div>
                <span className="message-count">
                  {data.messages.length} messages
                </span>
              </div>

              {selectedAppointment === appointmentId && (
                <div className="messages-container">
                  {data.messages.map((message, index) => (
                    <div key={index} className="message-item">
                      <div className="message-content">
                        {message.message}
                      </div>
                      <div className="message-meta">
                        <span className="message-time">
                          {formatDate(message.timestamp)}
                        </span>
                        <div className="message-analysis">
                          <span className="intent">Intent: {message.analysis.intent}</span>
                          <span className="sentiment">Sentiment: {message.analysis.sentiment}</span>
                          <span className="urgency">Urgency: {message.analysis.urgency}/5</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MessagesViewer;