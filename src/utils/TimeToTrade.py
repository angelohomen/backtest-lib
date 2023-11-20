from datetime import datetime
from src.utils.Log import Log

class TimeToTrade():

    def __init__(self, time_to_open_trades: datetime, time_to_stop_open: datetime, time_to_close_trades: datetime) -> None:
        self.time_to_open_trades=datetime.strptime(str(time_to_open_trades), '%H:%M:%S').time()
        self.time_to_stop_open=datetime.strptime(str(time_to_stop_open), '%H:%M:%S').time()
        self.time_to_close_trades=datetime.strptime(str(time_to_close_trades), '%H:%M:%S').time()
        if not self.__verify_inputs():
            raise Exception()

    def __verify_inputs(self):
        if self.time_to_open_trades>=self.time_to_stop_open:
            print('time_to_open_trades cannot be bigger or equals to time_to_stop_open')
            return False
        if self.time_to_open_trades>=self.time_to_close_trades:
            print('time_to_open_trades cannot be bigger or equals to time_to_close_trades')
            return False
        if self.time_to_close_trades<self.time_to_stop_open:
            print('time_to_stop_open cannot be bigger than time_to_close_trades')
            return False
        return True

    def TimeToOpenTrades(self, current_time):
        current_time=current_time.time()
        return current_time>=self.time_to_open_trades and current_time<=self.time_to_stop_open
    
    def TimeToCloseTrades(self, current_time):
        current_time=current_time.time()
        return current_time>=self.time_to_close_trades
    
    def get_current_inputs(self):
        return {
            'time_to_open_trades': self.time_to_open_trades.strftime('%H:%M:%S'),
            'time_to_stop_open': self.time_to_stop_open.strftime('%H:%M:%S'),
            'time_to_close_trades': self.time_to_close_trades.strftime('%H:%M:%S')
        }