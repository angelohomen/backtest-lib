import os
import datetime

class Log():
    ENUM_MSG_TYPE_ERROR='ERROR'
    ENUM_MSG_TYPE_WARNING='WARNING'
    ENUM_MSG_TYPE_INFO='INFO'

    def __init__(self,log_name) -> None:
        self.__name=log_name
        self.__writer=open(f"logs/{self.__name}.log", "w")
        if not os.path.exists('logs'): os.mkdir('logs')
        
    def __writer_open(self):
        self.__writer=open(f"logs/{self.__name}.log", "w")

    def LogMsg(self,ENUM_MSG_TYPE:str,msg:str,time:datetime.datetime=None) -> None:
        try:
            if not self.__writer: self.__writer_open()
            if self.__writer:
                if time:
                    self.__writer.write(f'{time.strftime("%d-%m-%Y %H:%M:%S")} - [{ENUM_MSG_TYPE}] {msg}\n')
                else:
                    self.__writer.write(f'[{ENUM_MSG_TYPE}] {msg}\n')
        except:
            pass

    def LogClose(self):
        if self.__writer: 
            self.__writer.close()
            self.__writer=None