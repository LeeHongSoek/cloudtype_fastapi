"""
    로그파일 관련...

"""
import logging as log
from logging import handlers
import datetime
import glob
import os
import logging
import time


class CustomFormatter(logging.Formatter):

    def formatTime(self, record, datefmt=None):

        ct = self.converter(record.created)
        if datefmt:
            s = time.strftime(datefmt, ct)
        else:
            t = time.strftime("%H:%M", ct)
            s = "%s" % t
        return s    
    # [def formatTime(self, record, datefmt=None):]
# [class CustomFormatter(logging.Formatter):]


log_dir = 'crawl_log'

def clear_logger(gubun=''):  # 한달전 로그파일을 삭제한다.

    date1 = datetime.date.today()  # 오늘자 날짜객체
    date2 = date1 - datetime.timedelta(days=30)  # 한달전
    # print(f'{date2.year:04d}-{date2.month:02d}-*')  

    path = f'{log_dir}/act_crawl_{gubun}.log.{date2.year:04d}-{date2.month:02d}-*'

    for filename in glob.glob(path):  # print(filename)
        os.remove(filename)
        """"
        with open(filename, 'r', encoding='UTF-8') as f:
            for line in f:
                print(line)
        """
    # [for filename in glob.glob(path):]
# [def clean_logger(gubun=''): ]

def get_logger(gubun=''):  # 로거 인스턴스를 구한다.

    # 로거 인스턴스를 만든다
    logger = log.getLogger('mylogger')

    # 포매터를 만든다  / 출력시간, 레벨이름, 파일명, 라인번호, 메시지 /
    fomatter = CustomFormatter('[%(asctime)s|%(levelname)8s|%(filename)15s:%(lineno)3s] %(message)s')

    # '스트림'과 '파일'로 로그를 출력하는 핸들러를 각각 만든다.
    fileHandler = handlers.TimedRotatingFileHandler(filename=f'{log_dir}/act_crawl_{gubun}.log', when='midnight', interval=1, encoding='utf-8')
    streamHandler = log.StreamHandler()

    # 각 핸들러에 포매터를 지정한다.
    fileHandler.setFormatter(fomatter)
    streamHandler.setFormatter(fomatter)

    # 로거 인스턴스에 스트림 핸들러와 파일핸들러를 붙인다.
    logger.addHandler(fileHandler)
    logger.addHandler(streamHandler)

    # 로거 인스턴스로 로그를 찍는다.
    logger.setLevel(log.DEBUG)  # 츨력내용 : DEBUG > INFO > WARNING > ERROR > CRITICAL
    
    # logger.setLevel(log.INFO)     # 츨력내용 : INFO > WARNING > ERROR > CRITICAL
    # logger.setLevel(log.WARNING)  # 츨력내용 : WARNING > ERROR > CRITICAL
    # logger.setLevel(log.ERROR)    # 츨력내용 : ERROR > CRITICAL
    # logger.setLevel(log.CRITICAL) # 츨력내용 : CRITICAL

    """
    logger.debug("===========================")
    logger.info("TEST START!!")
    logger.warning("스트림으로 로그가 남아요~")
    logger.error("동시에 파일로도 남으니 안심이죠~!")
    logger.critical('critical')
    """

    return logger
# [def get_logger(gubun=''):  ]
