import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import '../styles/Navbar.css';

const Navbar = () => {
  const { user, logout, isAuthenticated, isManager, loading } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          Hotel Management
        </Link>

        <ul className="navbar-menu">
          <li className="navbar-item">
            <Link to="/" className="navbar-link">
              Rooms
            </Link>
          </li>

          {isAuthenticated() && (
            <li className="navbar-item">
              <Link to="/my-bookings" className="navbar-link">
                My Bookings
              </Link>
            </li>
          )}

          {isManager() && (
            <li className="navbar-item">
              <Link to="/react-admin" className="navbar-link">
                Admin Panel
              </Link>
            </li>
          )}

          {loading ? null : isAuthenticated() ? (
            <>
              <li className="navbar-item">
                <span className="navbar-user">
                  Welcome, {user?.username} ({user?.role})
                </span>
              </li>
              <li className="navbar-item">
                <button onClick={handleLogout} className="navbar-button">
                  Logout
                </button>
              </li>
            </>
          ) : (
            <>
              <li className="navbar-item">
                <Link to="/login" className="navbar-link">
                  Login
                </Link>
              </li>
              <li className="navbar-item">
                <Link to="/register" className="navbar-link">
                  Register
                </Link>
              </li>
            </>
          )}
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;
