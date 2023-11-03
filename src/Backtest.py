from datetime import datetime
import pandas as pd
from src.models.Trade import Trade
from src.models.Order import Order
from src.data_analysis.Report import Report
from src.TradeLogic import TradeLogic

class Backtest():

    def __init__(
            self, 
            symbol: str, 
            mkt_data: list,
            trade_logic: TradeLogic,
            max_history: int=100,
            plot_report: bool=False,
            backtest_name: str=None,
            limit_history: int=None
        ):
        self.trades = []
        self.__symbol=symbol
        self.__mkt_data=mkt_data
        self.__trade_logic=trade_logic
        self.__curr_trade:Trade=None
        self.__report=None
        self.__max_history=max_history
        self.__plot_report=plot_report
        self.__name=backtest_name
        self.__limit_history=limit_history
        self.__trade_logic.set_full_history(self.__mkt_data)

    def run(self):
        print('\r\nInitializing backtest\r\n')
        for i in range(len(self.__mkt_data)):
            if i == 0:
                continue
            last=True if i == len(self.__mkt_data)-1 else False
            to_pred=(self.__mkt_data[:i] if i<self.__limit_history else self.__mkt_data[(i-self.__limit_history):i]) if self.__limit_history else self.__mkt_data[:i]
            self.__trade_logic_predict(to_pred, i, last)
        print('\r\nFinish backtest\r\n')
        self.__report=Report(self.__name,self.__symbol,self.trades)
        if self.__plot_report:
            self.__report.plot_report()
        return self.trades

    def get_report_pointer(self):
        return self.__report

    def __trade_logic_predict(self, history, step, last=False):
        try:
            date = pd.to_datetime(history[-1][0])
            curr_close_price = history[-2][4]
        except:
            return print(f'Skipping {history[-1][0]} due to history lack of data.')

        self.__trade_logic.update(history,self.__curr_trade)

        signal=self.__trade_logic.trade_logic(step)

        if self.__curr_trade != None:
            self.__curr_trade.main(history[-1])
            if self.__curr_trade.get_trade_info()['trade_state']==Trade.ENUM_TRADE_STATE_CLOSE:
                self.trades.append(self.__curr_trade)
                self.__curr_trade=None
                return
            if last or self.__trade_logic.close_trade_logic():
                if self.__curr_trade.get_trade_info()['trade_state']==Trade.ENUM_TRADE_STATE_OPEN:
                    self.__curr_trade.close_trade(curr_close_price, date)
                    self.trades.append(self.__curr_trade)
                    self.__curr_trade=None
                    return
            if self.__trade_logic.modify_logic():
                if self.__curr_trade.get_trade_info()['trade_state']==Trade.ENUM_TRADE_STATE_OPEN:
                    self.__curr_trade.modify_entry_stop_take(self.__trade_logic.new_sl,self.__trade_logic.new_tp)
                    return
        
        if signal == 1:
            if self.__curr_trade != None:
                if self.__curr_trade.get_trade_info()['trade_state']==Trade.ENUM_TRADE_STATE_OPEN:
                    if self.__curr_trade.get_trade_info()['trade_side']==Trade.ENUM_TRADE_SIDE_SOLD:
                        self.__curr_trade.close_trade(curr_close_price, date)
                        self.trades.append(self.__curr_trade)
                        self.__curr_trade=None
            else:
                self.__curr_trade=self.__new_trade(Order.ENUM_ORDER_SIDE_BUY,self.__trade_logic.qty,curr_close_price,date,self.__trade_logic.stop_loss,self.__trade_logic.take_profit)
        if signal == -1:
            if self.__curr_trade != None:
                if self.__curr_trade.get_trade_info()['trade_state']==Trade.ENUM_TRADE_STATE_OPEN:
                    if self.__curr_trade.get_trade_info()['trade_side']==Trade.ENUM_TRADE_SIDE_BOUGHT:
                        self.__curr_trade.close_trade(curr_close_price, date)
                        self.trades.append(self.__curr_trade)
                        self.__curr_trade=None
            else:
                self.__curr_trade=self.__new_trade(Order.ENUM_ORDER_SIDE_SELL,self.__trade_logic.qty,curr_close_price,date,self.__trade_logic.stop_loss,self.__trade_logic.take_profit)

    def __new_trade(
            self,
            ENUM_ORDER_SIDE,
            qty,
            price,
            time,
            stop_loss,
            take_profit
        ) -> Trade:
        return Trade(
                    Order(
                        self.__symbol,
                        ENUM_ORDER_SIDE,
                        qty,
                        price,
                        time,
                        price - stop_loss if ENUM_ORDER_SIDE==Order.ENUM_ORDER_SIDE_BUY else price + stop_loss,
                        price + take_profit if ENUM_ORDER_SIDE==Order.ENUM_ORDER_SIDE_BUY else price - take_profit
                    )
                )