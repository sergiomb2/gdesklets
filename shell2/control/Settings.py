import os

    
class Settings:
    ''' A singleton class that handles global variables and settings 
        that can be used through the rest of the control.
        
        Don't call this class directly. Just use module's get_setting('setting_name') '''

    __userhome = os.path.expanduser('~')
    __gdesklets_homedir = os.path.join(__userhome, ".gdesklets")
    # the dirs where desklets and controls may be found
    __display_dirs = (os.path.join(__gdesklets_homedir, "Displays"),)
    __control_dirs = (os.path.join(__gdesklets_homedir, "Controls"),)
    
    # the dirs where new ones should be installed
    __display_install_dir = os.path.join(__gdesklets_homedir, "Displays")
    __control_install_dir = os.path.join(__gdesklets_homedir, "Controls")
    
    #__display_lists_modified = os.path.join(__gdesklets_homedir, 'available_displays.modified',)
    #__display_lists_local_copy = os.path.join(__gdesklets_homedir, 'available_displays.pyon',)
    
    # the repositories where desklets and controls can be found. stored in a tuple of tuples
    # each repository tuple contains (site base url, path to desklet listing, 
    # path to desklets, path to control listing, path to controls) (all paths are relative to 
    # base url)
    __repositories = (
                      ('http://gdesklets.de', 
                       'files/desklets.0.5.pyon', 'files/', 
                       'files/controls.0.5.pyon', 'files/'),
                      )
    
    __cache_dir = os.path.join(__gdesklets_homedir, 'cache')
    
    __news_url = 'http://gdesklets.de/files/news.0.5.pyon'
    # this stuff is just for finding out the active desklets
    # TODO: find a way to get the list of displays in 0.40
    # from main.DisplayList import DisplayList
    #_DSPLIST = DisplayList(_DISPLAYLIST)
    
    
    
    def __init__(self):
        pass
    
    def get_cache_dir(self):
        return self.__cache_dir
    
    def get_display_lists_modified(self):
        return self.__display_lists_modified
    
    def get_repositories(self):
        return self.__repositories
    
    def get_display_lists_local_copy(self):
        return self.__display_lists_local_copy
    
    def get_control_dirs(self):
        return self.__control_dirs
    
    def get_display_dirs(self):
        return self.__display_dirs
    
    def get_control_install_dir(self):
        return self.__control_install_dir
    
    def get_display_install_dir(self):
        return self.__display_install_dir
        
    def get_userhome(self):
        return self.__userhome
    
    def get_gdesklets_home(self):
        return self.__gdesklets_homedir
    
    def get_news_url(self):
        return self.__news_url
    
    
_settings_singleton_instance = None

def get_setting(attr):
    ''' The interface to the settings. Just uses a singleton of Settings class 
        and returns valid settings. Raises "No such setting" on error. '''
    global _settings_singleton_instance
    if _settings_singleton_instance is None:
        _settings_singleton_instance = Settings()
    
    if attr == 'userhome':
        return _settings_singleton_instance.get_userhome()
    elif attr == 'gdesklets_home':
        return _settings_singleton_instance.get_gdesklets_home()
    elif attr == 'display_dirs':
        return _settings_singleton_instance.get_display_dirs()
    elif attr == 'control_dirs':
        return _settings_singleton_instance.get_control_dirs()
    elif attr == 'repositories':
        return _settings_singleton_instance.get_repositories()
    elif attr == 'display_lists_local_copy':
        return _settings_singleton_instance.get_display_lists_local_copy()
    elif attr == 'display_lists_modified':
        return _settings_singleton_instance.get_display_lists_modified()
    elif attr == 'cache_dir':
        return _settings_singleton_instance.get_cache_dir()
    elif attr == 'display_install_dir':
        return _settings_singleton_instance.get_display_install_dir()
    elif attr == 'control_install_dir':
        return _settings_singleton_instance.get_control_install_dir()
    elif attr == 'news_url':
        return _settings_singleton_instance.get_news_url()
    
    raise 'Settings: No such setting "'+str(attr)+'"'
    return None

