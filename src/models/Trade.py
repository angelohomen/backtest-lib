import uuid
import datetime
from src.models.Order import Order

class Trade():
        # Trade state
    ENUM_TRADE_STATE_OPEN='OPEN'
    ENUM_TRADE_STATE_CLOSE='CLOSE'
    ENUM_TRADE_STATE_REJECT='REJECT'

        # Trade side
    ENUM_TRADE_SIDE_BOUGHT='BOUGHT'
    ENUM_TRADE_SIDE_SOLD='SOLD'

    def __init__(self, entry_order: Order, bot_id: int=-1):
        '''
            "Trade()" class is a model for trades. It manages entry and out orders.
            --------------------------------------------------------------------------
                Parameters
                    entry_order -> Order:
                        Entry order object.
                    bot_id -> int (optional):
                        Bot ID to manage more than one, if needed.
        '''
        self.__bot_id=bot_id
        self.__trade_id=str(uuid.uuid4())
        self.__entry_order:Order=entry_order
        self.__out_order:Order=None
        self.__trade_side=None
        self.__trade_out_time=None
        if entry_order:
            self.__entry_order=entry_order
            if self.__entry_order.get_order_info()['side']==Order.ENUM_ORDER_SIDE_BUY:
                self.__set_trade_side(self.ENUM_TRADE_SIDE_BOUGHT)
            else:
                self.__set_trade_side(self.ENUM_TRADE_SIDE_SOLD)
            self.__set_trade_state(self.ENUM_TRADE_STATE_OPEN)
            self.__trade_creation_time=self.__entry_order.get_order_info()['time_created']
        else:
            self.__set_trade_state(self.ENUM_TRADE_STATE_REJECT)

    def __set_trade_state(self, ENUM_TRADE_STATE: str):
        self.__trade_state=ENUM_TRADE_STATE

    def __set_trade_side(self, ENUM_TRADE_SIDE: str):
        self.__trade_side=ENUM_TRADE_SIDE

    def main(self, last_mktdata):
        if not self.__trade_state==self.ENUM_TRADE_STATE_OPEN:
            return
        time = last_mktdata[0]
        high_price = last_mktdata[2]
        low_price = last_mktdata[3]
        last_price = last_mktdata[4]
        entry_order_info = self.__entry_order.get_order_info()
        if entry_order_info['order_status']==Order.ENUM_ORDER_STATUS_FILLED:
            if entry_order_info['stop_price'] != 0 or entry_order_info['take_price'] != 0:
                if entry_order_info['side']==Order.ENUM_ORDER_SIDE_BUY:
                    if entry_order_info['take_price']!=0 and high_price>=entry_order_info['take_price']:
                        self.close_trade(entry_order_info['take_price'], time)
                    if entry_order_info['stop_price']!=0 and low_price<=entry_order_info['stop_price']:
                        self.close_trade(entry_order_info['stop_price'], time)
                if entry_order_info['side']==Order.ENUM_ORDER_SIDE_SELL:
                    if entry_order_info['take_price']!=0 and low_price<=entry_order_info['take_price']:
                        self.close_trade(entry_order_info['take_price'], time)
                    if entry_order_info['stop_price']!=0 and high_price>=entry_order_info['stop_price']:
                        self.close_trade(entry_order_info['stop_price'], time)
        if entry_order_info['order_state']==Order.ENUM_ORDER_STATE_OPEN:
            if entry_order_info['side']==Order.ENUM_ORDER_SIDE_BUY:
                if last_price>=entry_order_info['price'] or entry_order_info['price']==0:
                    self.__entry_order.fill_insert(last_price, entry_order_info['qty'], time, Order.ENUM_ORDER_STATUS_FILLED)
            if entry_order_info['side']==Order.ENUM_ORDER_SIDE_SELL:
                if last_price<=entry_order_info['price'] or entry_order_info['price']==0:
                    self.__entry_order.fill_insert(last_price, entry_order_info['qty'], time, Order.ENUM_ORDER_STATUS_FILLED)

    def modify_entry_stop_take(self, stop_price: float=0, take_price: float=0):
        entry_order_info = self.__entry_order.get_order_info()
        if entry_order_info['order_state']==Order.ENUM_ORDER_STATE_CLOSE:
            return self.__entry_order.replace_stop_take(stop_price, take_price)
        return False

    def modify_entry(self, price: float=0, qty: float=0):
        entry_order_info = self.__entry_order.get_order_info()
        if entry_order_info['order_state']==Order.ENUM_ORDER_STATE_OPEN:
            return self.__entry_order.replace_order(price, qty)
        return False

    def cancel_entry(self):
        entry_order_info = self.__entry_order.get_order_info()
        if entry_order_info['order_state']==Order.ENUM_ORDER_STATE_OPEN:
            if self.__entry_order.cancel_order():
                self.__set_trade_state(self.ENUM_TRADE_STATE_CLOSE)
                return True
            else:
                return False

    def close_trade(self, price: float, time: datetime.datetime):
        order_info=self.__entry_order.get_order_info()
        if order_info['side']==Order.ENUM_ORDER_SIDE_BUY:
            self.__out_order=Order(order_info['symbol'],Order.ENUM_ORDER_SIDE_SELL, order_info['qty'], price, time, 0, 0, self.__bot_id)
            if self.__out_order:
                self.__out_order.fill_insert(price, order_info['qty'], time, Order.ENUM_ORDER_STATUS_FILLED)
                self.__set_trade_state(self.ENUM_TRADE_STATE_CLOSE)
                self.__trade_out_time=time
                return True
        if order_info['side']==Order.ENUM_ORDER_SIDE_SELL:
            self.__out_order=Order(order_info['symbol'],Order.ENUM_ORDER_SIDE_BUY, order_info['qty'], price, time, 0, 0, self.__bot_id)
            if self.__out_order:
                self.__out_order.fill_insert(price, order_info['qty'], time, Order.ENUM_ORDER_STATUS_FILLED)
                self.__set_trade_state(self.ENUM_TRADE_STATE_CLOSE)
                self.__trade_out_time=time
                return True
        return False

    def get_trade_info(self):
        return {
            'bot_id': self.__bot_id,
            'trade_id': self.__trade_id,
            'trade_state': self.__trade_state,
            'trade_side': self.__trade_side,
            'trade_creation_time': self.__trade_creation_time,
            'trade_out_time': self.__trade_out_time,
            'entry_order': self.__entry_order.get_order_info() if self.__entry_order != None else None,
            'out_order': self.__out_order.get_order_info() if self.__out_order != None else None
        }