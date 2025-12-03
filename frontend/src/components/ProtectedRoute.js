import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const ProtectedRoute = ({ children, requireManager = false }) => {
  const { isAuthenticated, isManager, loading } = useAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated()) {
    return <Navigate to="/login" />;
  }

  if (requireManager && !isManager()) {
    return <Navigate to="/" />;
  }

  return children;
};

export default ProtectedRoute;
