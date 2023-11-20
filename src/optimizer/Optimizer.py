from src.Backtest import Backtest
from src.utils.Log import Log
from datetime import datetime
import multiprocessing
from multiprocessing.pool import ThreadPool

class Optimizer():
    def __init__(
        self,
        symbol: str,
        ENUM_TIMEFRAME,
        trade_logic: list,
        limit_history: int,
        df_to_opt=None
    ) -> None:
        self.__trade_logic=trade_logic
        self.__ENUM_TIMEFRAME=ENUM_TIMEFRAME
        self.__test_timef=None
        self.__symbol=symbol
        self.__bt_list=[]
        self.__limit_history=limit_history
        self.__counter=0
        self.__to_opt=df_to_opt
        
    def run(self):
        t=ThreadPool(processes=multiprocessing.cpu_count())
        self.__bt_list=t.map(self.__optimize_process, self.__trade_logic)
        t.close()

    def get_list(self):
        return self.__bt_list
    
    def __optimize_process(self, tl):
        if type(self.__ENUM_TIMEFRAME)==list:
            for timef in self.self.__ENUM_TIMEFRAME:
                self.__test_timef=timef
                self.__counter+=1
                return self.__run_bt(tl, self.__counter)
        else:
            self.__counter+=1
            self.__test_timef=self.__ENUM_TIMEFRAME
            return self.__run_bt(tl, self.__counter)

    def __run_bt(self, tl, counter):
        bt = Backtest(symbol=self.__symbol,ENUM_TIMEFRAME=self.__test_timef,trade_logic=tl,plot_report=False,limit_history=self.__limit_history,backtest_name=f'opt/{counter}',df_to_bt=self.__to_opt)
        if bt: 
            bt.run()
        return {
                'inpts': tl.get_current_inputs(),
                'bt': bt
            }
    
    def get_max_result_bt(self):
        if len(self.__bt_list)==0:
            return None
        return max(self.__bt_list,key=lambda x: x['bt'].get_report_pointer().get_backtest_results()['returns'])
    
    def get_min_drawdown_bt(self):
        if len(self.__bt_list)==0:
            return None
        return min(self.__bt_list,key=lambda x: x['bt'].get_report_pointer().get_backtest_results()['max_drawdown'])
    
    def get_max_profit_factor_bt(self):
        if len(self.__bt_list)==0:
            return None
        return max(self.__bt_list,key=lambda x: x['bt'].get_report_pointer().get_backtest_results()['profit_factor'])
    
    def get_max_sharpe_bt(self):
        if len(self.__bt_list)==0:
            return None
        return max(self.__bt_list,key=lambda x: x['bt'].get_report_pointer().get_backtest_results()['sharpe_ratio'])