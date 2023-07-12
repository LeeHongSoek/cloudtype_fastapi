import datetime
from threading import Thread
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters  # pip install python-telegram-bot

from Crawling_ConfigFile import ConfigFile
from Crawling_Logger import get_logger, clean_logger
from Crawl_Mega import CrawlMega
from Crawl_Cgv import CrawlCgv
from Crawl_Lotte import CrawlLotte


def get_now():
    today = datetime.datetime.now()
    lasttime = '{:04d}-{:02d}-{:02d} {}:{}'.format(today.year, today.month, today.day, today.hour, today.minute)
    return lasttime


class Crawling:

    def __init__(self, _log, _config_file):
        self.__crawlMega = CrawlMega(True, _log)  # MEGA
        self.__crawlCgv = CrawlCgv(True, _log)  # CGV
        self.__crawlLotte = CrawlLotte(True, _log)  # LOTTE

        self.__crawlling_sw_all = False  # 크롤링 스위치 (전체극장체인)
        self.__crawlling_sw_mega = False  # 크롤링 스위치 (MEGA)
        self.__crawlling_sw_lotte = False  # 크롤링 스위치 (LOTTE)
        self.__crawlling_sw_cgv = False  # 크롤링 스위치 (CGV)
        self.__updater = None  # 크롤링 중간응답을 위해..

        self.__config_file = _config_file
        self.__my_token = self.__config_file.my_token  # telegram 토큰값
        self.__lasttime_all = self.__config_file.lasttime_all  # 최근 완료일시 (전체극장체인)
        self.__lasttime_mega = self.__config_file.lasttime_mega  # 최근 완료일시 (MEGA)
        self.__lasttime_lotte = self.__config_file.lasttime_lotte  # 최근 완료일시 (LOTTE)
        self.__lasttime_cgv = self.__config_file.lasttime_cgv  # 최근 완료일시 (CGV)

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

    #

    def crawlling_mega_exec(self):
        self.__crawlMega.crawling()
        self.__updater.message.reply_text('MEGA 크롤링 완료!!')
        self.__crawlMega.uplodding()
        self.__updater.message.reply_text('MEGA 서버업로드 완료!!')
    #

    def crawlling_lotte_exec(self):
        self.__crawlLotte.crawling()
        self.__updater.message.reply_text('LOTTE 크롤링 완료!!')
        self.__crawlLotte.uplodding()
        self.__updater.message.reply_text('LOTTE 서버업로드 완료!!')
    #

    def crawlling_cgv_exec(self):
        self.__crawlCgv.crawling()
        self.__updater.message.reply_text('CGV 크롤링 완료!!')
        self.__crawlCgv.uplodding()
        self.__updater.message.reply_text('CGV 서버업로드 완료!!')
    #

    def crawling_all(self):
        while True:  # 무한 루프로 대기 ............

            if self.__crawlling_sw_all:  # 크롤링 스위치(False)
                try:
                    self.crawlling_mega_exec()
                    self.crawlling_lotte_exec()
                    self.crawlling_cgv_exec()

                    self.__config_file.lasttime_all = self.__lasttime_all = get_now()
                    self.__config_file.writeFile()

                    self.__updater.message.reply_text('크롤링을 모두 마칩니다!')

                except:
                    message = '크롤링 중 오류발생!'
                    self.__updater.message.reply_text(message)
                    logger.info(message)

                finally:
                    self.__crawlling_sw_all = False
                    clean_logger()  # 로그파일을 정리한다. 한달전 로그 삭제
            #
        #
    #

    def crawling_mega(self):
        while True:  # 무한 루프로 대기 ............

            if self.__crawlling_sw_mega:  # MEGA 크롤링 스위치(False)
                try:
                    self.crawlling_mega_exec()

                    self.__config_file.lasttime_mega = self.__lasttime_mega = get_now()
                    self.__config_file.writeFile()

                except:
                    message = 'MEGA 크롤링 중 오류발생!'
                    self.__updater.message.reply_text(message)
                    logger.info(message)

                finally:
                    self.__crawlling_sw_mega = False
                    clean_logger()  # 로그파일을 정리한다. 한달전 로그 삭제
            #
        #
    #

    def crawling_lotte(self):
        while True:  # 무한 루프로 대기 ............

            if self.__crawlling_sw_lotte:  # LOTTE 크롤링 스위치(False)
                try:
                    self.crawlling_lotte_exec()

                    self.__config_file.lasttime_lotte = self.__lasttime_lotte = lasttime = get_now()
                    self.__config_file.writeFile()

                except:
                    message = 'LOTTE 크롤링 중 오류발생!'
                    self.__updater.message.reply_text(message)
                    logger.info(message)

                finally:
                    self.__crawlling_sw_lotte = False
                    clean_logger()  # 로그파일을 정리한다. 한달전 로그 삭제
            #
        #
    #

    def crawling_cgv(self):
        while True:  # 무한 루프로 대기 ............

            if self.__crawlling_sw_cgv:  # CGV 크롤링 스위치(False)
                try:
                    self.crawlling_cgv_exec()

                    self.__config_file.lasttime_cgv = self.__lasttime_cgv = get_now()
                    self.__config_file.writeFile()

                except:
                    message = 'CGV 크롤링 중 오류발생!'
                    self.__updater.message.reply_text(message)
                    logger.info(message)

                finally:
                    self.__crawlling_sw_cgv = False
                    clean_logger()  # 로그파일을 정리한다. 한달전 로그 삭제
            #
        #
    #
#


def start(update, context):  # /start 명령에 대한 반응
    message = '안녕하세요!\n극장체인점 상영정보 크로링서비스입니다.'
    update.message.reply_text(message)
    logger.info(message)


def crawl(update, context):  # /crawl  명령에 대한 반응
    if crawling.getCrawllingSwAll():  # 크롤링 시작 스위치 검사
        message = '지금 크롤링이 실행 중 입니다!'
        update.message.reply_text(message)
        logger.info(message)
    else:
        message = '크롤링실행을 시작 합니다!\n(최근 완료일시 : {})'.format(crawling.getLasttimeAll())
        update.message.reply_text(message)
        logger.info(message)

        crawling.setCrawllingSwAll(True)  # 크롤링 시작 스위치 온
        crawling.setUpdater(update)  # 텔래그램 전송을 위한 변수 등록


def crawl_all(update, context):  # /crawl_all  명령에 대한 반응
    crawl_mega(update, context)  # /crawl_mega  명령에 대한 반응
    crawl_lotte(update, context)  # /crawl_lotte  명령에 대한 반응
    crawl_cgv(update, context)  # /crawl_cgv  명령에 대한 반응


def crawl_mega(update, context):  # /crawl_mega  명령에 대한 반응
    if crawling.getCrawllingSwMega():  # 크롤링 시작 스위치 검사
        message = '지금 MEGA크롤링이 실행 중 입니다!'
        update.message.reply_text(message)
        logger.info(message)
    else:
        message = 'MEGA크롤링실행을 시작 합니다!\n(최근 완료일시 : {})'.format(crawling.getLasttimeMega())
        update.message.reply_text(message)
        logger.info(message)

        crawling.setCrawllingSwMega(True)  # 크롤링 시작 스위치 온
        crawling.setUpdater(update)  # 텔래그램 전송을 위한 변수 등록


def crawl_lotte(update, context):  # /crawl_lotte  명령에 대한 반응
    if crawling.getCrawllingSwLotte():  # 크롤링 시작 스위치 검사
        message = '지금 LOTTE크롤링이 실행 중 입니다!'
        update.message.reply_text(message)
        logger.info(message)
    else:
        message = 'LOTTE크롤링실행을 시작 합니다!\n(최근 완료일시 : {})'.format(crawling.getLasttimeLotte())
        update.message.reply_text(message)
        logger.info(message)

        crawling.setCrawllingSwLotte(True)  # 크롤링 시작 스위치 온
        crawling.setUpdater(update)  # 텔래그램 전송을 위한 변수 등록


def crawl_cgv(update, context):  # /crawl_cgv  명령에 대한 반응
    if crawling.getCrawllingSwCgv():  # 크롤링 시작 스위치 검사
        message = '지금 CGV크롤링이 실행 중 입니다!'
        update.message.reply_text(message)
        logger.info(message)
    else:
        message = 'CGV크롤링실행을 시작 합니다!\n(최근 완료일시 : {})'.format(crawling.getLasttimeCgv())
        update.message.reply_text(message)
        logger.info(message)

        crawling.setCrawllingSwCgv(True)  # 크롤링 시작 스위치 온
        crawling.setUpdater(update)  # 텔래그램 전송을 위한 변수 등록


def echo(update, context):  # Echo the user message.
    message = update.message.text
    update.message.reply_text(message)
    logger.info(message)


def error(update, context):  # Log Errors caused by Updates.
    logger.error('Update "%s" caused error "%s"', update, context.error)


if __name__ == '__main__':

    config_file = ConfigFile('ConfigFile.properties')

    # leehs : 1092046984:AAFY_n9SOuXy-IoaN9YgpEMGKYvmzMI9aa8
    # mtns7_01 : 1091699454:AAHnJlT7__keXGzj5t-J61MxO24Kqf0-n3k
    # mtns7_02 : 922349009:AAEhF288eGiTjVCaXkqrk16zw-iuINJ7Fbc
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

    dp.add_handler(MessageHandler(Filters.text, echo))

    dp.add_error_handler(error)

    logger = get_logger()
    crawling = Crawling(logger, config_file)
    Thread(target=crawling.crawling_all).start()
    Thread(target=crawling.crawling_mega).start()
    Thread(target=crawling.crawling_lotte).start()
    Thread(target=crawling.crawling_cgv).start()

    updater.start_polling()
    updater.idle()

# if __name__ == '__main__':
