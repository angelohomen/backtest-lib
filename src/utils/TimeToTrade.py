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
            Log.LogMsg(Log.ENUM_MSG_TYPE_ERROR,'time_to_open_trades cannot be bigger or equals to time_to_stop_open',time=datetime.now())
            return False
        if self.time_to_open_trades>=self.time_to_close_trades:
            Log.LogMsg(Log.ENUM_MSG_TYPE_ERROR,'time_to_open_trades cannot be bigger or equals to time_to_close_trades',time=datetime.now())
            return False
        if self.time_to_close_trades<self.time_to_stop_open:
            Log.LogMsg(Log.ENUM_MSG_TYPE_ERROR,'time_to_stop_open cannot be bigger than time_to_close_trades',time=datetime.now())
            return False
        return True

    def TimeToOpenTrades(self, current_time):
        current_time=current_time.time()
        return current_time>=self.time_to_open_trades and current_time<=self.time_to_stop_open
    
    def TimeToCloseTrades(self, current_time):
        current_time=current_time.time()
        return current_time>=self.time_to_close_trades