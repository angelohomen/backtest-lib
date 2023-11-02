import MetaTrader5 as mt5
import pandas as pd

timeframes = {
    'TIMEFRAME_M1': mt5.TIMEFRAME_M1,
    'TIMEFRAME_M2': mt5.TIMEFRAME_M2,
    'TIMEFRAME_M3': mt5.TIMEFRAME_M3,
    'TIMEFRAME_M4': mt5.TIMEFRAME_M4,
    'TIMEFRAME_M5': mt5.TIMEFRAME_M5,
    'TIMEFRAME_M6': mt5.TIMEFRAME_M6,
    'TIMEFRAME_M10': mt5.TIMEFRAME_M10,
    'TIMEFRAME_M12': mt5.TIMEFRAME_M12,
    'TIMEFRAME_M15': mt5.TIMEFRAME_M15,
    'TIMEFRAME_M20': mt5.TIMEFRAME_M20,
    'TIMEFRAME_M30': mt5.TIMEFRAME_M30,
    'TIMEFRAME_H1': mt5.TIMEFRAME_H1,
    'TIMEFRAME_H2': mt5.TIMEFRAME_H2,
    'TIMEFRAME_H3': mt5.TIMEFRAME_H3,
    'TIMEFRAME_H4': mt5.TIMEFRAME_H4,
    'TIMEFRAME_H6': mt5.TIMEFRAME_H6,
    'TIMEFRAME_H8': mt5.TIMEFRAME_H8,
    'TIMEFRAME_H12': mt5.TIMEFRAME_H12,
    'TIMEFRAME_D1': mt5.TIMEFRAME_D1,
    'TIMEFRAME_W1': mt5.TIMEFRAME_W1,
    'TIMEFRAME_MN1': mt5.TIMEFRAME_MN1
}

class MetaTraderConnection():
    def __init__(self, server: str="", login: int=0.0, password: str=""):
        self.__server = server
        self.__login = login
        self.__password = password
        self.__logged_in = None

        if self.__logged_in:
            print('Already connected')
        elif login == 0.0:
            mt5.initialize()
            self.__logged_in = True
            self.__version = mt5.version()
            print(f'Connect Sucessfully {self.__version}')
        elif not mt5.initialize(server=self.__server, login=self.__login, password=self.__password):
            print('Could not connect with MT5')
            mt5.shutdown()
        else:
            self.__logged_in = True
            self.__version = mt5.version()
            print(f'Connect Sucessfully {self.__version}')
   
        self.__position = None
        self.__order = None

        self.__by_request = None
        self.__by_result = None

        self.__magic_number = 0

        self.__trade_history = {}

    def __del__(self):
        print(f'Disconnected from {self.__version}')

        # del self.__login
        # del self.__password
        # del self.__server
        # del self.__logged_in
        # del self.__version
        # del self.__position
        # del self.__order
        # del self.__by_request
        # del self.__magic_number
        # del self.__trade_history

    def __str__(self):
        return f'MetaTrader Connection v. {self.version}'

    def get_timeframe(self, timeframe: str):
        return timeframes[timeframe] if timeframes[timeframe] else None

    def get_symbol_ohlc(self, symbol: str, timeframe: str, date: int=0, count: int=1) -> pd.DataFrame():
        self.verify_symbol(symbol)
        timeframe = self.get_timeframe(timeframe)
        
        if timeframe == None:
            return None

        return mt5.copy_rates_from_pos(symbol, timeframe, date, count)

    def get_orders(self, symbol: str=None, ticket: str=None, group: str=None) -> pd.DataFrame():
        if symbol != None:
            return mt5.orders_get(symbol=symbol)
        elif ticket != None:
            return mt5.orders_get(ticket=ticket)
        elif group != None:
            return mt5.orders_get(group=group)
        else:
            return None

    def get_orders_total(self) -> int:
        return mt5.orders_total()

    def get_positions(self, symbol: str=None, ticket: str=None, group: str=None) -> tuple:
        if symbol != None:
            return mt5.positions_get(symbol=symbol)
        elif ticket != None:
            return mt5.positions_get(ticket=ticket)
        elif group != None:
            return mt5.positions_get(group=group)
        else:
            return None

    def get_positions_total(self) -> int:
        return mt5.positions_total()
    
    def get_symbol_select(self, symbol, select=False) -> None:
        return mt5.symbol_select(symbol,select)
    
    def get_symbols(self, group='') -> pd.DataFrame():
        return mt5.symbols_get(group)
    
    def get_market_book_add(self, symbol: str=None) -> bool:
        self.verify_symbol(symbol)
        return mt5.market_book_add(symbol)
    
    def get_symbol_book(self, symbol: str=None) -> tuple:
        self.verify_symbol(symbol)
        if self.get_market_book_add(symbol):
            return mt5.market_book_get(symbol)
        else:
            return None
        
    def get_market_book_release(self, symbol: str=None) -> pd.DataFrame():
        self.verify_symbol(symbol)
        return mt5.market_book_release(symbol)
    
    def get_symbol_info(self, symbol: str=None) -> pd.DataFrame():
        self.verify_symbol(symbol)
        return mt5.symbol_info(symbol) 

    def get_symbol_info_last(self, symbol: str=None) -> float:
        self.verify_symbol(symbol)
        return mt5.symbol_info(symbol).last

    def get_symbol_info_trade_tick_size(self, symbol: str=None) -> float:
        self.verify_symbol(symbol)
        return mt5.symbol_info(symbol).trade_tick_size

    def get_symbol_info_trade_tick_value(self, symbol: str=None) -> float:
        self.verify_symbol(symbol)
        return mt5.symbol_info(symbol).trade_tick_value

    def get_symbol_info_trade_tick_profit(self, symbol: str) -> float:
        self.verify_symbol(symbol)
        return mt5.symbol_info(symbol).trade_tick_value_profit

    def get_symbol_info_trade_tick_loss(self, symbol: str) -> float:
        self.verify_symbol(symbol)
        return mt5.symbol_info(symbol).trade_tick_value_loss

    def get_symbol_info_last_high(self, symbol: str=None) -> float:
        self.verify_symbol(symbol)
        return mt5.symbol_info(symbol).lasthigh

    def get_symbol_info_last_low(self, symbol: str=None) -> float:
        self.verify_symbol(symbol)
        return mt5.symbol_info(symbol).lastlow

    def get_symbol_info_bid(self, symbol: str=None) -> float:
        self.verify_symbol(symbol)
        return mt5.symbol_info(symbol).bid

    def get_symbol_info_bid_high(self, symbol: str) -> float:
        self.verify_symbol(symbol)
        return mt5.symbol_info(symbol).bidhigh

    def get_symbol_info_bid_low(self, symbol: str) -> float:
        self.verify_symbol(symbol)
        return mt5.symbol_info(symbol).bidlow

    def get_symbol_info_ask(self, symbol: str) -> float:
        self.verify_symbol(symbol)
        return mt5.symbol_info(symbol).ask

    def get_symbol_info_ask_high(self, symbol: str) -> float:
        self.verify_symbol(symbol)
        return mt5.symbol_info(symbol).askhigh

    def get_symbol_info_ask_low(self, symbol: str) -> float:
        self.verify_symbol(symbol)
        return mt5.symbol_info(symbol).asklow

    def get_symbol_info_volume(self, symbol: str) -> float:
        self.verify_symbol(symbol)
        return mt5.symbol_info(symbol).volume

    def get_trade_from_history(self, ticket: str=None) -> dict:
        if ticket == None:
            return self.__trade_history
        elif not self.__trade_history[ticket]:
            print(f'{ticket} not listed on orders history')
            return None
        
        return self.__trade_history[ticket]

    def get_orders_history(self, datetime_start: str, datetime_end: str, symbol: str=None) -> pd.DataFrame():
        if symbol == None:
            return mt5.history_orders_get(datetime_end, datetime_start, symbol=symbol)

        return mt5.history_orders_get(datetime_end, datetime_start, symbol=symbol)

    def get_deals_history(self, datetime_start: str, datetime_end: str, symbol: str=None) -> pd.DataFrame():
        if symbol == None:
            mt5.history_deals_get(datetime_end, datetime_start)
            
        return mt5.history_deals_get(datetime_end, datetime_start, symbol=symbol)

    def get_last_trade(self):
        if self.__by_result == None:
            print('Don\'t have any trade')
            return None
        
        return self.__by_result

    def to_string_orders(self) -> str:
        print(f'Orders = {self.last_order}')

    def to_string_positions(self) -> str:
        print(f'Positions = {self.__position}')

    def set_magic_number(self, number_magic: int=1233) -> None:
        self.__magic_number = number_magic
    
    def buy(self, volume: float, symbol: str, price: float, sl: float=0.0, tp: float=0.0, deviation: int=0, comment: str=''):
        self.verify_symbol(symbol)

        point = self.get_symbol_info_trade_tick_value(symbol=symbol)/self.get_symbol_info_trade_tick_size(symbol=symbol)

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(volume),
            "price": price,
            "sl": price - sl*point if sl != 0.0 else 0.0,
            "tp": price + tp*point if tp != 0.0 else 0.0,
            "deviation": deviation,
            "type": mt5.ORDER_TYPE_BUY,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
            "magic": self.__magic_number,
            "comment": comment,
        }

        if mt5.order_check(request) == None:
            print('Order check gone wrong')
            return None

        result = mt5.order_send(request)

        self.__by_request = request
        self.__by_result = result

        self.__trade_history[result.order] = (request, result)

        return result

    def buy_limit(self, volume: float, symbol: str, price: float, limit_price: float, sl: float=0.0, tp: float=0.0, deviation: int=0, comment: str=''):
        self.verify_symbol(symbol)

        point = self.get_symbol_info_trade_tick_value(symbol=symbol)/self.get_symbol_info_trade_tick_size(symbol=symbol)
        
        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": float(volume),
            "price": price,
            'stoplimit': limit_price,
            "sl": price - sl*point if sl != 0.0 else 0.0,
            "tp": price + tp*point if tp != 0.0 else 0.0,
            "type": mt5.ORDER_TYPE_BUY_LIMIT,
            "type_filling": mt5.ORDER_FILLING_FOK,
            "type_time": mt5.ORDER_TIME_DAY,
            "expiration": 0,
            "devitation": deviation,
            "magic": self.__magic_number,
            "comment": comment,
        }

        if mt5.order_check(request) == None:
            return None

        result = mt5.order_send(request)

        self.__by_request = request
        self.__by_result = result

        self.__trade_history[result.order] = (request, result)

        return result

    def sell(self, volume: float, symbol: str, price: float, sl: float=0.0, tp: float=0.0, deviation: int=0, comment: str=''):
        self.verify_symbol(symbol)

        point = self.get_symbol_info_trade_tick_value(symbol=symbol)/self.get_symbol_info_trade_tick_size(symbol=symbol)
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(volume),
            "price": price,
            "sl": price + sl*point if sl != 0.0 else 0.0,
            "tp": price - tp*point if tp != 0.0 else 0.0,
            "deviation": deviation,
            "type": mt5.ORDER_TYPE_SELL,
            "type_filling": mt5.ORDER_FILLING_FOK,
            "type_time": mt5.ORDER_TIME_DAY,
            "magic": self.__magic_number,
            "comment": comment,
        }

        if mt5.order_check(request) == None:
            return None

        result = mt5.order_send(request)

        self.__by_request = request
        self.__by_result = result

        self.__trade_history[result.order] = (request, result)

        return result

    def sell_limit(self, volume: float, symbol: str, price: float, limit_price: float, sl: float=0.0, tp: float=0.0, deviation: int=0, comment: str=''):
        self.verify_symbol(symbol)

        point = self.get_symbol_info_trade_tick_value(symbol=symbol)/self.get_symbol_info_trade_tick_size(symbol=symbol)

        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": float(volume),
            "price": price,
            'stoplimit': limit_price,
            "sl": price + sl*point if sl != 0.0 else 0.0,
            "tp": price - tp*point if tp != 0.0 else 0.0,
            "type": mt5.ORDER_TYPE_SELL_LIMIT,
            "type_filling": mt5.ORDER_FILLING_FOK,
            "type_time": mt5.ORDER_TIME_DAY,
            "expiration": 0,
            "devitation": deviation,
            "magic": self.__magic_number,
            "comment": comment,
        }

        if mt5.order_check(request) == None:
            return None

        result = mt5.order_send(request)

        self.__by_request = request
        self.__by_result = result

        self.__trade_history[result.order] = (request, result)

        return result
    
    def order_modify(self, order_ticket: int, volume: float, symbol: str, price: float, limit_price: float, sl: float=0.0, tp: float=0.0, deviation: int=0, comment: str=''):
        self.verify_symbol(symbol)

        point = self.get_symbol_info_trade_tick_value(symbol=symbol)/self.get_symbol_info_trade_tick_size(symbol=symbol)
        
        request = {
            "action": mt5.TRADE_ACTION_MODIFY,
            'order': order_ticket,
            "symbol": symbol,
            "volume": float(volume),
            "price": price,
            "stoplimit": limit_price,
            "sl": sl,
            "tp": tp,
            "deviation": deviation,
            "type_time": mt5.ORDER_TIME_DAY,
            "type_filling": mt5.ORDER_FILLING_FOK,
            "expiration": 0,
            "magic": self.__magic_number,
            "comment": comment,
        }

        result = mt5.order_check(request)

        if result == None:
            return None

        self.__by_request = request
        self.__by_result = result

        self.__trade_history[result.order] = (request, result)

        return result

    def position_close(self, order_request: int):
        if self.get_positions(ticket=order_request.order) == None:
            return None

        volume = float(order_request.volume)

        if order_request.request.type == mt5.ORDER_TYPE_SELL:
            m_type = mt5.ORDER_TYPE_BUY
            m_price = self.get_symbol_info_ask(symbol=order_request.request.symbol)
            m_position_id = order_request.order
            symbol = order_request.request.symbol
            magic = order_request.request.magic

        elif order_request.request.type == mt5.ORDER_TYPE_BUY:
            m_type = mt5.ORDER_TYPE_SELL
            m_price = self.get_symbol_info_bid(symbol=order_request.request.symbol)
            m_position_id = order_request.order
            symbol = order_request.request.symbol
            magic = order_request.request.magic

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "order": m_position_id,
            "symbol": symbol,
            "price": m_price,
            "volume": volume,
            "deviation": 1,
            "type": m_type,
            "type_time": mt5.ORDER_TIME_DAY,
            "type_filling": mt5.ORDER_FILLING_FOK,
            "magic": magic,
            "comment": f"Position {order_request.request.type} closed by {m_type}",
        }

        result = mt5.order_check(request)

        if result == None:
            return None

        result = mt5.order_send(request)
        
        return result

    def position_close_by(self, order_request: int, order_request_by: int):
        if self.get_positions(ticket=order_request.order) == None:
            print('gone wrong 1')
            return None
        elif self.get_positions(ticket=order_request_by.order) == None:
            print('gone wrong 2')
            return None

        request = {
            "action": mt5.TRADE_ACTION_CLOSE_BY,
            "position": order_request.order,
            "position_by": order_request_by.order,
            "magic": order_request.request.magic
        }

        result = mt5.order_check(request)

        if result == None:
            print('gone wrong')
            return None

        result = mt5.order_send(request)
        
        return result

    def verify_symbol(self, symbol: str):
        if symbol == None:
            return None

        selected = mt5.symbol_select(symbol)

        if not selected:
            return None