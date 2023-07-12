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


log_dir = 'log'


def clean_logger(gubun=''):  # 한달전 로그파일을 삭제한다.

    date1 = datetime.date.today()  # 오늘자 날짜객체
    date2 = date1 - datetime.timedelta(days=30)  # 한달전

    # print('{:04d}-{:02d}-*'.format(date2.year, date2.month))  #

    path = '{}/crawling_{}.log.{:04d}-{:02d}-*'.format(log_dir, gubun, date2.year, date2.month)
    for filename in glob.glob(path):
        # print(filename)
        os.remove(filename)
        """"
        with open(filename, 'r', encoding='UTF-8') as f:
            for line in f:
                print(line)
        """
    #


def get_logger(gubun=''):  # 로거 인스턴스를 구한다.

    # 로거 인스턴스를 만든다
    logger = log.getLogger('mylogger')

    # 포매터를 만든다  / 출력시간, 레벨이름, 파일명, 라인번호, 메시지 /
    # fomatter = log.Formatter(' %(asctime)10s [ %(levelname)8s | %(filename)15s:%(lineno)3s ] %(message)s')
    #fomatter = log.Formatter('[%(asctime)s|%(levelname)8s| %(filename)15s:%(lineno)3s ] %(message)s')
    fomatter = CustomFormatter('[%(asctime)s|%(levelname)8s|%(filename)15s:%(lineno)3s] %(message)s')


    # '스트림'과 '파일'로 로그를 출력하는 핸들러를 각각 만든다.
    # fileHandler = log.FileHandler(filename='crawling.log', mode='w', encoding='utf-8')
    fileHandler = handlers.TimedRotatingFileHandler(filename='{}/crawling_{}.log'.format(log_dir, gubun), when='midnight', interval=1, encoding='utf-8')
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
#


