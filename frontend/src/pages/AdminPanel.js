import React, { useState, useEffect } from 'react';
import roomService from '../services/roomService';
import bookingService from '../services/bookingService';
import offerService from '../services/offerService';
import '../styles/AdminPanel.css';

const AdminPanel = () => {
  const [activeTab, setActiveTab] = useState('rooms');
  const [rooms, setRooms] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [offers, setOffers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [roomForm, setRoomForm] = useState({
    room_number: '',
    room_type: 'single',
    price_per_night: '',
    capacity: '',
    description: '',
    amenities: '',
    floor: '',
    is_available: true,
  });

  const [editingRoom, setEditingRoom] = useState(null);

  const [offerForm, setOfferForm] = useState({
    name: '',
    description: '',
    price: '',
    offer_type: 'global',
    is_active: true,
  });

  const [editingOffer, setEditingOffer] = useState(null);

  useEffect(() => {
    if (activeTab === 'rooms') {
      loadRooms();
    } else if (activeTab === 'bookings') {
      loadBookings();
    } else if (activeTab === 'offers') {
      loadOffers();
    }
  }, [activeTab]);

  const loadRooms = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await roomService.getAllRooms();
      setRooms(data);
    } catch (err) {
      setError('Failed to load rooms');
    } finally {
      setLoading(false);
    }
  };

  const loadBookings = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await bookingService.getAllBookings();
      setBookings(data);
    } catch (err) {
      setError('Failed to load bookings');
    } finally {
      setLoading(false);
    }
  };

  const loadOffers = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await offerService.getAllOffers();
      setOffers(data);
    } catch (err) {
      setError('Failed to load offers');
    } finally {
      setLoading(false);
    }
  };

  const handleRoomFormChange = (e) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
    setRoomForm({
      ...roomForm,
      [e.target.name]: value,
    });
  };

  const handleCreateRoom = async (e) => {
    e.preventDefault();
    try {
      const roomData = {
        ...roomForm,
        price_per_night: parseFloat(roomForm.price_per_night),
        capacity: parseInt(roomForm.capacity),
        floor: roomForm.floor ? parseInt(roomForm.floor) : null,
      };

      await roomService.createRoom(roomData);
      alert('Room created successfully');
      resetRoomForm();
      loadRooms();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create room');
    }
  };

  const handleUpdateRoom = async (e) => {
    e.preventDefault();
    try {
      const roomData = {
        ...roomForm,
        price_per_night: parseFloat(roomForm.price_per_night),
        capacity: parseInt(roomForm.capacity),
        floor: roomForm.floor ? parseInt(roomForm.floor) : null,
      };

      await roomService.updateRoom(editingRoom, roomData);
      alert('Room updated successfully');
      resetRoomForm();
      loadRooms();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to update room');
    }
  };

  const handleEditRoom = (room) => {
    setEditingRoom(room.id);
    setRoomForm({
      room_number: room.room_number,
      room_type: room.room_type,
      price_per_night: room.price_per_night,
      capacity: room.capacity,
      description: room.description || '',
      amenities: room.amenities || '',
      floor: room.floor || '',
      is_available: room.is_available,
    });
  };

  const handleDeleteRoom = async (id) => {
    if (!window.confirm('Are you sure you want to delete this room?')) {
      return;
    }

    try {
      await roomService.deleteRoom(id);
      alert('Room deleted successfully');
      loadRooms();
    } catch (err) {
      alert('Failed to delete room');
    }
  };

  const resetRoomForm = () => {
    setRoomForm({
      room_number: '',
      room_type: 'single',
      price_per_night: '',
      capacity: '',
      description: '',
      amenities: '',
      floor: '',
      is_available: true,
    });
    setEditingRoom(null);
  };

  const handleOfferFormChange = (e) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
    setOfferForm({
      ...offerForm,
      [e.target.name]: value,
    });
  };

  const handleCreateOffer = async (e) => {
    e.preventDefault();
    try {
      const offerData = {
        ...offerForm,
        price: parseFloat(offerForm.price),
      };

      await offerService.createOffer(offerData);
      alert('Offer created successfully');
      resetOfferForm();
      loadOffers();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create offer');
    }
  };

  const handleUpdateOffer = async (e) => {
    e.preventDefault();
    try {
      const offerData = {
        ...offerForm,
        price: parseFloat(offerForm.price),
      };

      await offerService.updateOffer(editingOffer, offerData);
      alert('Offer updated successfully');
      resetOfferForm();
      loadOffers();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to update offer');
    }
  };

  const handleEditOffer = (offer) => {
    setEditingOffer(offer.id);
    setOfferForm({
      name: offer.name,
      description: offer.description,
      price: offer.price,
      offer_type: offer.offer_type,
      is_active: offer.is_active,
    });
  };

  const handleDeleteOffer = async (id) => {
    if (!window.confirm('Are you sure you want to delete this offer?')) {
      return;
    }

    try {
      await offerService.deleteOffer(id);
      alert('Offer deleted successfully');
      loadOffers();
    } catch (err) {
      alert('Failed to delete offer');
    }
  };

  const resetOfferForm = () => {
    setOfferForm({
      name: '',
      description: '',
      price: '',
      offer_type: 'global',
      is_active: true,
    });
    setEditingOffer(null);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="admin-panel-container">
      <h1>Admin Panel</h1>

      <div className="admin-tabs">
        <button
          className={activeTab === 'rooms' ? 'active' : ''}
          onClick={() => setActiveTab('rooms')}
        >
          Manage Rooms
        </button>
        <button
          className={activeTab === 'offers' ? 'active' : ''}
          onClick={() => setActiveTab('offers')}
        >
          Manage Offers
        </button>
        <button
          className={activeTab === 'bookings' ? 'active' : ''}
          onClick={() => setActiveTab('bookings')}
        >
          View Bookings
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {activeTab === 'rooms' && (
        <div className="admin-section">
          <div className="room-form-section">
            <h2>{editingRoom ? 'Edit Room' : 'Create New Room'}</h2>
            <form onSubmit={editingRoom ? handleUpdateRoom : handleCreateRoom}>
              <div className="form-row">
                <div className="form-group">
                  <label>Room Number</label>
                  <input
                    type="text"
                    name="room_number"
                    value={roomForm.room_number}
                    onChange={handleRoomFormChange}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Room Type</label>
                  <select
                    name="room_type"
                    value={roomForm.room_type}
                    onChange={handleRoomFormChange}
                    required
                  >
                    <option value="single">Single</option>
                    <option value="double">Double</option>
                    <option value="suite">Suite</option>
                    <option value="deluxe">Deluxe</option>
                  </select>
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Price per Night</label>
                  <input
                    type="number"
                    name="price_per_night"
                    value={roomForm.price_per_night}
                    onChange={handleRoomFormChange}
                    step="0.01"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Capacity</label>
                  <input
                    type="number"
                    name="capacity"
                    value={roomForm.capacity}
                    onChange={handleRoomFormChange}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Floor</label>
                  <input
                    type="number"
                    name="floor"
                    value={roomForm.floor}
                    onChange={handleRoomFormChange}
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Description</label>
                <textarea
                  name="description"
                  value={roomForm.description}
                  onChange={handleRoomFormChange}
                  rows="3"
                />
              </div>

              <div className="form-group">
                <label>Amenities</label>
                <input
                  type="text"
                  name="amenities"
                  value={roomForm.amenities}
                  onChange={handleRoomFormChange}
                  placeholder="WiFi, TV, Air conditioning..."
                />
              </div>

              <div className="form-group">
                <label>
                  <input
                    type="checkbox"
                    name="is_available"
                    checked={roomForm.is_available}
                    onChange={handleRoomFormChange}
                  />
                  Available
                </label>
              </div>

              <div className="form-actions">
                {editingRoom && (
                  <button type="button" onClick={resetRoomForm} className="btn btn-secondary">
                    Cancel
                  </button>
                )}
                <button type="submit" className="btn btn-primary">
                  {editingRoom ? 'Update Room' : 'Create Room'}
                </button>
              </div>
            </form>
          </div>

          <div className="rooms-list-section">
            <h2>Existing Rooms</h2>
            {loading ? (
              <div>Loading...</div>
            ) : (
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>Room #</th>
                    <th>Type</th>
                    <th>Price</th>
                    <th>Capacity</th>
                    <th>Floor</th>
                    <th>Available</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {rooms.map((room) => (
                    <tr key={room.id}>
                      <td>{room.room_number}</td>
                      <td>{room.room_type}</td>
                      <td>${room.price_per_night}</td>
                      <td>{room.capacity}</td>
                      <td>{room.floor || 'N/A'}</td>
                      <td>{room.is_available ? 'Yes' : 'No'}</td>
                      <td>
                        <button
                          onClick={() => handleEditRoom(room)}
                          className="btn btn-small btn-primary"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDeleteRoom(room.id)}
                          className="btn btn-small btn-danger"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}

      {activeTab === 'offers' && (
        <div className="admin-section">
          <div className="offer-form-section">
            <h2>{editingOffer ? 'Edit Offer' : 'Create New Offer'}</h2>
            <form onSubmit={editingOffer ? handleUpdateOffer : handleCreateOffer}>
              <div className="form-row">
                <div className="form-group">
                  <label>Offer Name</label>
                  <input
                    type="text"
                    name="name"
                    value={offerForm.name}
                    onChange={handleOfferFormChange}
                    placeholder="e.g., Breakfast, Spa Massage"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Price ($)</label>
                  <input
                    type="number"
                    name="price"
                    value={offerForm.price}
                    onChange={handleOfferFormChange}
                    step="0.01"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Type</label>
                  <select
                    name="offer_type"
                    value={offerForm.offer_type}
                    onChange={handleOfferFormChange}
                    required
                  >
                    <option value="global">Global (All Rooms)</option>
                    <option value="room_specific">Room Specific (Premium)</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label>Description</label>
                <textarea
                  name="description"
                  value={offerForm.description}
                  onChange={handleOfferFormChange}
                  rows="3"
                  placeholder="Describe the offer..."
                  required
                />
              </div>

              <div className="form-group">
                <label>
                  <input
                    type="checkbox"
                    name="is_active"
                    checked={offerForm.is_active}
                    onChange={handleOfferFormChange}
                  />
                  Active
                </label>
              </div>

              <div className="form-actions">
                {editingOffer && (
                  <button type="button" onClick={resetOfferForm} className="btn btn-secondary">
                    Cancel
                  </button>
                )}
                <button type="submit" className="btn btn-primary">
                  {editingOffer ? 'Update Offer' : 'Create Offer'}
                </button>
              </div>
            </form>
          </div>

          <div className="offers-list-section">
            <h2>Existing Offers</h2>
            {loading ? (
              <div>Loading...</div>
            ) : (
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Description</th>
                    <th>Price</th>
                    <th>Type</th>
                    <th>Active</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {offers.map((offer) => (
                    <tr key={offer.id}>
                      <td>{offer.id}</td>
                      <td>{offer.name}</td>
                      <td>{offer.description}</td>
                      <td>${offer.price}</td>
                      <td>
                        <span className={`type-badge type-${offer.offer_type}`}>
                          {offer.offer_type === 'global' ? 'Global' : 'Premium'}
                        </span>
                      </td>
                      <td>{offer.is_active ? 'Yes' : 'No'}</td>
                      <td>
                        <button
                          onClick={() => handleEditOffer(offer)}
                          className="btn btn-small btn-primary"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDeleteOffer(offer.id)}
                          className="btn btn-small btn-danger"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}

      {activeTab === 'bookings' && (
        <div className="admin-section">
          <h2>All Bookings</h2>
          {loading ? (
            <div>Loading...</div>
          ) : (
            <table className="admin-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>User ID</th>
                  <th>Room ID</th>
                  <th>Check-in</th>
                  <th>Check-out</th>
                  <th>Guests</th>
                  <th>Total Price</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {bookings.map((booking) => (
                  <tr key={booking.id}>
                    <td>{booking.id}</td>
                    <td>{booking.user_id}</td>
                    <td>{booking.room_id}</td>
                    <td>{formatDate(booking.check_in_date)}</td>
                    <td>{formatDate(booking.check_out_date)}</td>
                    <td>{booking.guests_count}</td>
                    <td>${booking.total_price}</td>
                    <td>
                      <span className={`status-badge status-${booking.status}`}>
                        {booking.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
};

export default AdminPanel;
