try:
    import configparser  # pip install configparser
except ImportError:
    print('모듈이 없습니다.')

class ConfigFile:

    def __init__(self, file):

        def get_value(config, section, key ):        

            try:
                return config[section][key]
            except Exception as ex:
                print(f'토큰({ex})이 없읍니다.')
                return ''
        # [def get_config_value(self, config, key, variable):]

        config = configparser.ConfigParser()
        config.read_file(open(file))

        self.my_name        = get_value(config, 'String', 'telegram.name')
        self.my_token       = get_value(config, 'String', 'telegram.token')
        self.lasttime_all   = get_value(config, 'String', 'telegram.lasttime.all')
        self.lasttime_mega  = get_value(config, 'String', 'telegram.lasttime.mega')
        self.lasttime_lotte = get_value(config, 'String', 'telegram.lasttime.lotte')
        self.lasttime_cgv   = get_value(config, 'String', 'telegram.lasttime.cgv')
        self.lasttime_kobis = get_value(config, 'String', 'telegram.lasttime.kobis')

        self.sqlmap_dir = get_value(config, 'Dir', 'sqlmap_dir')
        self.db_dir     = get_value(config, 'Dir', 'db_dir')
        self.log_dir    = get_value(config, 'Dir', 'log_dir')
    # [def __init__(self, file):]

    def writeFile(self):        

        config = configparser.RawConfigParser()

        config.add_section('String')
        config.set('String', 'telegram.name',           self.my_name)
        config.set('String', 'telegram.token',          self.my_token)
        config.set('String', 'telegram.lasttime.all',   self.lasttime_all)
        config.set('String', 'telegram.lasttime.mega',  self.lasttime_mega)
        config.set('String', 'telegram.lasttime.lotte', self.lasttime_lotte)
        config.set('String', 'telegram.lasttime.cgv',   self.lasttime_cgv)
        config.set('String', 'telegram.lasttime.kobis', self.lasttime_kobis)

        config.add_section('Dir')
        config.set('Dir', 'sqlmap_dir', self.sqlmap_dir)
        config.set('Dir', 'db_dir',     self.db_dir)
        config.set('Dir', 'logfile',    self.log_dir)

        with open(self.__file, 'w') as configfile:
            config.write(configfile)
    # [def writeFile(self):]
# [class ConfigFile:]