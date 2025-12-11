class StatisticsResponseBuilder:
    """Builder pattern for composing statistics responses."""

    def __init__(self):
        self._data = {}

    def with_room_overview(self, total_rooms: int, available_rooms: int):
        self._data.update({
            'total_rooms': total_rooms,
            'available_rooms': available_rooms,
            'occupied_rooms': total_rooms - available_rooms,
        })
        return self

    def with_bookings_by_status(self, bookings_by_status):
        self._data['bookings_by_status'] = bookings_by_status
        return self

    def with_user_total(self, total_users: int):
        self._data['total_users'] = total_users
        return self

    def with_current_revenue(self, current_month_revenue: float):
        self._data['current_month_revenue'] = current_month_revenue
        return self

    def build(self):
        return self._data
