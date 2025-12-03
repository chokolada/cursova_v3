import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import roomService from '../services/roomService';
import bookingService from '../services/bookingService';
import '../styles/BookingForm.css';

const BookingForm = () => {
  const { roomId } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const [room, setRoom] = useState(null);
  const [formData, setFormData] = useState({
    check_in_date: '',
    check_out_date: '',
    guests_count: 1,
    special_requests: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login');
      return;
    }

    loadRoom();
  }, [roomId, isAuthenticated, navigate]);

  const loadRoom = async () => {
    try {
      const data = await roomService.getRoom(roomId);
      setRoom(data);
    } catch (err) {
      setError('Failed to load room details');
      console.error(err);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const bookingData = {
        room_id: parseInt(roomId),
        check_in_date: new Date(formData.check_in_date).toISOString(),
        check_out_date: new Date(formData.check_out_date).toISOString(),
        guests_count: parseInt(formData.guests_count),
        special_requests: formData.special_requests,
      };

      await bookingService.createBooking(bookingData);
      alert('Booking created successfully!');
      navigate('/my-bookings');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create booking');
    } finally {
      setLoading(false);
    }
  };

  if (!room) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="booking-form-container">
      <div className="booking-form-card">
        <h2>Book Room {room.room_number}</h2>

        <div className="room-summary">
          <h3>{room.room_type}</h3>
          <p>Price: ${room.price_per_night} / night</p>
          <p>Capacity: {room.capacity} guests</p>
        </div>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="check_in_date">Check-in Date</label>
            <input
              type="date"
              id="check_in_date"
              name="check_in_date"
              value={formData.check_in_date}
              onChange={handleChange}
              min={new Date().toISOString().split('T')[0]}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="check_out_date">Check-out Date</label>
            <input
              type="date"
              id="check_out_date"
              name="check_out_date"
              value={formData.check_out_date}
              onChange={handleChange}
              min={formData.check_in_date || new Date().toISOString().split('T')[0]}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="guests_count">Number of Guests</label>
            <input
              type="number"
              id="guests_count"
              name="guests_count"
              value={formData.guests_count}
              onChange={handleChange}
              min="1"
              max={room.capacity}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="special_requests">Special Requests (Optional)</label>
            <textarea
              id="special_requests"
              name="special_requests"
              value={formData.special_requests}
              onChange={handleChange}
              rows="4"
            />
          </div>

          <div className="form-actions">
            <button
              type="button"
              onClick={() => navigate('/')}
              className="btn btn-secondary"
            >
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Booking...' : 'Confirm Booking'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default BookingForm;
