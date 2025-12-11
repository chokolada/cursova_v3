import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import bookingService from '../services/bookingService';
import '../styles/UserDashboard.css';

const UserDashboard = () => {
  const { user } = useAuth();
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [extendingBookingId, setExtendingBookingId] = useState(null);
  const [extendDays, setExtendDays] = useState(1);

  useEffect(() => {
    loadBookings();
  }, []);

  const loadBookings = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await bookingService.getMyBookings();
      setBookings(data);
    } catch (err) {
      setError('Failed to load bookings');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCancelBooking = async (bookingId) => {
    if (!window.confirm('Are you sure you want to cancel this booking?')) {
      return;
    }

    try {
      await bookingService.cancelBooking(bookingId);
      alert('Booking cancelled successfully');
      loadBookings();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to cancel booking');
    }
  };

  const handleExtendBooking = async (bookingId) => {
    try {
      await bookingService.extendBooking(bookingId, extendDays);
      alert(`Booking extended by ${extendDays} day(s) successfully`);
      setExtendingBookingId(null);
      setExtendDays(1);
      loadBookings();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to extend booking');
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: '#FFA500',
      confirmed: '#50C878',
      completed: '#4A90E2',
      cancelled: '#FF6B6B'
    };
    return colors[status] || '#666';
  };

  const canCancelOrExtend = (booking) => {
    return booking.status === 'pending' || booking.status === 'confirmed';
  };

  const calculateBonusPoints = (totalPrice) => {
    // Award 1 bonus point per $10 spent
    return Math.floor(totalPrice / 10);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="user-dashboard">
      <div className="dashboard-header">
        <h1>My Personal Dashboard</h1>
        <div className="user-info">
          <div className="user-welcome">
            <h2>Welcome back, {user?.username || 'Guest'}!</h2>
            <p>{user?.email}</p>
          </div>
          <div className="bonus-points-card">
            <div className="bonus-icon">⭐</div>
            <div className="bonus-info">
              <h3>Bonus Points</h3>
              <div className="points-value">{user?.bonus_points || 0}</div>
              <p className="points-info">Earn 1 point per $10 spent</p>
            </div>
          </div>
        </div>
      </div>

      <div className="dashboard-content">
        <h2>My Booking History</h2>

        {error && <div className="error-message">{error}</div>}

        {loading ? (
          <div className="loading">Loading your bookings...</div>
        ) : bookings.length === 0 ? (
          <div className="no-bookings">
            <p>You haven't made any bookings yet.</p>
            <a href="/booking" className="btn-primary">Book a Room</a>
          </div>
        ) : (
          <div className="bookings-grid">
            {bookings.map((booking) => (
              <div key={booking.id} className="booking-card">
                <div className="booking-header">
                  <h3>Room #{booking.room_id}</h3>
                  <span
                    className="status-badge"
                    style={{ backgroundColor: getStatusColor(booking.status) }}
                  >
                    {booking.status}
                  </span>
                </div>

                <div className="booking-details">
                  <div className="detail-row">
                    <span className="label">Check-in:</span>
                    <span className="value">{formatDate(booking.check_in_date)}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Check-out:</span>
                    <span className="value">{formatDate(booking.check_out_date)}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Guests:</span>
                    <span className="value">{booking.guests_count}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Total Price:</span>
                    <span className="value price">${booking.total_price}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Points Earned:</span>
                    <span className="value points">
                      ⭐ {calculateBonusPoints(booking.total_price)}
                    </span>
                  </div>
                  {booking.special_requests && (
                    <div className="detail-row">
                      <span className="label">Special Requests:</span>
                      <span className="value">{booking.special_requests}</span>
                    </div>
                  )}
                </div>

                {canCancelOrExtend(booking) && (
                  <div className="booking-actions">
                    {extendingBookingId === booking.id ? (
                      <div className="extend-form">
                        <input
                          type="number"
                          min="1"
                          max="30"
                          value={extendDays}
                          onChange={(e) => setExtendDays(parseInt(e.target.value))}
                          className="extend-input"
                        />
                        <button
                          onClick={() => handleExtendBooking(booking.id)}
                          className="btn-confirm"
                        >
                          Confirm
                        </button>
                        <button
                          onClick={() => setExtendingBookingId(null)}
                          className="btn-cancel-action"
                        >
                          Cancel
                        </button>
                      </div>
                    ) : (
                      <>
                        <button
                          onClick={() => setExtendingBookingId(booking.id)}
                          className="btn-extend"
                        >
                          Extend Booking
                        </button>
                        <button
                          onClick={() => handleCancelBooking(booking.id)}
                          className="btn-cancel"
                        >
                          Cancel Booking
                        </button>
                      </>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default UserDashboard;
