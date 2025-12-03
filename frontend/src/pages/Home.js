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
    min_price: '',
    max_price: '',
    capacity: '',
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
      if (filter.min_price) params.min_price = filter.min_price;
      if (filter.max_price) params.max_price = filter.max_price;
      if (filter.capacity) params.capacity = filter.capacity;

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

          <input
            type="number"
            placeholder="Min Price"
            value={filter.min_price}
            onChange={(e) => setFilter({ ...filter, min_price: e.target.value })}
            min="0"
            step="10"
          />

          <input
            type="number"
            placeholder="Max Price"
            value={filter.max_price}
            onChange={(e) => setFilter({ ...filter, max_price: e.target.value })}
            min="0"
            step="10"
          />

          <select
            value={filter.capacity}
            onChange={(e) => setFilter({ ...filter, capacity: e.target.value })}
          >
            <option value="">Any Capacity</option>
            <option value="1">1+ guests</option>
            <option value="2">2+ guests</option>
            <option value="3">3+ guests</option>
            <option value="4">4+ guests</option>
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
