import React, { useState, useEffect } from 'react';
import RoomCard from '../components/RoomCard';
import roomService from '../services/roomService';
import '../styles/Home.css';

const Home = () => {
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState({
    available_only: false,
    room_type: '',
  });

  useEffect(() => {
    loadRooms();
  }, [filter]);

  const loadRooms = async () => {
    setLoading(true);
    setError('');

    try {
      const params = {};
      if (filter.available_only) params.available_only = true;
      if (filter.room_type) params.room_type = filter.room_type;

      const data = await roomService.getAllRooms(params);
      setRooms(data);
    } catch (err) {
      setError('Failed to load rooms');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="home-container">
      <div className="home-header">
        <h1>Available Rooms</h1>

        <div className="home-filters">
          <label>
            <input
              type="checkbox"
              checked={filter.available_only}
              onChange={(e) =>
                setFilter({ ...filter, available_only: e.target.checked })
              }
            />
            Available Only
          </label>

          <select
            value={filter.room_type}
            onChange={(e) => setFilter({ ...filter, room_type: e.target.value })}
          >
            <option value="">All Types</option>
            <option value="single">Single</option>
            <option value="double">Double</option>
            <option value="suite">Suite</option>
            <option value="deluxe">Deluxe</option>
          </select>
        </div>
      </div>

      {loading && <div className="loading">Loading rooms...</div>}

      {error && <div className="error-message">{error}</div>}

      {!loading && !error && rooms.length === 0 && (
        <div className="no-data">No rooms found</div>
      )}

      <div className="rooms-grid">
        {rooms.map((room) => (
          <RoomCard key={room.id} room={room} />
        ))}
      </div>
    </div>
  );
};

export default Home;
