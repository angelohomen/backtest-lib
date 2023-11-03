import pandas as pd
from src.Trade import Trade

class TradeLogic():
    def __init__(
        self,
        qty: float,
        stop_loss: float=0,
        take_profit: float=0
        ):
        self.__history=None
        self.qty=abs(qty)
        self.stop_loss=abs(stop_loss)
        self.take_profit=abs(take_profit)
        self.new_sl=0
        self.new_tp=0
        self.__trade:Trade=None

    def update(self, history,trade):
        self.__history=history
        self.__trade=trade

    def trade_logic(self) -> int:
        try:
            date = pd.to_datetime(self.__history[-1][0])
            prev_close_price = self.__history[-3][4]
            curr_close_price = self.__history[-2][4]
            return 1 if curr_close_price>prev_close_price else -1 if curr_close_price<prev_close_price else 0
        except:
            return 0

    def close_trade_logic(self):
        return False

    def modify_logic(self) -> dict:
        try:
            date = pd.to_datetime(self.__history[-1][0])
            curr_close_price = self.__history[-2][4]

            curr_signal=self.trade_logic()

            if curr_signal==0:
                return False

            if curr_signal==1:
                if self.__trade.get_trade_info()['trade_side']==Trade.ENUM_TRADE_SIDE_BOUGHT:
                    self.new_sl=curr_close_price-self.stop_loss
                    self.new_tp=curr_close_price+self.take_profit
                    return True
            
            if curr_signal==-1:
                if self.__trade.get_trade_info()['trade_side']==Trade.ENUM_TRADE_SIDE_SOLD:
                    self.new_sl=curr_close_price+self.stop_loss
                    self.new_tp=curr_close_price-self.take_profit
                    return True

            return False
        except:
            return False
        return False