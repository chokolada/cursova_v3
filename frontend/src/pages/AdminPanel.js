import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import roomService from '../services/roomService';
import bookingService from '../services/bookingService';
import offerService from '../services/offerService';
import statisticsService from '../services/statisticsService';
import { useAuth } from '../contexts/AuthContext';
import '../styles/AdminPanel.css';

const AdminPanel = () => {
  const { isManager } = useAuth();
  const [activeTab, setActiveTab] = useState(isManager() ? 'rooms' : 'graphs');
  const [rooms, setRooms] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [offers, setOffers] = useState([]);
  const [statistics, setStatistics] = useState({
    dashboard: null,
    roomOccupancy: [],
    financial: null,
    regularCustomers: [],
    roomCategoryPopularity: []
  });
  const [graphData, setGraphData] = useState({
    revenue: [],
    occupancy: [],
    bookingsStatus: []
  });
  const [graphPeriod, setGraphPeriod] = useState('month');
  const [graphDays, setGraphDays] = useState(180);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [roomOccupancyData, setRoomOccupancyData] = useState([]);

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
    } else if (activeTab === 'statistics') {
      loadStatistics();
    } else if (activeTab === 'graphs') {
      loadGraphs();
    } else if (activeTab === 'occupancy') {
      loadRoomOccupancy();
    }
  }, [activeTab]);

  useEffect(() => {
    if (activeTab === 'graphs') {
      loadGraphs();
    }
  }, [graphPeriod, graphDays]);

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

  const loadStatistics = async () => {
    setLoading(true);
    setError('');
    try {
      const [dashboard, roomOccupancy, financial, regularCustomers, roomCategoryPopularity] = await Promise.all([
        statisticsService.getDashboardSummary(),
        statisticsService.getRoomOccupancy(),
        statisticsService.getFinancialMetrics(),
        statisticsService.getRegularCustomers(),
        statisticsService.getRoomCategoryPopularity()
      ]);
      setStatistics({
        dashboard,
        roomOccupancy,
        financial,
        regularCustomers,
        roomCategoryPopularity
      });
    } catch (err) {
      setError('Failed to load statistics');
    } finally {
      setLoading(false);
    }
  };

  const loadGraphs = async () => {
    setLoading(true);
    setError('');
    try {
      const [revenue, occupancy, bookingsStatus] = await Promise.all([
        statisticsService.getRevenueGraph(graphPeriod, graphDays),
        statisticsService.getOccupancyGraph(graphPeriod, graphDays),
        statisticsService.getBookingsStatusGraph(graphPeriod, graphDays)
      ]);
      setGraphData({
        revenue,
        occupancy,
        bookingsStatus
      });
    } catch (err) {
      setError('Failed to load graph data');
    } finally {
      setLoading(false);
    }
  };

  const loadRoomOccupancy = async () => {
    setLoading(true);
    setError('');
    try {
      const [roomsData, bookingsData] = await Promise.all([
        roomService.getAllRooms(),
        bookingService.getAllBookings()
      ]);

      const today = new Date();
      today.setHours(0, 0, 0, 0);

      // Process room occupancy data
      const occupancyData = roomsData.map(room => {
        // Filter bookings for this room that are confirmed or pending (not cancelled)
        const roomBookings = bookingsData.filter(
          booking => booking.room_id === room.id &&
          booking.status !== 'cancelled'
        );

        // Find current booking (today is between check-in and check-out)
        const currentBooking = roomBookings.find(booking => {
          const checkIn = new Date(booking.check_in_date);
          const checkOut = new Date(booking.check_out_date);
          checkIn.setHours(0, 0, 0, 0);
          checkOut.setHours(0, 0, 0, 0);
          return checkIn <= today && checkOut > today;
        });

        // Find upcoming bookings (check-in date is in the future)
        const upcomingBookings = roomBookings
          .filter(booking => {
            const checkIn = new Date(booking.check_in_date);
            checkIn.setHours(0, 0, 0, 0);
            return checkIn > today;
          })
          .sort((a, b) => new Date(a.check_in_date) - new Date(b.check_in_date))
          .slice(0, 5); // Show next 5 bookings

        return {
          room,
          isOccupied: !!currentBooking,
          currentBooking,
          upcomingBookings
        };
      });

      setRoomOccupancyData(occupancyData);
    } catch (err) {
      setError('Failed to load room occupancy data');
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
    // Format as YYYY-MM-DD
    const date = new Date(dateString);
    return date.toISOString().split('T')[0];
  };

  const handleConfirmBooking = async (bookingId) => {
    if (!window.confirm('Confirm this booking?')) {
      return;
    }

    try {
      await bookingService.confirmBooking(bookingId);
      alert('Booking confirmed successfully');
      // Reload data based on active tab
      if (activeTab === 'bookings') {
        loadBookings();
      } else if (activeTab === 'occupancy') {
        loadRoomOccupancy();
      }
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to confirm booking');
    }
  };

  const handleDeclineBooking = async (bookingId) => {
    if (!window.confirm('Decline this booking? This will cancel it.')) {
      return;
    }

    try {
      await bookingService.declineBooking(bookingId);
      alert('Booking declined successfully');
      // Reload data based on active tab
      if (activeTab === 'bookings') {
        loadBookings();
      } else if (activeTab === 'occupancy') {
        loadRoomOccupancy();
      }
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to decline booking');
    }
  };

  return (
    <div className="admin-panel-container">
      <h1>Admin Panel</h1>

      <div className="admin-tabs">
        {isManager() && (
          <>
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
              className={activeTab === 'occupancy' ? 'active' : ''}
              onClick={() => setActiveTab('occupancy')}
            >
              Room Occupancy
            </button>
            <button
              className={activeTab === 'statistics' ? 'active' : ''}
              onClick={() => setActiveTab('statistics')}
            >
              Statistics
            </button>
          </>
        )}
        <button
          className={activeTab === 'graphs' ? 'active' : ''}
          onClick={() => setActiveTab('graphs')}
        >
          Statistics (Graph)
        </button>
        {isManager() && (
          <button
            className={activeTab === 'bookings' ? 'active' : ''}
            onClick={() => setActiveTab('bookings')}
          >
            View Bookings
          </button>
        )}
      </div>

      {error && <div className="error-message">{error}</div>}

      {isManager() && activeTab === 'rooms' && (
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

      {isManager() && activeTab === 'offers' && (
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

      {isManager() && activeTab === 'statistics' && (
        <div className="admin-section">
          <h2>Statistics & Analytics</h2>
          {loading ? (
            <div>Loading...</div>
          ) : (
            <>
              {/* Dashboard Summary */}
              {statistics.dashboard && (
                <div className="stats-summary">
                  <h3>Dashboard Summary</h3>
                  <div className="stats-cards">
                    <div className="stat-card">
                      <div className="stat-value">{statistics.dashboard.total_rooms}</div>
                      <div className="stat-label">Total Rooms</div>
                    </div>
                    <div className="stat-card">
                      <div className="stat-value">{statistics.dashboard.available_rooms}</div>
                      <div className="stat-label">Available Rooms</div>
                    </div>
                    <div className="stat-card">
                      <div className="stat-value">{statistics.dashboard.occupied_rooms}</div>
                      <div className="stat-label">Occupied Rooms</div>
                    </div>
                    <div className="stat-card">
                      <div className="stat-value">{statistics.dashboard.total_users}</div>
                      <div className="stat-label">Total Users</div>
                    </div>
                    <div className="stat-card">
                      <div className="stat-value">${statistics.dashboard.current_month_revenue.toFixed(2)}</div>
                      <div className="stat-label">Current Month Revenue</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Room Occupancy */}
              <div className="stats-section">
                <h3>Room Occupancy</h3>
                <table className="admin-table">
                  <thead>
                    <tr>
                      <th>Room #</th>
                      <th>Type</th>
                      <th>Status</th>
                      <th>Total Bookings</th>
                      <th>Confirmed Bookings</th>
                    </tr>
                  </thead>
                  <tbody>
                    {statistics.roomOccupancy.map((room) => (
                      <tr key={room.room_id}>
                        <td>{room.room_number}</td>
                        <td>{room.room_type}</td>
                        <td>
                          <span className={room.is_available ? 'status-available' : 'status-occupied'}>
                            {room.is_available ? 'Available' : 'Occupied'}
                          </span>
                        </td>
                        <td>{room.total_bookings}</td>
                        <td>{room.confirmed_bookings}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Financial Metrics */}
              {statistics.financial && (
                <div className="stats-section">
                  <h3>Financial Metrics</h3>
                  <div className="financial-summary">
                    <div className="financial-stat">
                      <strong>Total Revenue:</strong> ${statistics.financial.total_revenue.toFixed(2)}
                    </div>
                    <div className="financial-stat">
                      <strong>Total Bookings:</strong> {statistics.financial.total_bookings}
                    </div>
                  </div>

                  <h4>Room Type Popularity</h4>
                  <table className="admin-table">
                    <thead>
                      <tr>
                        <th>Room Type</th>
                        <th>Bookings</th>
                        <th>Total Revenue</th>
                        <th>Avg Price</th>
                      </tr>
                    </thead>
                    <tbody>
                      {statistics.financial.room_type_popularity.map((type) => (
                        <tr key={type.room_type}>
                          <td>{type.room_type}</td>
                          <td>{type.booking_count}</td>
                          <td>${type.total_revenue.toFixed(2)}</td>
                          <td>${type.avg_price.toFixed(2)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>

                  <h4>Monthly Revenue (Last 12 Months)</h4>
                  <table className="admin-table">
                    <thead>
                      <tr>
                        <th>Month</th>
                        <th>Revenue</th>
                        <th>Bookings</th>
                      </tr>
                    </thead>
                    <tbody>
                      {statistics.financial.monthly_revenue.map((month, index) => (
                        <tr key={index}>
                          <td>{month.year}-{String(month.month).padStart(2, '0')}</td>
                          <td>${month.revenue.toFixed(2)}</td>
                          <td>{month.booking_count}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* Regular Customers */}
              <div className="stats-section">
                <h3>Regular Customers</h3>
                <table className="admin-table">
                  <thead>
                    <tr>
                      <th>Username</th>
                      <th>Email</th>
                      <th>Full Name</th>
                      <th>Bookings</th>
                      <th>Total Spent</th>
                      <th>Last Booking</th>
                    </tr>
                  </thead>
                  <tbody>
                    {statistics.regularCustomers.map((customer) => (
                      <tr key={customer.user_id}>
                        <td>{customer.username}</td>
                        <td>{customer.email}</td>
                        <td>{customer.full_name}</td>
                        <td>{customer.booking_count}</td>
                        <td>${customer.total_spent.toFixed(2)}</td>
                        <td>{customer.last_booking_date ? formatDate(customer.last_booking_date) : 'N/A'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Room Category Popularity */}
              <div className="stats-section">
                <h3>Room Category Popularity</h3>
                <table className="admin-table">
                  <thead>
                    <tr>
                      <th>Room Type</th>
                      <th>Total Bookings</th>
                      <th>Percentage</th>
                      <th>Total Revenue</th>
                      <th>Unique Customers</th>
                    </tr>
                  </thead>
                  <tbody>
                    {statistics.roomCategoryPopularity.map((category) => (
                      <tr key={category.room_type}>
                        <td><strong>{category.room_type}</strong></td>
                        <td>{category.booking_count}</td>
                        <td>{category.percentage}%</td>
                        <td>${category.total_revenue.toFixed(2)}</td>
                        <td>{category.unique_customers}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>
      )}

      {activeTab === 'graphs' && (
        <div className="admin-section">
          <h2>Statistics Graphs</h2>

          <div className="graph-controls">
            <div className="control-group">
              <label>Time Period:</label>
              <select
                value={graphPeriod}
                onChange={(e) => setGraphPeriod(e.target.value)}
                className="period-selector"
              >
                <option value="day">Daily</option>
                <option value="week">Weekly</option>
                <option value="month">Monthly</option>
              </select>
            </div>

            <div className="control-group">
              <label>Look Back (days):</label>
              <div className="days-row">
                <input
                  type="number"
                  value={graphDays}
                  onChange={(e) => setGraphDays(parseInt(e.target.value))}
                  min="1"
                  max="365"
                  className="days-input"
                />
                <div className="quick-pills">
                  {[7, 30, 60, 90, 180, 365].map((days) => (
                    <button
                      key={days}
                      type="button"
                      className={`pill ${graphDays === days ? 'active' : ''}`}
                      onClick={() => setGraphDays(days)}
                    >
                      {days === 7 ? '1w' : days === 30 ? '1m' : `${Math.round(days / 30)}m`}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {loading ? (
            <div>Loading graphs...</div>
          ) : (
            <>
              <div className="graph-section">
                <h3>Revenue Over Time</h3>
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart
                    data={graphData.revenue}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                    <XAxis
                      dataKey="period"
                      stroke="#666"
                      style={{ fontSize: '12px' }}
                    />
                    <YAxis
                      stroke="#666"
                      style={{ fontSize: '12px' }}
                    />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc' }}
                    />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="revenue"
                      stroke="#4A90E2"
                      name="Revenue ($)"
                      strokeWidth={3}
                      dot={{ fill: '#4A90E2', r: 5 }}
                      activeDot={{ r: 7 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              <div className="graph-section">
                <h3>Room Occupancy Over Time</h3>
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart
                    data={graphData.occupancy}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                    <XAxis
                      dataKey="period"
                      stroke="#666"
                      style={{ fontSize: '12px' }}
                    />
                    <YAxis
                      stroke="#666"
                      style={{ fontSize: '12px' }}
                    />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc' }}
                    />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="occupancy_rate"
                      stroke="#50C878"
                      name="Occupancy Rate (%)"
                      strokeWidth={3}
                      dot={{ fill: '#50C878', r: 5 }}
                      activeDot={{ r: 7 }}
                    />
                    <Line
                      type="monotone"
                      dataKey="occupied_rooms"
                      stroke="#FF6B6B"
                      name="Occupied Rooms"
                      strokeWidth={3}
                      dot={{ fill: '#FF6B6B', r: 5 }}
                      activeDot={{ r: 7 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              <div className="graph-section">
                <h3>Bookings by Status Over Time</h3>
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart
                    data={graphData.bookingsStatus}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                    <XAxis
                      dataKey="period"
                      stroke="#666"
                      style={{ fontSize: '12px' }}
                    />
                    <YAxis
                      stroke="#666"
                      style={{ fontSize: '12px' }}
                    />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc' }}
                    />
                    <Legend />
                    <Bar dataKey="confirmed" stackId="a" fill="#50C878" name="Confirmed" />
                    <Bar dataKey="completed" stackId="a" fill="#4A90E2" name="Completed" />
                    <Bar dataKey="pending" stackId="a" fill="#FFA500" name="Pending" />
                    <Bar dataKey="cancelled" stackId="a" fill="#FF6B6B" name="Cancelled" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </>
          )}
        </div>
      )}

      {isManager() && activeTab === 'bookings' && (
        <div className="admin-section">
          <h2>All Bookings</h2>
          {loading ? (
            <div>Loading...</div>
          ) : (
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>User</th>
                    <th>Room</th>
                    <th>Check-in</th>
                    <th>Check-out</th>
                    <th>Guests</th>
                    <th>Total Price</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
              </thead>
                <tbody>
                  {bookings.map((booking) => (
                    <tr key={booking.id}>
                      <td>{booking.id}</td>
                      <td>
                        {booking.user?.username || 'Unknown'} (ID: {booking.user_id})
                      </td>
                      <td>
                        {booking.room?.room_number || 'Unknown'} (ID: {booking.room_id})
                      </td>
                      <td>{formatDate(booking.check_in_date)}</td>
                      <td>{formatDate(booking.check_out_date)}</td>
                      <td>{booking.guests_count}</td>
                      <td>${booking.total_price}</td>
                      <td>
                        <span className={`status-badge status-${booking.status}`}>
                          {booking.status}
                        </span>
                      </td>
                      <td>
                        {booking.status === 'pending' && (
                          <div className="action-buttons">
                            <button
                              onClick={() => handleConfirmBooking(booking.id)}
                              className="btn-success"
                            >
                              Confirm
                            </button>
                            <button
                              onClick={() => handleDeclineBooking(booking.id)}
                              className="btn-danger"
                            >
                              Decline
                            </button>
                          </div>
                        )}
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {isManager() && activeTab === 'occupancy' && (
        <div className="admin-section">
          <h2>Room Occupancy</h2>
          {loading ? (
            <div>Loading...</div>
          ) : (
            <div className="occupancy-container">
              <div className="occupancy-summary">
                <div className="summary-card">
                  <h3>Currently Occupied</h3>
                  <div className="summary-number">
                    {roomOccupancyData.filter(r => r.isOccupied).length}
                  </div>
                </div>
                <div className="summary-card">
                  <h3>Available Now</h3>
                  <div className="summary-number">
                    {roomOccupancyData.filter(r => !r.isOccupied).length}
                  </div>
                </div>
                <div className="summary-card">
                  <h3>Total Rooms</h3>
                  <div className="summary-number">
                    {roomOccupancyData.length}
                  </div>
                </div>
              </div>

              <table className="admin-table occupancy-table">
                <thead>
                  <tr>
                    <th>Room</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Current Booking</th>
                    <th>Upcoming Bookings</th>
                  </tr>
                </thead>
                <tbody>
                  {roomOccupancyData.map(({ room, isOccupied, currentBooking, upcomingBookings }) => (
                    <tr key={room.id}>
                      <td>
                        <strong>{room.room_number}</strong>
                      </td>
                      <td>{room.room_type}</td>
                      <td>
                        <span className={`status-badge ${isOccupied ? 'status-occupied' : 'status-available'}`}>
                          {isOccupied ? 'Occupied' : 'Available'}
                        </span>
                      </td>
                      <td>
                        {currentBooking ? (
                          <div className="booking-info">
                            <div>
                              <strong>{currentBooking.user?.username || 'Unknown'}</strong>
                            </div>
                            <div className="booking-dates">
                              {formatDate(currentBooking.check_in_date)} → {formatDate(currentBooking.check_out_date)}
                            </div>
                            <span className={`status-badge status-${currentBooking.status}`}>
                              {currentBooking.status}
                            </span>
                            {currentBooking.status === 'pending' && (
                              <div className="action-buttons" style={{marginTop: '10px'}}>
                                <button
                                  onClick={() => handleConfirmBooking(currentBooking.id)}
                                  className="btn-success"
                                >
                                  Confirm
                                </button>
                                <button
                                  onClick={() => handleDeclineBooking(currentBooking.id)}
                                  className="btn-danger"
                                >
                                  Decline
                                </button>
                              </div>
                            )}
                          </div>
                        ) : (
                          <span className="no-booking">—</span>
                        )}
                      </td>
                      <td>
                        {upcomingBookings.length > 0 ? (
                          <div className="upcoming-bookings">
                            {upcomingBookings.map(booking => (
                              <div key={booking.id} className="upcoming-booking-item">
                                <span className="booking-dates">
                                  {formatDate(booking.check_in_date)} → {formatDate(booking.check_out_date)}
                                </span>
                                <span className="booking-user">
                                  {booking.user?.username || 'Unknown'}
                                </span>
                                <span className={`status-badge status-${booking.status}`}>
                                  {booking.status}
                                </span>
                                {booking.status === 'pending' && (
                                  <div className="action-buttons" style={{marginTop: '8px'}}>
                                    <button
                                      onClick={() => handleConfirmBooking(booking.id)}
                                      className="btn-success btn-small"
                                    >
                                      Confirm
                                    </button>
                                    <button
                                      onClick={() => handleDeclineBooking(booking.id)}
                                      className="btn-danger btn-small"
                                    >
                                      Decline
                                    </button>
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        ) : (
                          <span className="no-booking">No upcoming bookings</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AdminPanel;
