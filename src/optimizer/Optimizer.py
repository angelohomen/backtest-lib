from src.Backtest import Backtest
from src.utils.Log import Log
from datetime import datetime
import multiprocessing
from multiprocessing import Pool

def unwrap_self_f(arg, **kwarg):
    return Optimizer.optimize_process(*arg, **kwarg)

class Optimizer():
    def __init__(
        self,
        symbol: str,
        ENUM_TIMEFRAME,
        trade_logic: list,
        limit_history: int
    ) -> None:
        self.__trade_logic=trade_logic
        self.__ENUM_TIMEFRAME=ENUM_TIMEFRAME
        self.__test_timef=None
        Log.LogMsg(Log.ENUM_MSG_TYPE_INFO, f'Called Optimizer. Number of tests={(len(trade_logic)*len(self.__ENUM_TIMEFRAME) if type(self.__ENUM_TIMEFRAME)==list else len(trade_logic))}', time=datetime.now())
        self.__symbol=symbol
        self.__bt_list=[]
        self.__limit_history=limit_history
        self.__counter=0
        
    def run(self):
        # pool = multiprocessing.Pool()
        # result=pool.map(unwrap_self_f, zip([self]*len(self.__trade_logic), self.__trade_logic))
        # pool.close()
        # self.__bt_list=result[:]
        for tl in self.__trade_logic:
            self.__bt_list.append(self.optimize_process(tl))

    def get_list(self):
        return self.__bt_list
    
    def optimize_process(self, tl):
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
        bt = Backtest(symbol=self.__symbol,ENUM_TIMEFRAME=self.__test_timef,trade_logic=tl,plot_report=False,backtest_name=f'opt/{counter}',limit_history=self.__limit_history)
        if bt: 
            Log.LogMsg(Log.ENUM_MSG_TYPE_INFO, 'Running backtest with inputs:', time=datetime.now())
            Log.LogMsg(Log.ENUM_MSG_TYPE_INFO, f'OPT {counter} | '+''.join([' | {0}={1} | '.format(k, v) for k,v in tl.get_current_inputs().items()]), time=datetime.now())
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