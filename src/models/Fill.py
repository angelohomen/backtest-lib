import uuid
import datetime
from src.utils.Log import Log

class Fill():
    def __init__(
            self, 
            order_id: str,
            side: str,
            qty: float,
            price: float,
            fill_time: datetime.datetime,
            logger=None
            ):
        '''
            "Fill()" class is a model for order fills.
            --------------------------------------------------------------------------
                Parameters
                    order_id -> str:
                        Fill order ID.
                    side -> str:
                        Side for this fill, taken from Order.ENUM_ORDER_SIDE.
                    qty -> float:
                        Fill quantity.
                    price -> float:
                        Fill price.
                    fill_time -> datetime:
                        Fill time.
        '''
        self.__fill_id=str(uuid.uuid4())
        self.__order_id=order_id
        self.__side=side
        self.__qty=qty
        self.__price=price
        self.__fill_time=fill_time
        if logger: logger.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_INFO,msg=f'New fill ({self.__fill_id}) - Side {self.__side} | Qty {self.__qty} | Px {self.__price} .',time=self.__fill_time)
    
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