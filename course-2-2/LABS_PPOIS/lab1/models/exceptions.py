class HotelException(Exception):
    """Базовое исключение для ошибок отеля"""
    pass

class RoomNotAvailableError(HotelException):
    """Номер недоступен"""
    pass

class GuestNotFoundError(HotelException):
    """Гость не найден"""
    pass

class BookingNotFoundError(HotelException):
    """Бронирование не найдено"""
    pass

class PaymentError(HotelException):
    """Ошибка оплаты"""
    pass

class ServiceError(HotelException):
    """Ошибка сервиса"""
    pass