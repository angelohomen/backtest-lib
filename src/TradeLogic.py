import pandas as pd
from src.models.Trade import Trade
from src.indicators.MovingAverage import MovingAverage

class TradeLogic():
    def __init__(
        self,
        qty: float,
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
                    stop_loss -> float (optional):
                        Order stop price.
                    take_profit -> float (optional):
                        Order stop price.
        '''
        self.__history=None
        self.qty=abs(qty)
        self.stop_loss=abs(stop_loss)
        self.take_profit=abs(take_profit)
        self.new_sl=0
        self.new_tp=0
        self.__trade:Trade=None
        self.__signal=None

    def set_full_history(self, full_history):
        self.__full_history=full_history
        self.initialize_indicators()

    def initialize_indicators(self):
        self.sma = MovingAverage(self.__full_history,MovingAverage.ENUM_AVERAGE_TYPE_SMA,20).get_ma()
        self.ema = MovingAverage(self.__full_history,MovingAverage.ENUM_AVERAGE_TYPE_EMA,44).get_ma()

    def update(self, history,trade):
        self.__history=history
        self.__trade=trade

    def trade_logic(self, step) -> int:
        self.__step=step
        try:
            date = pd.to_datetime(self.__history[-1][0])
            curr_close_price = self.__history[-2][4]
            curr_sma = self.sma[step-1]
            curr_ema = self.ema[step-1]
            buy_signal=curr_sma>curr_ema and curr_close_price>curr_sma
            sell_signal=curr_sma<curr_ema and curr_close_price<curr_sma
            self.__signal=1 if buy_signal else -1 if sell_signal else 0
            return self.__signal
        except:
            self.__signal=0
            return 0

    def close_trade_logic(self):
        return False

    def modify_logic(self) -> dict:
        try:
            date = pd.to_datetime(self.__history[-1][0])
            curr_close_price = self.__history[-2][4]
            if self.__signal==0:
                return False
            if self.__signal==1:
                if self.__trade.get_trade_info()['trade_side']==Trade.ENUM_TRADE_SIDE_BOUGHT:
                    update=False
                    new_sl=curr_close_price-self.stop_loss
                    new_tp=curr_close_price+self.take_profit
                    if self.__trade.get_trade_info()['entry_order']['stop_price']<new_sl:
                        self.new_sl=new_sl
                        update=True
                    if self.__trade.get_trade_info()['entry_order']['take_price']>new_tp:
                        self.new_tp=new_tp
                        update=True
                    return update
            if self.__signal==-1:
                if self.__trade.get_trade_info()['trade_side']==Trade.ENUM_TRADE_SIDE_SOLD:
                    update=False
                    new_sl=curr_close_price+self.stop_loss
                    new_tp=curr_close_price-self.take_profit
                    if self.__trade.get_trade_info()['entry_order']['stop_price']>new_sl:
                        self.new_sl=new_sl
                        update=True
                    if self.__trade.get_trade_info()['entry_order']['take_price']<new_tp:
                        self.new_tp=new_tp
                        update=True
                    return update
            return False
        except:
            return False