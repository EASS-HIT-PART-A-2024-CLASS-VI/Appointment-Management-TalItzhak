import React, { useState, useEffect } from 'react';
import { Check, Trash2 } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import '../styles/MessagesManager.css';

const MessagesManager = ({ onClose }) => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [expandedMessage, setExpandedMessage] = useState(null);
  const { isDark } = useTheme();

  useEffect(() => {
    fetchMessages();
    const interval = setInterval(fetchMessages, 30000);
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
    } catch (error) {
      setError('Failed to load messages');
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (messageId, e) => {
    e.stopPropagation();
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
    } catch (error) {
      setError('Failed to mark message as read');
    }
  };

  const deleteMessage = async (messageId, e) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this message?')) return;
    
    try {
      const response = await fetch(`http://localhost:8000/api/messages/messages/${messageId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) throw new Error('Failed to delete message');

      setMessages(messages.filter(msg => msg.id !== messageId));
    } catch (error) {
      setError('Failed to delete message');
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const isToday = date.toDateString() === now.toDateString();
    
    const timeOptions = { hour: '2-digit', minute: '2-digit', hour12: true };
    const time = date.toLocaleTimeString('en-US', timeOptions);

    if (isToday) {
      return `Today at ${time}`;
    }
    
    return `${date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric' 
    })} at ${time}`;
  };

  const handleMessageClick = (messageId) => {
    setExpandedMessage(expandedMessage === messageId ? null : messageId);
  };

  const getUnreadCount = () => {
    return messages.filter(msg => !msg.read).length;
  };

  return (
    <div className={`messages-manager ${isDark ? 'dark' : ''}`}>
      <div className="messages-header">
        <h2>
          Messages 
          {getUnreadCount() > 0 && (
            <span className="unread-count">{getUnreadCount()}</span>
          )}
        </h2>
        <button className="close-button" onClick={onClose}>×</button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {loading ? (
        <div className="loading">Loading messages...</div>
      ) : messages.length === 0 ? (
        <div className="no-messages">No messages yet</div>
      ) : (
        <div className="messages-list">
          {messages.map(message => (
            <div 
              key={message.id} 
              className={`message-card ${!message.read ? 'unread' : ''}`}
              onClick={() => handleMessageClick(message.id)}
            >
              <div className="message-header">
                <div className="message-info">
                  <h3>{message.title}</h3>
                  <span className="sender">From: {message.sender_name}</span>
                  <span className="date">{formatDate(message.created_at)}</span>
                </div>
                <div className="message-actions">
                  {!message.read && (
                    <button 
                      className="mark-read-button"
                      onClick={(e) => markAsRead(message.id, e)}
                    >
                      <Check size={16} />
                      Mark as read
                    </button>
                  )}
                  <button 
                    className="delete-button"
                    onClick={(e) => deleteMessage(message.id, e)}
                    title="Delete message"
                  >
                    <Trash2 size={16} />
                    Delete
                  </button>
                </div>
              </div>
              {expandedMessage === message.id && (
                <div className="message-content">
                  <p>{message.content}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MessagesManager;