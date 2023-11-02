from datetime import datetime
import pandas as pd
from classes.trade import Trade
from classes.order import Order
from classes.report import Report

class Backtest():

    def __init__(
            self, 
            symbol: str, 
            mkt_data: list,
            max_history: int=100,
            plot_report: bool=False
        ):
        self.trades = []
        self.__symbol=symbol
        self.__mkt_data=mkt_data
        self.__curr_trade:Trade=None
        self.__report=None
        self.__max_history=max_history
        self.__plot_report=plot_report

    def main(self):
        print('\r\nInitializing backtest\r\n')
        for i in range(len(self.__mkt_data)):
            if i == 0:
                continue
            last=True if i == len(self.__mkt_data)-1 else False
            to_pred=self.__mkt_data[:i]
            self.__predict(to_pred, last)
        print('\r\nFinish backtest\r\n')
        self.__report=Report(self.__symbol,self.trades)
        if self.__plot_report:
            self.__report.plot_report()
        return self.trades

    def get_report_pointer(self):
        return self.__report

    def __predict(self, history, last=False):
        try:
            prev_close_price = history[-2][4]
            curr_close_price = history[-1][4]
            date = pd.to_datetime(history[-1][0])

            take_profit = 1
            stop_loss = -0.5

            signal=self.__trade_logic(history)

            if self.__curr_trade != None:
                self.__curr_trade.main(history[-1])
                if self.__curr_trade.get_trade_info()['trade_state']==Trade.ENUM_TRADE_STATE_CLOSE:
                    self.trades.append(self.__curr_trade)
                    self.__curr_trade=None
                if last or self.__close_trade_logic(history):
                    if self.__curr_trade.get_trade_info()['trade_state']==Trade.ENUM_TRADE_STATE_OPEN:
                        self.__curr_trade.close_trade(curr_close_price, date)
                        self.trades.append(self.__curr_trade)
                        self.__curr_trade=None
                        return
            
            if signal == 1:
                if self.__curr_trade != None:
                    if self.__curr_trade.get_trade_info()['trade_state']==Trade.ENUM_TRADE_STATE_OPEN:
                        if self.__curr_trade.get_trade_info()['trade_side']==Trade.ENUM_TRADE_SIDE_SOLD:
                            self.__curr_trade.close_trade(curr_close_price, date)
                            self.trades.append(self.__curr_trade)
                            self.__curr_trade=None
                        else:
                            if curr_close_price > prev_close_price and curr_close_price > self.prev_traded_price:
                                self.__curr_trade.modify_entry_stop_take(curr_close_price + stop_loss,curr_close_price + take_profit)
                                self.curr_stop_loss = self.__curr_trade.get_trade_info()['entry_order']['stop_price']
                                self.curr_take_profit = self.__curr_trade.get_trade_info()['entry_order']['take_price']
                else:
                    self.prev_traded_price = curr_close_price
                    self.__curr_trade=Trade(Order(self.__symbol,Order.ENUM_ORDER_SIDE_BUY,1,curr_close_price,date,curr_close_price + stop_loss,curr_close_price + take_profit))
                    self.curr_stop_loss = self.__curr_trade.get_trade_info()['entry_order']['stop_price']
                    self.curr_take_profit = self.__curr_trade.get_trade_info()['entry_order']['take_price']
            if signal == -1:
                if self.__curr_trade != None:
                    if self.__curr_trade.get_trade_info()['trade_state']==Trade.ENUM_TRADE_STATE_OPEN:
                        if self.__curr_trade.get_trade_info()['trade_side']==Trade.ENUM_TRADE_SIDE_BOUGHT:
                            self.__curr_trade.close_trade(curr_close_price, date)
                            self.trades.append(self.__curr_trade)
                            self.__curr_trade=None
                        else:
                            if curr_close_price < prev_close_price and curr_close_price < self.prev_traded_price:
                                self.__curr_trade.modify_entry_stop_take(curr_close_price - stop_loss,curr_close_price - take_profit)
                                self.curr_stop_loss = self.__curr_trade.get_trade_info()['entry_order']['stop_price']
                                self.curr_take_profit = self.__curr_trade.get_trade_info()['entry_order']['take_price']
                else:
                    self.prev_traded_price = curr_close_price
                    self.__curr_trade=Trade(Order(self.__symbol,Order.ENUM_ORDER_SIDE_SELL,1,curr_close_price,date,curr_close_price - stop_loss,curr_close_price - take_profit))
                    self.curr_stop_loss = self.__curr_trade.get_trade_info()['entry_order']['stop_price']
                    self.curr_take_profit = self.__curr_trade.get_trade_info()['entry_order']['take_price']
        except:
            print(f'Skipping {history[-1][0]} due to history lack of data.')

    def __trade_logic(self, history):
        try:
            prev_close_price = history[-2][4]
            curr_close_price = history[-1][4]
            return 1 if curr_close_price>prev_close_price else -1 if curr_close_price<prev_close_price else 0
        except:
            print(f'Skipping {history[-1][0]} due to history lack of data.')
            return 0

    def __close_trade_logic(self, history):
        return False