try:
    import configparser  # pip install configparser
except ImportError:
    print('모듈이 없습니다.')


class ConfigFile:

    def __init__(self, file):
        self.__file = file
        self.__sction = 'Config'

        config = configparser.ConfigParser()

        config.read_file(open(file))
        try:
            self.my_name = config[self.__sction]["telegram.name"]
        except Exception as ex:
            self.my_name = ''
            print('이름({})이 없읍니다.'.format(ex))

        try:
            self.my_token = config[self.__sction]["telegram.token"]
        except Exception as ex:
            self.my_token = ''
            print('토큰({})이 없읍니다.'.format(ex))

        try:
            self.lasttime_all = config[self.__sction]["telegram.lasttime.all"]
        except Exception as ex:
            self.lasttime_all = ''
            print('토큰({})이 없읍니다.'.format(ex))

        try:
            self.lasttime_mega = config[self.__sction]["telegram.lasttime.mega"]
        except Exception as ex:
            self.lasttime_mega = ''
            print('토큰({})이 없읍니다.'.format(ex))

        try:
            self.lasttime_lotte = config[self.__sction]["telegram.lasttime.lotte"]
        except Exception as ex:
            self.lasttime_lotte = ''
            print('토큰({})이 없읍니다.'.format(ex))

        try:
            self.lasttime_cgv = config[self.__sction]["telegram.lasttime.cgv"]
        except Exception as ex:
            self.lasttime_cgv = ''
            print('토큰({})이 없읍니다.'.format(ex))

        try:
            self.lasttime_kobis = config[self.__sction]["telegram.lasttime.kobis"]
        except Exception as ex:
            self.lasttime_kobis = ''
            print('토큰({})이 없읍니다.'.format(ex))

    def writeFile(self):
        config = configparser.RawConfigParser()

        config.add_section(self.__sction)
        config.set('Config', 'telegram.name', self.my_name)
        config.set('Config', 'telegram.token', self.my_token)
        config.set('Config', 'telegram.lasttime.all', self.lasttime_all)
        config.set('Config', 'telegram.lasttime.mega', self.lasttime_mega)
        config.set('Config', 'telegram.lasttime.lotte', self.lasttime_lotte)
        config.set('Config', 'telegram.lasttime.cgv', self.lasttime_cgv)
        config.set('Config', 'telegram.lasttime.kobis', self.lasttime_kobis)

        with open(self.__file, 'w') as configfile:
            config.write(configfile)
