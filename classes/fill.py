import uuid
import datetime

class Fill():
    def __init__(
            self, 
            order_id: str,
            side: str,
            qty: float,
            price: float,
            fill_time: datetime.datetime
            ):
        self.__fill_id=str(uuid.uuid4())
        self.__order_id=order_id
        self.__side=side
        self.__qty=qty
        self.__price=price
        self.__fill_time=fill_time
    
    def get_fill_id(self):
        return self.__fill_id

    def get_order_id(self):
        return self.__order_id
    
    def get_fill_info(self):
        return {
            'order_id': self.__order_id,
            'fill_id': self.__fill_id,
            'side': self.__side,
            'qty': self.__qty,
            'price': self.__price,
            'fill_time': self.__fill_time
        }