from Cc__Config import ConfigFile
from Cc__Logger import CcLogger

import datetime
import subprocess
from threading import Thread
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


def get_now():
    today = datetime.datetime.now()
    return f'{today:%Y-%m-%d %H:%M}'

logger = CcLogger().get_logger('Crawling')   # 파이션 로그


class Crawling:

    def __init__(self, _config_file):

        self.__crawlling_sw_all = False  # 크롤링 스위치 (전체극장체인)
        self.__crawlling_sw_mega = False  # 크롤링 스위치 (MEGA)
        self.__crawlling_sw_lotte = False  # 크롤링 스위치 (LOTTE)
        self.__crawlling_sw_cgv = False  # 크롤링 스위치 (CGV)
        self.__crawlling_sw_kobis = False  # 크롤링 스위치 (KOBIS)
        self.__updater = None  # 크롤링 중간응답을 위해..

        self.__config_file = _config_file

        self.__my_name = _config_file.my_name  # 토큰의 이름
        self.__lasttime_all = _config_file.lasttime_all  # 최근 완료일시 (전체극장체인)
        self.__lasttime_mega = _config_file.lasttime_mega  # 최근 완료일시 (MEGA)
        self.__lasttime_lotte = _config_file.lasttime_lotte  # 최근 완료일시 (LOTTE)
        self.__lasttime_cgv = _config_file.lasttime_cgv  # 최근 완료일시 (CGV)
        self.__lasttime_kobis = _config_file.lasttime_kobis  # 최근 완료일시 (KOBIS)
    # [def __init__(self, _config_file):]    

    def getMyName(self):
        return self.__my_name

    def getCrawllingSwAll(self):
        return self.__crawlling_sw_all

    def setCrawllingSwAll(self, _crawlling_sw):
        self.__crawlling_sw_all = _crawlling_sw

    def getCrawllingSwMega(self):
        return self.__crawlling_sw_mega

    def setCrawllingSwMega(self, _crawlling_sw):
        self.__crawlling_sw_mega = _crawlling_sw

    def getCrawllingSwLotte(self):
        return self.__crawlling_sw_lotte

    def setCrawllingSwLotte(self, _crawlling_sw):
        self.__crawlling_sw_lotte = _crawlling_sw

    def getCrawllingSwCgv(self):
        return self.__crawlling_sw_cgv

    def setCrawllingSwCgv(self, _crawlling_sw):
        self.__crawlling_sw_cgv = _crawlling_sw

    def getCrawllingSwKobis(self):
        return self.__crawlling_sw_kobis

    def setCrawllingSwKobis(self, _crawlling_sw):
        self.__crawlling_sw_kobis = _crawlling_sw

    def setUpdater(self, _updater):
        self.__updater = _updater

    def getLasttimeAll(self):
        return self.__lasttime_all

    def setLasttimeAll(self, _lasttime):
        self.__lasttime_all = _lasttime

    def getLasttimeMega(self):
        return self.__lasttime_mega

    def setLasttimeMega(self, _lasttime):
        self.__lasttime_mega = _lasttime

    def getLasttimeLotte(self):
        return self.__lasttime_lotte

    def setLasttimeLotte(self, _lasttime):
        self.__lasttime_lotte = _lasttime

    def getLasttimeCgv(self):
        return self.__lasttime_cgv

    def setLasttimeCgv(self, _lasttime):
        self.__lasttime_cgv = _lasttime

    def getLasttimeKobis(self):
        return self.__lasttime_kobis

    def setLasttimeKobis(self, _lasttime):
        self.__lasttime_kobis = _lasttime

    def crawling_all(self):
        while True:  # 무한 루프로 대기 ............
            if self.__crawlling_sw_all:  # ALL 크롤링 스위치(False)

                try:
                    subprocess.run(['Crawl_Mega.bat'], shell=True, check=True)
                    subprocess.run(['Crawl_Lotte.bat'], shell=True, check=True)
                    subprocess.run(['Crawl_Cgv.bat'], shell=True, check=True)
                    subprocess.run(['Crawl_Kobis.bat'], shell=True, check=True)

                    self.__config_file.lasttime_all = self.__lasttime_all = get_now()
                    self.__config_file.writeFile()

                    self.__updater.message.reply_text('크롤링을 모두 마칩니다!')

                except Exception as e:
                    message = f'크롤링 중 오류발생: {str(e)}'
                    self.__updater.message.reply_text(message)
                    logger.info(message)

                finally:
                    self.__crawlling_sw_all = False
                    self.ccLogger.clean_logger()  # 로그파일을 정리한다. 한달 전 로그 삭제
            # [if self.__crawlling_sw_all:]        
        # [while True:]            
    # [def crawling_all(self):]                

    def crawling_mega(self):
        while True:  # 무한 루프로 대기 ............
            if self.__crawlling_sw_mega:  # MEGA 크롤링 스위치(False)

                try:
                    lstMsg = self.__updater.message.text.split(' ')
                    if len(lstMsg) > 2:
                        message = '잘못된 명령입니다!'
                    else:
                        if len(lstMsg) == 2:  # 2 개의 아규먼트를 사용할 때 [날짜수지정]
                            subprocess.run(['Crawl_Mega.bat', lstMsg[1]], shell=True, check=True)
                        if len(lstMsg) == 1:
                            subprocess.run(['Crawl_Mega.bat'], shell=True, check=True)

                    self.__config_file.lasttime_mega = self.__lasttime_mega = get_now()
                    self.__config_file.writeFile()

                    message = 'MEGA 크롤링 & 전송 완료!'
                    self.__updater.message.reply_text(message)
                    logger.info(message)
                except Exception as e:
                    message = f'MEGAf 크롤링 중 오류발생: {str(e)}'
                    self.__updater.message.reply_text(message)
                    logger.info(message)

                finally:
                    self.__crawlling_sw_mega = False
                    self.ccLogger.clean_logger()  # 로그파일을 정리한다. 한달 전 로그 삭제
            # [if self.__crawlling_sw_mega:]        
        # [while True:]            
    # [def crawling_mega(self):]

    def crawling_lotte(self):
        while True:  # 무한 루프로 대기 ............
            if self.__crawlling_sw_lotte:  # LOTTE 크롤링 스위치(False)

                try:
                    lstMsg = self.__updater.message.text.split(' ')
                    if len(lstMsg) > 2:
                        message = '잘못된 명령입니다!'
                    else:
                        if len(lstMsg) == 2:  # 2 개의 아규먼트를 사용할 때 [날짜수지정]
                            subprocess.run(['Crawl_Lotte.bat', lstMsg[1]], shell=True, check=True)
                        if len(lstMsg) == 1:
                            subprocess.run(['Crawl_Lotte.bat'], shell=True, check=True)

                    self.__config_file.lasttime_lotte = self.__lasttime_lotte = get_now()
                    self.__config_file.writeFile()

                    message = 'LOTTE 크롤링 & 전송 완료!'
                    self.__updater.message.reply_text(message)
                    logger.info(message)
                except Exception as e:
                    message = f'LOTTEf 크롤링 중 오류발생: {str(e)}'
                    self.__updater.message.reply_text(message)
                    logger.info(message)

                finally:
                    self.__crawlling_sw_lotte = False
                    self.ccLogger.clean_logger()  # 로그파일을 정리한다. 한달 전 로그 삭제
            # [if self.__crawlling_sw_lotte:]        
        # [while True:]            
    # [def crawling_lotte(self):]    
    
    def crawling_cgv(self):
        while True:  # 무한 루프로 대기 ............
            if self.__crawlling_sw_cgv:  # CGV 크롤링 스위치(False)

                try:
                    lstMsg = self.__updater.message.text.split(' ')
                    if len(lstMsg) > 2:
                        message = '잘못된 명령입니다!'
                    else:
                        if len(lstMsg) == 2:  # 2 개의 아규먼트를 사용할 때 [날짜수지정]
                            subprocess.run(['Crawl_Cgv.bat', lstMsg[1]], shell=True, check=True)
                        if len(lstMsg) == 1:
                            subprocess.run(['Crawl_Cgv.bat'], shell=True, check=True)

                    self.__config_file.lasttime_cgv = self.__lasttime_cgv = get_now()
                    self.__config_file.writeFile()

                    message = 'CGV 크롤링 & 전송 완료!'
                    self.__updater.message.reply_text(message)
                    logger.info(message)
                except Exception as e:
                    message = f'CGVf 크롤링 중 오류발생: {str(e)}'
                    self.__updater.message.reply_text(message)
                    logger.info(message)

                finally:
                    self.__crawlling_sw_cgv = False
                    self.ccLogger.clean_logger()  # 로그파일을 정리한다. 한달 전 로그 삭제
            # [if self.__crawlling_sw_cgv:]        
        # [while True:]            
    # [def crawling_cgv(self):]

    def crawling_kobis(self):
        while True:  # 무한 루프로 대기 ............
            if self.__crawlling_sw_kobis:  # Kobis 크롤링 스위치(False)

                try:
                    lstMsg = self.__updater.message.text.split(' ')
                    if len(lstMsg) > 2:
                        message = '잘못된 명령입니다!'
                    else:
                        if len(lstMsg) == 2:  # 2 개의 아규먼트를 사용할 때 [날짜수지정]
                            subprocess.run(['Crawl_Kobis.bat', lstMsg[1]], shell=True, check=True)
                        if len(lstMsg) == 1:
                            subprocess.run(['Crawl_Kobis.bat'], shell=True, check=True)

                    self.__config_file.lasttime_kobis = self.__lasttime_kobis = get_now()
                    self.__config_file.writeFile()

                    message = 'KOBIS 크롤링 & 전송 완료!'
                    self.__updater.message.reply_text(message)
                    logger.info(message)
                except Exception as e:
                    message = f'KOBISf 크롤링 중 오류발생: {str(e)}'
                    self.__updater.message.reply_text(message)
                    logger.info(message)

                finally:
                    self.__crawlling_sw_kobis = False
                    self.ccLogger.clean_logger()  # 로그파일을 정리한다. 한달 전 로그 삭제
            # [if self.__crawlling_sw_kobis:]        
        # [while True:]            
    # [def crawling_kobis(self):]                
# [class Crawling:]

def start(update, context):  # /start 명령에 대한 반응

    message = f'안녕하세요!\n극장체인점 & 영진위 상영정보 크로링서비스 ({crawling.getMyName()}) 입니다.'
    update.message.reply_text(message)
    logger.info(message)


def crawl(update, context):  # /crawl  명령에 대한 반응

    if crawling.getCrawllingSwAll():  # 크롤링 시작 스위치 검사
        message = '지금 크롤링이 실행 중입니다!'
        update.message.reply_text(message)
        logger.info(message)
    else:
        message = f'크롤링 실행을 시작합니다!\n(최근 완료일시: {crawling.getLasttimeAll()})'
        update.message.reply_text(message)
        logger.info(message)

        crawling.setCrawllingSwAll(True)  # 크롤링 시작 스위치 온
        crawling.setUpdater(update)  # 텔레그램 전송을 위한 변수 등록


def crawl_all(update, context):  # /crawl_all  명령에 대한 반응

    crawl_mega(update, context)  # /crawl_mega  명령에 대한 반응
    crawl_lotte(update, context)  # /crawl_lotte  명령에 대한 반응
    crawl_cgv(update, context)  # /crawl_cgv  명령에 대한 반응
    crawl_kobis(update, context)  # /crawl_kobis  명령에 대한 반응


def crawl_mega_lotte_cgv(update, context):  # /crawl_3  명령에 대한 반응
    
    crawl_mega(update, context)  # /crawl_mega  명령에 대한 반응
    crawl_lotte(update, context)  # /crawl_lotte  명령에 대한 반응
    crawl_cgv(update, context)  # /crawl_cgv  명령에 대한 반응


def crawl_mega(update, context):  # /crawl_mega  명령에 대한 반응
    if crawling.getCrawllingSwMega():  # 크롤링 시작 스위치 검사
        message = '지금 MEGA 크롤링이 실행 중입니다!'
        update.message.reply_text(message)
        logger.info(message)
    else:
        lstMsg = update.message.text.split(' ')
        if len(lstMsg) > 2:
            message = '잘못된 명령입니다!'
        else:
            if len(lstMsg) == 1:
                dateRag = 6
            if len(lstMsg) == 2:
                try:
                    dateRag = int(lstMsg[1])

                    if dateRag < 1:
                        dateRag = 1
                    if dateRag > 13:
                        dateRag = 13
                except ValueError:
                    dateRag = 6

            message = f'MEGA 크롤링 실행(~{dateRag+1}일 후까지)을 시작합니다!\n(최근 완료일시: {crawling.getLasttimeKobis()})'

        update.message.reply_text(message)
        logger.info(message)

        crawling.setCrawllingSwMega(True)  # 크롤링 시작 스위치 온
        crawling.setUpdater(update)  # 텔레그램 전송을 위한 변수 등록


def crawl_lotte(update, context):  # /crawl_lotte  명령에 대한 반응
    if crawling.getCrawllingSwLotte():  # 크롤링 시작 스위치 검사
        message = '지금 LOTTE 크롤링이 실행 중입니다!'
        update.message.reply_text(message)
        logger.info(message)
    else:
        lstMsg = update.message.text.split(' ')
        if len(lstMsg) > 2:
            message = '잘못된 명령입니다!'
        else:
            if len(lstMsg) == 1:
                dateRag = 6
            if len(lstMsg) == 2:
                try:
                    dateRag = int(lstMsg[1])

                    if dateRag < 1:
                        dateRag = 1
                    if dateRag > 13:
                        dateRag = 13
                except ValueError:
                    dateRag = 6

            message = f'LOTTE 크롤링 실행(~{dateRag+1}일 후까지)을 시작합니다!\n(최근 완료일시: {crawling.getLasttimeKobis()})'

        update.message.reply_text(message)
        logger.info(message)

        crawling.setCrawllingSwLotte(True)  # 크롤링 시작 스위치 온
        crawling.setUpdater(update)  # 텔레그램 전송을 위한 변수 등록


def crawl_cgv(update, context):  # /crawl_cgv  명령에 대한 반응
    if crawling.getCrawllingSwCgv():  # 크롤링 시작 스위치 검사
        message = '지금 CGV 크롤링이 실행 중입니다!'
        update.message.reply_text(message)
        logger.info(message)
    else:
        lstMsg = update.message.text.split(' ')
        if len(lstMsg) > 2:
            message = '잘못된 명령입니다!'
        else:
            if len(lstMsg) == 1:
                dateRag = 6
            if len(lstMsg) == 2:
                try:
                    dateRag = int(lstMsg[1])

                    if dateRag < 1:
                        dateRag = 1
                    if dateRag > 13:
                        dateRag = 13
                except ValueError:
                    dateRag = 6

            message = f'CGV 크롤링 실행(~{dateRag+1}일 후까지)을 시작합니다!\n(최근 완료일시: {crawling.getLasttimeKobis()})'

        update.message.reply_text(message)
        logger.info(message)

        crawling.setCrawllingSwCgv(True)  # 크롤링 시작 스위치 온
        crawling.setUpdater(update)  # 텔레그램 전송을 위한 변수 등록


def crawl_kobis(update, context):  # /crawl_kobis  명령에 대한 반응
    if crawling.getCrawllingSwKobis():  # 크롤링 시작 스위치 검사
        message = '지금 KOBIS 크롤링이 실행 중입니다!'
        update.message.reply_text(message)
        logger.info(message)
    else:
        lstMsg = update.message.text.split(' ')
        if len(lstMsg) > 2:
            message = '잘못된 명령입니다!'
        else:
            if len(lstMsg) == 1:
                dateRag = 2
            if len(lstMsg) == 2:
                try:
                    dateRag = int(lstMsg[1])

                    if dateRag < 1:
                        dateRag = 1
                    if dateRag > 7:
                        dateRag = 7
                except ValueError:
                    dateRag = 2

            message = f'KOBIS 크롤링 실행(~{dateRag+1}일 후까지)을 시작합니다!\n(최근 완료일시: {crawling.getLasttimeKobis()})'

        update.message.reply_text(message)
        logger.info(message)

        crawling.setCrawllingSwKobis(True)  # 크롤링 시작 스위치 온
        crawling.setUpdater(update)  # 텔레그램 전송을 위한 변수 등록


def echo(update, context):  # Echo the user message.
    message = update.message.text
    update.message.reply_text(message)
    logger.info(message)


def error(update, context):  # Log Errors caused by Updates.
    logger.error('Update "%s" caused error "%s"', update, context.error)


if __name__ == '__main__':

    config_file = ConfigFile('Cc__Config.properties')

    # leehs : 1092046984:AAFY_n9SOuXy-IoaN9YgpEMGKYvmzMI9aa8
    # mtns7_01 : 1091699454:AAHnJlT7__keXGzj5t-J61MxO24Kqf0-n3k
    # mtns7_02 : 922349009:AAEhF288eGiTjVCaXkqrk16zw-iuINJ7Fbc

    # config_file = ConfigFile('ConfigFile.properties')

    updater = Updater(token=config_file.my_token, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))

    dp.add_handler(CommandHandler("crawl", crawl))

    dp.add_handler(CommandHandler("0", crawl_all))
    dp.add_handler(CommandHandler("crawl_all", crawl_all))

    dp.add_handler(CommandHandler("1", crawl_mega))
    dp.add_handler(CommandHandler("mega", crawl_mega))

    dp.add_handler(CommandHandler("2", crawl_lotte))
    dp.add_handler(CommandHandler("lotte", crawl_lotte))

    dp.add_handler(CommandHandler("3", crawl_cgv))
    dp.add_handler(CommandHandler("cgv", crawl_cgv))

    dp.add_handler(CommandHandler("4", crawl_kobis))
    dp.add_handler(CommandHandler("kobis", crawl_kobis))

    dp.add_handler(CommandHandler("123", crawl_mega_lotte_cgv))
    dp.add_handler(CommandHandler("7", crawl_mega_lotte_cgv))

    dp.add_handler(MessageHandler(Filters.text, echo))

    dp.add_error_handler(error)

    
    crawling = Crawling(config_file)

    Thread(target=crawling.crawling_all).start()
    Thread(target=crawling.crawling_mega).start()
    Thread(target=crawling.crawling_lotte).start()
    Thread(target=crawling.crawling_cgv).start()
    Thread(target=crawling.crawling_kobis).start()

    updater.start_polling()
    updater.idle()
# [if __name__ == '__main__':]