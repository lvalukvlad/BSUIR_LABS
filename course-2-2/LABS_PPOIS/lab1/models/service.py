from enum import Enum, auto
from typing import Dict
from exceptions import ServiceError


class ServiceType(Enum):
    BREAKFAST = auto()
    LAUNDRY = auto()
    ROOM_SERVICE = auto()
    SPA = auto()
    TRANSPORT = auto()


class Service:
    def __init__(self):
        self.services: Dict[ServiceType, float] = {
            ServiceType.BREAKFAST: 15.0,
            ServiceType.LAUNDRY: 10.0,
            ServiceType.ROOM_SERVICE: 20.0,
            ServiceType.SPA: 50.0,
            ServiceType.TRANSPORT: 30.0
        }

    def get_service_price(self, service_type: ServiceType) -> float:
        if service_type not in self.services:
            raise ServiceError(f"Service {service_type.name} not available")
        return self.services[service_type]

    def add_service(self, service_type: ServiceType, price: float) -> None:
        self.services[service_type] = price

    def remove_service(self, service_type: ServiceType) -> None:
        if service_type in self.services:
            del self.services[service_type]