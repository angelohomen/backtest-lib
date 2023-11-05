import uuid
from datetime import datetime
from src.utils.Log import Log
from src.models.Order import Order
from src.data_analysis.DataManipulation import DataManipulation

class Trade():
        # Trade state
    ENUM_TRADE_STATE_OPEN='OPEN'
    ENUM_TRADE_STATE_CLOSE='CLOSE'
    ENUM_TRADE_STATE_REJECT='REJECT'

        # Trade side
    ENUM_TRADE_SIDE_BOUGHT='BOUGHT'
    ENUM_TRADE_SIDE_SOLD='SOLD'

        # Trade stop and take type of calculation
    ENUM_TAKE_STOP_CALC_TYPE_PTS='PTS'
    ENUM_TAKE_STOP_CALC_TYPE_PCTG='PCTG'

    def __init__(
            self, 
            entry_order: Order, 
            bot_id: int=-1,
            stop_loss: float=0,
            take_profit: float=0,
            ENUM_TAKE_STOP_CALC_TYPE: str=ENUM_TAKE_STOP_CALC_TYPE_PTS
        ):
        '''
            "Trade()" class is a model for trades. It manages entry and out orders.
            --------------------------------------------------------------------------
                Parameters
                    entry_order -> Order:
                        Entry order object.
                    bot_id -> int (optional):
                        Bot ID to manage more than one, if needed.
                    stop_loss -> float (optional):
                        Stop loss in points.
                    take_profit -> float (optional):
                        Take profit in points.
                    ENUM_TAKE_STOP_CALC_TYPE -> str (optional):
                        Take/Stop price calculation type.
                    log -> bool (optional):
                        Set True if want to retrieve bot logs.
        '''
        self.__bot_id=bot_id
        self.__trade_id=str(uuid.uuid4())
        self.__out_order:Order=None
        self.__trade_side=None
        self.__trade_out_time=None
        self.__stop_loss=stop_loss
        self.__take_profit=take_profit
        self.__stop_price=0
        self.__take_price=0
        self.__take_stop_calc=ENUM_TAKE_STOP_CALC_TYPE
        self.__entry_order=entry_order
        self.__set_entry_order_params()
        self.__trade_state=None
        self.__trade_creation_time=datetime.min
        self.__trade_out_time=datetime.min
        self.__dm=DataManipulation()
        Log.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_INFO,msg=f'Trade ({self.__trade_id}) created.')

    def __set_entry_order_params(self):
        if self.__entry_order:
            if self.__entry_order.get_order_info()['order_status']==Order.ENUM_ORDER_STATUS_FILLED:
                entry_price=self.__entry_order.get_order_info()['avg_fill_price']
                if self.__entry_order.get_order_info()['side']==Order.ENUM_ORDER_SIDE_BUY:
                    self.__set_trade_side(self.ENUM_TRADE_SIDE_BOUGHT)
                    self.__stop_price=self.calculate_take_stop(entry_price,self.__stop_loss,False,True)
                    self.__take_price=self.calculate_take_stop(entry_price,self.__take_profit,True,True)
                else:
                    self.__set_trade_side(self.ENUM_TRADE_SIDE_SOLD)
                    self.__stop_price=self.calculate_take_stop(entry_price,self.__stop_loss,False,False)
                    self.__take_price=self.calculate_take_stop(entry_price,self.__take_profit,True,False)
                self.__set_trade_state(self.ENUM_TRADE_STATE_OPEN)
                self.__trade_creation_time=self.__entry_order.get_order_info()['time_created']
                Log.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_INFO,msg=f'Trade ({self.__trade_id}) entry price= {entry_price}.',time=self.__trade_creation_time)
                Log.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_INFO,msg=f'Trade ({self.__trade_id}) stop price= {self.__stop_price}.',time=self.__trade_creation_time)
                Log.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_INFO,msg=f'Trade ({self.__trade_id}) take price= {self.__take_price}.',time=self.__trade_creation_time)

    def get_stop_price(self):
        return self.__stop_price
    
    def get_take_price(self):
        return self.__take_price

    def __set_trade_state(self, ENUM_TRADE_STATE: str):
        Log.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_INFO,msg=f'Trade ({self.__trade_id}) {ENUM_TRADE_STATE}.')
        self.__trade_state=ENUM_TRADE_STATE

    def __set_trade_side(self, ENUM_TRADE_SIDE: str):
        Log.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_INFO,msg=f'Trade ({self.__trade_id}) {ENUM_TRADE_SIDE}.')
        self.__trade_side=ENUM_TRADE_SIDE

    def main(self, last_mktdata):
        if not self.__trade_state in [self.ENUM_TRADE_STATE_OPEN,None]:
            return
        self.__time = last_mktdata[self.__dm.get_data_idx('time')]
        high_price = last_mktdata[self.__dm.get_data_idx('high')]
        low_price = last_mktdata[self.__dm.get_data_idx('low')]
        last_price = last_mktdata[self.__dm.get_data_idx('close')]
        entry_order_info = self.__entry_order.get_order_info()
        if entry_order_info['order_status']==Order.ENUM_ORDER_STATUS_FILLED:
            if self.__stop_price != 0 or self.__take_price != 0:
                if entry_order_info['side']==Order.ENUM_ORDER_SIDE_BUY:
                    if self.__stop_price!=0 and low_price<=self.__stop_price:
                        Log.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_INFO,msg=f'Trade ({self.__trade_id}) closing. Stop loss.',time=self.__time)
                        self.close_trade(self.__stop_price)
                    if self.__take_price!=0 and high_price>=self.__take_price:
                        Log.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_INFO,msg=f'Trade ({self.__trade_id}) closing. Take profit.',time=self.__time)
                        self.close_trade(self.__take_price)
                if entry_order_info['side']==Order.ENUM_ORDER_SIDE_SELL:
                    if self.__stop_price!=0 and high_price>=self.__stop_price:
                        Log.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_INFO,msg=f'Trade ({self.__trade_id}) closing. Stop loss.',time=self.__time)
                        self.close_trade(self.__stop_price)
                    if self.__take_price!=0 and low_price<=self.__take_price:
                        Log.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_INFO,msg=f'Trade ({self.__trade_id}) closing. Take profit.',time=self.__time)
                        self.close_trade(self.__take_price)
        if entry_order_info['order_state']==Order.ENUM_ORDER_STATE_OPEN:
            if entry_order_info['side']==Order.ENUM_ORDER_SIDE_BUY:
                if last_price>=entry_order_info['price'] or entry_order_info['price']==0:
                    self.__entry_order.fill_insert(last_price, entry_order_info['qty'], self.__time, Order.ENUM_ORDER_STATUS_FILLED)
                    self.__set_entry_order_params()
            if entry_order_info['side']==Order.ENUM_ORDER_SIDE_SELL:
                if last_price<=entry_order_info['price'] or entry_order_info['price']==0:
                    self.__entry_order.fill_insert(last_price, entry_order_info['qty'], self.__time, Order.ENUM_ORDER_STATUS_FILLED)
                    self.__set_entry_order_params()

    def modify_entry_stop_take(self, stop_price: float=0, take_price: float=0):
        entry_order_info = self.__entry_order.get_order_info()
        if entry_order_info['order_state']==Order.ENUM_ORDER_STATUS_FILLED:
            return self.replace_stop_take(stop_price, take_price)
        return False

    def modify_entry(self, price: float=0, qty: float=0):
        entry_order_info = self.__entry_order.get_order_info()
        if entry_order_info['order_state']==Order.ENUM_ORDER_STATE_OPEN:
            return self.replace_order(price, qty)
        return False
    
    def __validate_replace_stop_take(self, stop_price, take_price):
        if stop_price<0 or take_price<0:
            return False
        if stop_price==0 or take_price==0:
            return False
        if self.__entry_order.get_order_info()['order_status']!=Order.ENUM_ORDER_STATUS_FILLED:
            return False
        
    def replace_stop_take(self, stop_price: float=0, take_price: float=0):
        if not self.__validate_replace_stop_take(stop_price, take_price):
            return False
        if(self.__entry_order.get_order_info()['order_state']==Order.ENUM_ORDER_STATE_CLOSE):
            self.__entry_order.set_order_status(Order.ENUM_ORDER_STATUS_REPLACED)
            self.__stop_price=stop_price if stop_price != 0 else self.__stop_price
            self.__take_price=take_price if take_price != 0 else self.__take_price
            Log.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_INFO,msg=f'Trade ({self.__trade_id}) replacing.',time=self.__time)
            Log.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_INFO,msg=f'Trade ({self.__trade_id}) new stop price= {self.__stop_price}.',time=self.__time)
            Log.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_INFO,msg=f'Trade ({self.__trade_id}) new take price= {self.__take_price}.',time=self.__time)
            return True
        else:
            return False

    def cancel_entry(self):
        entry_order_info = self.__entry_order.get_order_info()
        if entry_order_info['order_state']==Order.ENUM_ORDER_STATE_OPEN:
            if self.__entry_order.cancel_order():
                self.__set_trade_state(self.ENUM_TRADE_STATE_CLOSE)
                return True
            else:
                return False

    def close_trade(self, price: float):
        order_info=self.__entry_order.get_order_info()
        if order_info['side']==Order.ENUM_ORDER_SIDE_BUY:
            self.__out_order=Order(order_info['symbol'],Order.ENUM_ORDER_SIDE_SELL, order_info['qty'], price, self.__time, self.__bot_id)
            if self.__out_order:
                self.__out_order.fill_insert(price, order_info['qty'], self.__time, Order.ENUM_ORDER_STATUS_FILLED)
                self.__set_trade_state(self.ENUM_TRADE_STATE_CLOSE)
                self.__trade_out_time=self.__time
                return True
        if order_info['side']==Order.ENUM_ORDER_SIDE_SELL:
            self.__out_order=Order(order_info['symbol'],Order.ENUM_ORDER_SIDE_BUY, order_info['qty'], price, self.__time, self.__bot_id)
            if self.__out_order:
                self.__out_order.fill_insert(price, order_info['qty'], self.__time, Order.ENUM_ORDER_STATUS_FILLED)
                self.__set_trade_state(self.ENUM_TRADE_STATE_CLOSE)
                self.__trade_out_time=self.__time
                return True
        return False
    
    def calculate_take_stop(self, price, value, is_take=True, bought=True):
        if self.__take_stop_calc==self.ENUM_TAKE_STOP_CALC_TYPE_PCTG:
            if is_take and bought:
                return price*(1+value/100)
            if not is_take and bought:
                return price*(1-value/100)
            if is_take and not bought:
                return price*(1-value/100)
            if not is_take and not bought:
                return price*(1+value/100)
        elif self.__take_stop_calc==self.ENUM_TAKE_STOP_CALC_TYPE_PTS:
            if is_take and bought:
                return price+value
            if not is_take and bought:
                return price-value
            if is_take and not bought:
                return price-value
            if not is_take and not bought:
                return price+value
        else:
            Log.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_ERROR,msg=f'Calculation {self.__take_stop_calc} is not available.',time=datetime.now())
            return

    def get_trade_info(self):
        return {
            'bot_id': self.__bot_id,
            'trade_id': self.__trade_id,
            'trade_state': self.__trade_state,
            'trade_side': self.__trade_side,
            'trade_creation_time': self.__trade_creation_time,
            'trade_out_time': self.__trade_out_time,
            'entry_order': self.__entry_order.get_order_info() if self.__entry_order != None else None,
            'out_order': self.__out_order.get_order_info() if self.__out_order != None else None,
            'trade_result': (self.__out_order.get_order_info()['avg_fill_price']*self.__out_order.get_order_info()['qty'] - self.__entry_order.get_order_info()['avg_fill_price']*self.__entry_order.get_order_info()['qty'] if self.__trade_side==self.ENUM_TRADE_SIDE_BOUGHT else -self.__out_order.get_order_info()['avg_fill_price']*self.__out_order.get_order_info()['qty'] + self.__entry_order.get_order_info()['avg_fill_price']*self.__entry_order.get_order_info()['qty']) if self.__entry_order != None and self.__out_order != None and self.__entry_order.get_order_info()['qty']==self.__out_order.get_order_info()['qty'] else 0
        }