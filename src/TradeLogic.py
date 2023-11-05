import pandas as pd
from src.utils.Log import Log
from src.models.Trade import Trade
from src.indicators.MovingAverage import MovingAverage
from src.data_analysis.DataManipulation import DataManipulation

class TradeLogic():
    def __init__(
        self,
        qty: float,
        ENUM_TAKE_STOP_CALC_TYPE: str=Trade.ENUM_TAKE_STOP_CALC_TYPE_PTS,
        stop_loss: float=0,
        take_profit: float=0
        ):
        '''
            "TradeLogic()" is a class with all algo logics to trade, called by backtest. Do not delete set_full_history, update, trade_logic, close_trade_logic or modify_logic functions.
            When you don't need these, its just return a default value like False or 0.
            --------------------------------------------------------------------------
                Parameters
                    qty -> float:
                        Order quantity.
                    ENUM_TAKE_STOP_CALC_TYPE -> str (optional):
                        Take/Stop price calculation type.
                    stop_loss -> float (optional):
                        Order stop price.
                    take_profit -> float (optional):
                        Order stop price.
                    log -> bool (optional):
                        Set True if want to retrieve bot logs.
        '''
        self.__history=None
        self.qty=abs(qty)
        self.stop_loss=abs(stop_loss)
        self.take_profit=abs(take_profit)
        self.take_stop_calc=ENUM_TAKE_STOP_CALC_TYPE
        self.new_sl=0
        self.new_tp=0
        self.__trade:Trade=None
        self.__signal=None
        self.__dm=DataManipulation()

    def set_full_history(self, full_history):
        self.__full_history=full_history
        self.initialize_indicators()

    def initialize_indicators(self):
        self.sma = MovingAverage(self.__full_history,MovingAverage.ENUM_AVERAGE_TYPE_SMA,20).get_ma()
        self.ema = MovingAverage(self.__full_history,MovingAverage.ENUM_AVERAGE_TYPE_EMA,44).get_ma()

    def update(self, history,trade):
        self.__history=history
        self.__trade=trade
        self.__time=pd.to_datetime(self.__history[-1][self.__dm.get_data_idx('time')])

    def trade_logic(self, step) -> int:
        if len(self.__history)<2:
            return 0
        curr_close_price = self.__history[-2][self.__dm.get_data_idx('close')]
        curr_sma = self.sma[step-1]
        curr_ema = self.ema[step-1]
        buy_signal=curr_sma>curr_ema and curr_close_price>curr_sma
        sell_signal=curr_sma<curr_ema and curr_close_price<curr_sma
        self.__signal=1 if buy_signal else -1 if sell_signal else 0
        return self.__signal

    def close_trade_logic(self):
        if self.__trade:
            if self.__signal == 1:
                if self.__trade.get_trade_info()['trade_state']==Trade.ENUM_TRADE_STATE_OPEN:
                    if self.__trade.get_trade_info()['trade_side']==Trade.ENUM_TRADE_SIDE_SOLD:
                        Log.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_INFO,msg=f'Close trade ({self.__trade.get_trade_info()["trade_id"]}) logic due to inverse signal.',time=self.__time)
                        return True
            if self.__signal == -1:
                if self.__trade.get_trade_info()['trade_state']==Trade.ENUM_TRADE_STATE_OPEN:
                    if self.__trade.get_trade_info()['trade_side']==Trade.ENUM_TRADE_SIDE_BOUGHT:
                        Log.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_INFO,msg=f'Close trade ({self.__trade.get_trade_info()["trade_id"]}) logic due to inverse signal.',time=self.__time)
                        return True
        return False

    def modify_logic(self) -> dict:
        if len(self.__history)<2:
            return False
        curr_close_price = self.__history[-2][self.__dm.get_data_idx('close')]
        if self.__signal==0:
            return False
        if self.__signal==1:
            if self.__trade.get_trade_info()['trade_side']==Trade.ENUM_TRADE_SIDE_BOUGHT:
                update=False
                new_sl=self.__trade.calculate_take_stop(curr_close_price, self.stop_loss, False, True)
                new_tp=self.__trade.calculate_take_stop(curr_close_price, self.stop_loss, True, True)
                if self.__trade.get_stop_price()<new_sl and new_sl>0:
                    self.new_sl=new_sl
                    update=True
                if self.__trade.get_take_price()>new_tp and new_tp>0:
                    self.new_tp=new_tp
                    update=True
                return update
        if self.__signal==-1:
            if self.__trade.get_trade_info()['trade_side']==Trade.ENUM_TRADE_SIDE_SOLD:
                update=False
                new_sl=self.__trade.calculate_take_stop(curr_close_price, self.stop_loss, False, False)
                new_tp=self.__trade.calculate_take_stop(curr_close_price, self.stop_loss, True, False)
                if self.__trade.get_stop_price()>new_sl and new_sl>0:
                    self.new_sl=new_sl
                    update=True
                if self.__trade.get_take_price()<new_tp and new_tp>0:
                    self.new_tp=new_tp
                    update=True
                return update
        return False