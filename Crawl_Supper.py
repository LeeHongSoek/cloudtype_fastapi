from abc import *


class Crawl(metaclass=ABCMeta):
    delayTime = 2  # 딜레이(초)

    @abstractmethod
    def crawling(self):
        pass

    @abstractmethod
    def uplodding(self):
        pass

