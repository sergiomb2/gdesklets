import os
import ConfigParser
import control.Settings

class Config(object):
    ''' a basic configuration management class for the shell. '''
    
    def __init__(self):
        self.parser = ConfigParser.ConfigParser()
        self.config_file_path = os.path.join(control.Settings.get_setting('gdesklets_home'), 'registry', 'config.ini')
        self.parser.read(self.config_file_path)
        
    
    def get(self, attr):
        try:
            return self.parser.get('Shell', attr)
        except ConfigParser.NoOptionError:
            return 0
        except ConfigParser.NoSectionError:
            self.parser.add_section('Shell')
            return 0
    
    def set(self, attr, value):
        self.parser.set('Shell', attr, value)
        self.write()
        self.parser.read(self.config_file_path)
    
    def write(self):
        fh = open(self.config_file_path, 'w')
        self.parser.write(fh)
        fh.close()