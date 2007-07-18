import os, logging

import Settings
import remote
import local
from Desklet import Desklet
from Control import Control

class Assembly:
    ''' Fetches the local and remote widgets and creates the
        list of all widgets. This is the main interface through
        which desklets and controls should be manipulated. 
        
        Just hook up all observers and call "start" '''
    
    def __init__(self):
        self.__desklets = {}
        self.__controls = {}
        self.__observers = []
        local.core_interface.initialize( Settings.get_setting('gdesklets_home'))
        


    def start(self, website_integration=False):
        # fetch controls first so that dependencies
        # may be marked correctly
        self.notify_observers("FETCH", "Looking for local widgets")
        self.__find_local_controls()
        self.__find_local_desklets()
        self.notify_observers("FETCH", "Found local widgets")
        
        if website_integration:
            self.notify_observers("FETCH", "Looking for remote widgets")
            self.__find_remote_controls()
            self.__find_remote_desklets()
            self.__find_news()
            self.notify_observers("FETCH", "Found remote widgets")
        
        self.notify_observers("FETCH", "All done")
    
       
        
    def refresh(self):
        ''' Reload all the local and remote widgets. '''
        self.__desklets = {}
        self.__controls = {}
        self.start()
        
        

    def __find_remote_desklets(self):
        self.notify_observers("FETCH", "Fetching remote desklets")
        self.remote_desklets = {}
        for (base_url, d_list, d_path, c_list, c_path) in Settings.get_setting('repositories'):
            rds = remote.get_desklets(base_url, d_list, 
                                      Settings.get_setting('cache_dir'))
            self.remote_desklets.update(rds)
            
            for d_key in rds:
                d_data = rds[d_key]
                d = Desklet(d_data['name'], d_data['description'], d_data['category'], d_data['authors'])
                d.remote_domain = base_url
                d.set_available_remotely(True)
                d.preview = d_data['preview']
                d.add_observer(self.update)
                for version_number in d_data['versions']:
                    version_object = d_data['versions'][version_number]
                    # make dependencies point to control objects
                    for dep in d_data['versions'][version_number]['dependencies']:
                        dep_object = version_object['dependencies'][dep]
                        control_object = self.get_control( dep_object['name'] )
                        d_data['versions'][version_number]['dependencies'][dep]['object'] = control_object
                        logging.info( "added to %s dependency %s" % (d_key, control_object) )
                    d.add_version(version_number, d_data['versions'][version_number])
                    
                #for ver in d_data['versions']:
                 #   d.add_version(ver)
                self.add_desklet(d)
                del(d)
    

    
    def __find_remote_controls(self):
        self.notify_observers("FETCH", "Fetching remote controls")
        self.remote_controls = {}
        for (base_url, d_list, d_path, c_list, c_path) in Settings.get_setting('repositories'):
            rds = remote.get_controls(base_url, c_list, 
                                      Settings.get_setting('cache_dir'))
            self.remote_controls.update(rds)
            
            for d_key in rds:
                d_data = rds[d_key]
                d = Control(d_data['name'], d_data['description'], d_data['authors'])
                d.remote_domain = base_url
                
                d.set_available_remotely(True)
                for version_number in d_data['versions']:
                    d.add_version(version_number, d_data['versions'][version_number])
                #for ver in d_data['versions']:
                 #   d.add_version(ver)
                self.add_control(d)
                del(d)            



    def __find_local_desklets(self):
        self.notify_observers("FETCH", "Fetching local desklets")
        self.local_desklets = {}
        for disp_dir in Settings.get_setting('display_dirs'):
            desklets_in_this_dir = local.get_desklets(disp_dir)
            self.local_desklets.update( desklets_in_this_dir )

            for d_key in desklets_in_this_dir:
                d_data = self.local_desklets[d_key]
                d = Desklet(d_data['name'], d_data['description'], d_data['category'], [d_data['author'],])
                d.preview = d_data['preview']
                d.local_path = os.path.join(disp_dir, d_data['directory'])
                
                # there is no version information for installed desklets unfortunately
                # so build one version based on what we know about the installed desklet
                if d_data['version'] is '':
                    d_data['version'] = 'Unknown'
                
                version = {'changes': 'Unknown', 'number': d_data['version'], 'dependencies':{} }
                d.add_version(d_data['version'], version)
                d.add_displays( d_data['displays'] )
                self.add_desklet(d)
                del(d)



    def __find_local_controls(self):
        self.notify_observers("FETCH", "Fetching local controls")
        self.local_controls = {}
        for cont_dir in Settings.get_setting('control_dirs'):
            self.local_controls.update( local.get_controls(cont_dir) )

        for d_key in self.local_controls:
            d_data = self.local_controls[d_key]
            d = Control(d_data['name'], '', [])
            d.local_path = d_data['directory']
            #for ver in d_data['versions']:
             #   d.add_version(ver)
            self.add_control(d)
            del(d)



    def __find_news(self):
        self.notify_observers("FETCH", "Fetching news")
        self.__news = remote.get_news(Settings.get_setting('news_url'), 
                                      Settings.get_setting('cache_dir'))
        self.__news.reverse();
        
        
    
    def add_observer(self, function):
        ''' Connects the function to to be called everytime something worth mentioning
            happens. '''
        self.__observers.append(function)
    
    
    
    def notify_observers(self, event, param):
        for func in self.__observers:
            func(event, param)
    
    
    def update(self, event, widget):
        ''' Called by widgets to notify of a change. Mostly just propagates the event up. '''
        logging.info("Assembly.py: update called with %s " % event)
        self.notify_observers(event, widget)
        
        
        
    def add_desklet(self, desklet):
        ''' Add one desklet to the internal array.'''
        name = desklet.name
        if self.__desklets.has_key(name):
            logging.info("found previous desklet", name, " in array")
            self.__desklets[ name ].update(desklet)
        else:
            logging.info("added new desklet with key", name)
            self.__desklets[ name ] = desklet
        
        
    
    def add_control(self, control):
        ''' Add one control to the internal array.'''
        name = control.get_name()
        if self.__controls.has_key(name):
            logging.info("updating previous control", name, " in array")
            self.__controls[ name ].update(control)
        else:
            logging.info("new control with key", name)
            self.__controls[ name ] = control
    
    
    
    def get_desklets(self): return self.__desklets
    
    
    def get_desklet(self, name):
        try:
            d = self.__desklets[name]
            return d
        except KeyError:
            logging.info("failed to find desklet", name)

    
    
    def get_controls(self): return self.__controls
    
    
    
    def get_control(self, name):
        try:
            d = self.__controls[name]
            return d
        except KeyError:
            logging.info("failed to find control", name)

                
    
    def get_local_desklets(self):
        foo = {}
        for d_key in self.__desklets:
            d_obj = self.__desklets[d_key]
            if d_obj.local_path is not None:
                foo[d_key] = d_obj
        return foo
    
    
    
    def get_local_controls(self): 
        foo = {}
        for d_key in self.__controls:
            d_obj = self.__controls[d_key]
            if d_obj.local_path is not None:
                foo[d_key] = d_obj
        return foo



    def get_remote_desklets(self):
        foo = {}
        for d_key in self.__desklets:
            d_obj = self.__desklets[d_key]
            if d_obj.local_path is None and d_obj.remote_domain is not None:
                foo[d_key] = d_obj
        return foo
    
    
    
    def get_remote_controls(self):
        foo = {}
        for d_key in self.__controls:
            d_obj = self.__controls[d_key]
            if d_obj.local_path is None and d_obj.remote_domain is not None:
                foo[d_key] = d_obj
        return foo



    def get_news(self): return self.__news
        

# Unit testing...
if __name__ == '__main__':
    import utils
    print "Testing ..."
    a = Assembly()
    a.start()

    #d1 = a.get_desklet('SEcondary1')
    #d1.install_newest_version()
    
    def p_d():
        c = a.get_desklets()
        for d in c:
            print "->", c[d]