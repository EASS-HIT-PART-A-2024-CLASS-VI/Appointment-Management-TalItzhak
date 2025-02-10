// src/components/MessagesManager.js
import React, { useState, useEffect } from 'react';
import { Check, Mail } from 'lucide-react';
import '../styles/MessagesManager.css';

const MessagesManager = ({ onClose }) => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    fetchMessages();
    const interval = setInterval(fetchMessages, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchMessages = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/messages/my-messages', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) throw new Error('Failed to fetch messages');
      const data = await response.json();
      setMessages(data);

      // Fetch unread count
      const unreadResponse = await fetch('http://localhost:8000/api/messages/unread-count', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (unreadResponse.ok) {
        const unreadData = await unreadResponse.json();
        setUnreadCount(unreadData.unread_count);
      }
    } catch (error) {
      setError('Failed to load messages');
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (messageId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/messages/messages/${messageId}/read`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) throw new Error('Failed to mark message as read');

      setMessages(messages.map(msg => 
        msg.id === messageId ? { ...msg, read: true } : msg
      ));
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      setError('Failed to mark message as read');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="messages-manager">
      <div className="messages-header">
        <h2>
          Messages 
          {unreadCount > 0 && <span className="unread-badge">{unreadCount}</span>}
        </h2>
        <button className="close-button" onClick={onClose}>×</button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {loading ? (
        <div className="loading">Loading messages...</div>
      ) : messages.length === 0 ? (
        <div className="no-messages">
          <Mail size={48} />
          <p>No messages yet</p>
        </div>
      ) : (
        <div className="messages-list">
          {messages.map(message => (
            <div key={message.id} className={`message-card ${!message.read ? 'unread' : ''}`}>
              <div className="message-header">
                <div className="message-info">
                  <h3>{message.title}</h3>
                  <p className="sender">From: {message.sender_name}</p>
                  <p className="timestamp">{formatDate(message.created_at)}</p>
                </div>
                {!message.read && (
                  <button 
                    className="mark-read-button"
                    onClick={() => markAsRead(message.id)}
                  >
                    <Check size={16} />
                    Mark as Read
                  </button>
                )}
              </div>
              <div className="message-content">
                <p>{message.content}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MessagesManager;