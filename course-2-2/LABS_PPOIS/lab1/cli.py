import cmd
from models.reception import Reception
from models.room import (Room, RoomType)
from models.staff import Staff, StaffRole
from models.service import Service, ServiceType
from models.exceptions import (
    RoomNotAvailableError, GuestNotFoundError,
    BookingNotFoundError, ServiceError
)


class HotelCLI(cmd.Cmd):
    intro = "Welcome to Hotel Management System. Type 'help' for commands list."
    prompt = "(hotel) "

    def __init__(self):
        super().__init__()
        self.reception = Reception()
        self.service = Service()
        self._setup_sample_data()

    def _setup_sample_data(self):
        # Add sample rooms
        self.reception.add_room(Room(101, RoomType.SINGLE, 100))
        self.reception.add_room(Room(102, RoomType.DOUBLE, 150))
        self.reception.add_room(Room(201, RoomType.SUITE, 250))
        self.reception.add_room(Room(202, RoomType.DELUXE, 350))

        # Add sample staff
        self.reception.add_staff(Staff(1, "John Doe", StaffRole.RECEPTIONIST, "john@hotel.com"))
        self.reception.add_staff(Staff(2, "Jane Smith", StaffRole.HOUSEKEEPING, "jane@hotel.com"))
        self.reception.add_staff(Staff(3, "Mike Johnson", StaffRole.MANAGER, "mike@hotel.com"))

    def do_add_room(self, arg):
        """Add a new room: add_room <number> <type> <price>
        Types: SINGLE, DOUBLE, SUITE, DELUXE"""
        try:
            args = arg.split()
            if len(args) != 3:
                print("Usage: add_room <number> <type> <price>")
                return

            number = int(args[0])
            room_type = RoomType[args[1].upper()]
            price = float(args[2])

            room = Room(number, room_type, price)
            self.reception.add_room(room)
            print(f"Room {number} added successfully.")
        except (ValueError, KeyError) as e:
            print(f"Error: {e}")

    def do_list_rooms(self, arg):
        """List all rooms: list_rooms [available]"""
        rooms = self.reception.rooms.values()
        if arg.lower() == "available":
            rooms = self.reception.get_available_rooms()

        for room in rooms:
            print(room)

    def do_register_guest(self, arg):
        """Register a new guest: register_guest <name> <email> <phone> <passport>"""
        try:
            args = arg.split(maxsplit=3)
            if len(args) != 4:
                print("Usage: register_guest <name> <email> <phone> <passport>")
                return

            name, email, phone, passport = args
            guest = self.reception.register_guest(name, email, phone, passport)
            print(f"Guest registered with ID: {guest.guest_id}")
        except Exception as e:
            print(f"Error: {e}")

    def do_book_room(self, arg):
        """Book a room: book_room <guest_id> <room_number> <check_in> <check_out>
        Date format: YYYY-MM-DD"""
        try:
            args = arg.split()
            if len(args) != 4:
                print("Usage: book_room <guest_id> <room_number> <check_in> <check_out>")
                return

            guest_id = int(args[0])
            room_number = int(args[1])
            check_in = args[2]
            check_out = args[3]

            booking = self.reception.book_room(guest_id, room_number, check_in, check_out)
            print(f"Booking created with ID: {booking.booking_id}")
        except (ValueError, RoomNotAvailableError, GuestNotFoundError) as e:
            print(f"Error: {e}")

    def do_check_out(self, arg):
        """Check out and pay: check_out <booking_id>"""
        try:
            if not arg:
                print("Usage: check_out <booking_id>")
                return

            booking_id = int(arg)
            total = self.reception.check_out(booking_id)
            print(f"Total amount to pay: ${total:.2f}")
            print("Payment processed successfully. Guest checked out.")
        except (ValueError, BookingNotFoundError) as e:
            print(f"Error: {e}")

    def do_add_service(self, arg):
        """Add service to guest: add_service <guest_id> <service_type>
        Service types: BREAKFAST, LAUNDRY, ROOM_SERVICE, SPA, TRANSPORT"""
        try:
            args = arg.split()
            if len(args) != 2:
                print("Usage: add_service <guest_id> <service_type>")
                return

            guest_id = int(args[0])
            service_type = ServiceType[args[1].upper()]

            if guest_id not in self.reception.guests:
                raise GuestNotFoundError(f"Guest with ID {guest_id} not found")

            price = self.service.get_service_price(service_type)
            self.reception.guests[guest_id].add_service(service_type.name, price)
            print(f"Service {service_type.name} added to guest {guest_id}. Price: ${price:.2f}")
        except (ValueError, KeyError, GuestNotFoundError, ServiceError) as e:
            print(f"Error: {e}")

    def do_list_services(self, arg):
        """List all available services: list_services"""
        for service_type, price in self.service.services.items():
            print(f"{service_type.name}: ${price:.2f}")

    def do_list_guests(self, arg):
        """List all guests: list_guests"""
        for guest in self.reception.guests.values():
            print(guest)

    def do_list_bookings(self, arg):
        """List all bookings: list_bookings [active]"""
        bookings = self.reception.bookings.values()
        if arg.lower() == "active":
            bookings = [b for b in bookings if not b.is_paid and not b.is_cancelled]

        for booking in bookings:
            print(booking)

    def do_exit(self, arg):
        """Exit the program: exit"""
        print("Thank you for using Hotel Management System. Goodbye!")
        return True

    def default(self, line):
        print(f"Unknown command: {line}. Type 'help' for available commands.")

    def do_EOF(self, arg):
        """Exit the program (Ctrl+D)"""
        return self.do_exit(arg)