import os
import datetime

class Log():
    ENUM_MSG_TYPE_ERROR='ERROR'
    ENUM_MSG_TYPE_WARNING='WARNING'
    ENUM_MSG_TYPE_INFO='INFO'
    __writer = None
    __name="log"

    @staticmethod
    def LogMsg(ENUM_MSG_TYPE:str,msg:str,time:datetime.datetime=None) -> None:
        try:
            if not os.path.exists('logs'): os.mkdir('logs')
            if not Log.__writer: Log.__writer = open(f"logs/{Log.__name}.log", "w")
            if Log.__writer:
                if time:
                    Log.__writer.write(f'{time.strftime("%d-%m-%Y %H:%M:%S")} - [{ENUM_MSG_TYPE}] {msg}\n')
                else:
                    Log.__writer.write(f'[{ENUM_MSG_TYPE}] {msg}\n')
        except:
            pass

    @staticmethod
    def LogClose():
        if Log.__writer: 
            Log.__writer.close()
            Log.__writer=None

    @staticmethod
    def SetLogName(log_name='logs'):
        Log.__name=log_name