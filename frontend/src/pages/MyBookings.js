import React, { useState, useEffect } from 'react';
import bookingService from '../services/bookingService';
import '../styles/MyBookings.css';

const MyBookings = () => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

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

  const handleCancelBooking = async (id) => {
    if (!window.confirm('Are you sure you want to cancel this booking?')) {
      return;
    }

    try {
      await bookingService.cancelBooking(id);
      alert('Booking cancelled successfully');
      loadBookings();
    } catch (err) {
      alert('Failed to cancel booking');
      console.error(err);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getStatusClass = (status) => {
    const statusMap = {
      pending: 'status-pending',
      confirmed: 'status-confirmed',
      cancelled: 'status-cancelled',
      completed: 'status-completed',
    };
    return statusMap[status] || '';
  };

  if (loading) {
    return <div className="loading">Loading bookings...</div>;
  }

  return (
    <div className="my-bookings-container">
      <h1>My Bookings</h1>

      {error && <div className="error-message">{error}</div>}

      {bookings.length === 0 && !error && (
        <div className="no-data">You don't have any bookings yet.</div>
      )}

      <div className="bookings-list">
        {bookings.map((booking) => (
          <div key={booking.id} className="booking-card">
            <div className="booking-header">
              <h3>Booking #{booking.id}</h3>
              <span className={`booking-status ${getStatusClass(booking.status)}`}>
                {booking.status.toUpperCase()}
              </span>
            </div>

            <div className="booking-details">
              <p>
                <strong>Check-in:</strong> {formatDate(booking.check_in_date)}
              </p>
              <p>
                <strong>Check-out:</strong> {formatDate(booking.check_out_date)}
              </p>
              <p>
                <strong>Guests:</strong> {booking.guests_count}
              </p>
              <p>
                <strong>Total Price:</strong> ${booking.total_price}
              </p>
              {booking.special_requests && (
                <p>
                  <strong>Special Requests:</strong> {booking.special_requests}
                </p>
              )}
            </div>

            {booking.status === 'pending' && (
              <div className="booking-actions">
                <button
                  onClick={() => handleCancelBooking(booking.id)}
                  className="btn btn-danger"
                >
                  Cancel Booking
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default MyBookings;
