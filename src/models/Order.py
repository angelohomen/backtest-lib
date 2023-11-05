import uuid
import datetime
from src.models.Fill import Fill
from src.utils.Log import Log

class Order():
        # Order state
    ENUM_ORDER_STATE_OPEN='OPEN'
    ENUM_ORDER_STATE_CLOSE='CLOSE'
    ENUM_ORDER_STATE_REJECT='REJECT'

        # Order status
    ENUM_ORDER_STATUS_NEW='NEW'
    ENUM_ORDER_STATUS_PARTIALLY_FILLED='PARTIALLY_FILLED'
    ENUM_ORDER_STATUS_FILLED='FILLED'
    ENUM_ORDER_STATUS_CANCELED='CANCELED'
    ENUM_ORDER_STATUS_REPLACED='REPLACED'
    ENUM_ORDER_STATUS_REJECTED='REJECTED'

        # Order side
    ENUM_ORDER_SIDE_BUY='BUY'
    ENUM_ORDER_SIDE_SELL='SELL'

    def __init__(
            self, 
            symbol: str,
            ENUM_ORDER_SIDE: str,
            qty: float,
            price: float,
            time_created: datetime.datetime,
            bot_id: int=-1
            ):
        '''
            "Order()" class is a model for orders.
            --------------------------------------------------------------------------
                Parameters
                    symbol -> str:
                        Order symbol.
                    ENUM_ORDER_SIDE -> str:
                        Side for this order, taken from ENUM_ORDER_SIDE.
                    qty -> float:
                        Order quantity.
                    price -> float:
                        Order price.
                    time_created -> datetime:
                        Time of order placement.
                    bot_id -> int (optional):
                        Bot ID to manage more than one, if needed.
        '''
        self.__order_id=str(uuid.uuid4())
        self.__symbol=symbol
        self.__bot_id=bot_id
        self.__side=ENUM_ORDER_SIDE
        self.__qty=qty
        self.__price=price
        self.__time_created=time_created
        self.__initialize_order_info()

    def __initialize_order_info(self):
        self.__fills_list=[]
        self.__avg_fill_price=0
        self.__filled_volume=0
        self.__last_fill_price=0
        self.__last_fill_qty=0
        self.__last_fill_time=datetime.datetime.min
        if not self.__check_first_inputs():
            self.__order_status=self.set_order_status(self.ENUM_ORDER_STATUS_REJECTED)
            return False
        else:
            self.__order_status=self.set_order_status(self.ENUM_ORDER_STATUS_NEW)
            return True

    def __check_first_inputs(self):
        if self.__price<0:
            return False
        if self.__qty<=0:
            return False
        return True

    def __set_order_state(self, ENUM_ORDER_STATE: str):
        self.__order_state=ENUM_ORDER_STATE
        Log.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_INFO,msg=f'Setting order ({self.__order_id}) state to {self.__order_state}.',time=None)

    def set_order_status(self, ENUM_ORDER_STATUS: str):
        self.__order_status=ENUM_ORDER_STATUS
        Log.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_INFO,msg=f'Setting order ({self.__order_id}) status to {self.__order_status}.',time=None)
        if self.__order_status in [self.ENUM_ORDER_STATUS_NEW, self.ENUM_ORDER_STATUS_PARTIALLY_FILLED, self.ENUM_ORDER_STATUS_REPLACED]:
            self.__set_order_state(self.ENUM_ORDER_STATE_OPEN)
        elif self.__order_status==self.ENUM_ORDER_STATUS_REJECTED:
            self.__set_order_state(self.ENUM_ORDER_STATE_REJECT)
        else:
            self.__set_order_state(self.ENUM_ORDER_STATE_CLOSE)

    def cancel_order(self):
        if(self.__order_state==self.ENUM_ORDER_STATE_OPEN):
            self.set_order_status(self.ENUM_ORDER_STATUS_CANCELED)
            return True
        else:
            Log.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_ERROR,msg=f'Cannot cancel order ({self.__order_id}).',time=None)
            return False

    def __validate_replace(self, price, qty):
        if price<0:
            return False
        if qty<=0 or qty<self.__filled_volume:
            return False
        if qty==0 and price==0:
            return False
        return True

    def replace_order(self, price: float=0, qty: float=0):
        if(self.__order_state==self.ENUM_ORDER_STATE_OPEN) and self.__validate_replace():
            self.set_order_status(self.ENUM_ORDER_STATUS_REPLACED)
            self.__price=price
            self.__qty=qty
            return True
        else:
            Log.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_ERROR,msg=f'Cannot replace order ({self.__order_id}).',time=None)
            return False

    def fill_insert(self, last_price: float, last_qty: float, fill_time: datetime.datetime, order_status: str):
        Log.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_INFO,msg=f'New order ({self.__order_id}) fill.',time=fill_time)
        self.__fills_list.append(Fill(self.__order_id, self.__side, last_qty, last_price, fill_time).get_fill_info())
        self.__avg_fill_price = last_price if self.__avg_fill_price==0 else ((self.__avg_fill_price*self.__filled_volume)+(last_price*last_qty))/(self.__filled_volume+last_qty)
        self.__filled_volume = abs(self.__filled_volume) + abs(last_qty)
        self.__last_fill_qty=abs(last_qty)
        self.__last_fill_price=last_price
        self.__last_fill_time=fill_time
        self.set_order_status(order_status)

    def get_order_info(self):
        return {
            'bot_id':self.__bot_id,
            'order_id':  self.__order_id,
            'symbol':self.__symbol,
            'side':self.__side,
            'qty':self.__qty,
            'price':self.__price,
            'time_created':self.__time_created,
            'avg_fill_price': self.__avg_fill_price,
            'filled_volume': self.__filled_volume,
            'order_state': self.__order_state,
            'order_status': self.__order_status,
            'last_fill_price': self.__last_fill_price,
            'last_fill_qty': self.__last_fill_qty,
            'last_fill_time': self.__last_fill_time,
            'fills_list':self.__fills_list
        }