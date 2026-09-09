from enum import Enum, auto


class StaffRole(Enum):
    RECEPTIONIST = auto()
    HOUSEKEEPING = auto()
    MANAGER = auto()
    CHEF = auto()
    WAITER = auto()


class Staff:
    def __init__(self, staff_id: int, name: str, role: StaffRole, contact: str):
        self.staff_id = staff_id
        self.name = name
        self.role = role
        self.contact = contact

    def __str__(self) -> str:
        return f"Staff {self.staff_id}: {self.name}, Role: {self.role.name}, Contact: {self.contact}"