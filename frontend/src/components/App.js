import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '../context/ThemeContext';
import Layout from './Layout';
import Login from './Login';
import Register from './Register';
import BusinessDashboard from './BusinessDashboard';
import CustomerDashboard from './CustomerDashboard';
import ProtectedRoute from './ProtectedRoute';
import '../styles/shared.css';

const App = () => {
  return (
    <ThemeProvider>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/register" />} />
            <Route path="/register" element={<Register />} />
            <Route path="/login" element={<Login />} />
            <Route 
              path="/business-dashboard" 
              element={
                <ProtectedRoute>
                  <BusinessDashboard />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/customer-dashboard" 
              element={
                <ProtectedRoute>
                  <CustomerDashboard />
                </ProtectedRoute>
              } 
            />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
};

export default App;