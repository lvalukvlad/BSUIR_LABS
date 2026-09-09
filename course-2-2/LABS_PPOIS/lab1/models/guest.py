from datetime import date
from typing import Optional


class Guest:
    def __init__(self, guest_id: int, name: str, email: str, phone: str,
                 passport: str, check_in_date: Optional[date] = None,
                 check_out_date: Optional[date] = None):
        self.guest_id = guest_id
        self.name = name
        self.email = email
        self.phone = phone
        self.passport = passport
        self.check_in_date = check_in_date
        self.check_out_date = check_out_date
        self.services_used: list[dict] = []

    def add_service(self, service_name: str, price: float) -> None:
        self.services_used.append({"name": service_name, "price": price})

    def calculate_services_total(self) -> float:
        return sum(service["price"] for service in self.services_used)

    def __str__(self) -> str:
        return f"Guest {self.guest_id}: {self.name}, Email: {self.email}, Phone: {self.phone}"