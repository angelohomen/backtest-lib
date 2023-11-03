import pandas as pd

class TradeLogic():
    def __init__(
        self,
        stop_loss: float=0,
        take_profit: float=0
        ):
        self.__history=None

    def new_history(self, history):
        self.__history=history

    def trade_logic(self) -> int:
        try:
            date = pd.to_datetime(self.__history[-1][0])
            prev_close_price = self.__history[-2][4]
            curr_close_price = self.__history[-1][4]
            return 1 if curr_close_price>prev_close_price else -1 if curr_close_price<prev_close_price else 0
        except:
            print('Pass')
            return 0

    def close_trade_logic(self):
        return False