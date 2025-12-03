import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import '../styles/RoomCard.css';

const RoomCard = ({ room }) => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const handleBookNow = () => {
    if (!isAuthenticated()) {
      // Save the intended booking location and redirect to register
      localStorage.setItem('redirectAfterLogin', `/booking/${room.id}`);
      navigate('/register');
    } else {
      navigate(`/booking/${room.id}`);
    }
  };

  return (
    <div className="room-card">
      <div className="room-card-image">
        {room.image_url ? (
          <img src={room.image_url} alt={room.room_type} />
        ) : (
          <div className="room-card-placeholder">No Image</div>
        )}
      </div>

      <div className="room-card-content">
        <h3 className="room-card-title">
          Room {room.room_number} - {room.room_type}
        </h3>

        <div className="room-card-details">
          <p>
            <strong>Price:</strong> ${room.price_per_night} / night
          </p>
          <p>
            <strong>Capacity:</strong> {room.capacity} guests
          </p>
          {room.floor && (
            <p>
              <strong>Floor:</strong> {room.floor}
            </p>
          )}
        </div>

        {room.description && (
          <p className="room-card-description">{room.description}</p>
        )}

        {room.amenities && (
          <div className="room-card-amenities">
            <strong>Amenities:</strong> {room.amenities}
          </div>
        )}

        <div className="room-card-footer">
          <span
            className={`room-status ${
              room.is_available ? 'available' : 'unavailable'
            }`}
          >
            {room.is_available ? 'Available' : 'Not Available'}
          </span>

          {room.is_available && (
            <button onClick={handleBookNow} className="btn btn-primary">
              Book Now
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default RoomCard;
