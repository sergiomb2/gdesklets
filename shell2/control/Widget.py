from utils import log
import tempfile
import remote
import local
import os
        
class Widget(object):
    ''' A superclass for desklets and controls. Should not be used directly '''
    
    
    
    def __init__(self, name, description, authors):
        if type(authors) != list:
            raise 'Widget class: the authors parameter should be a list'
        # common attributes for all widgets
        self.__name = name
        self.__description = description
        self.__authors = authors
        self.__versions = {}
        self.__available_remotely = False
        self.__remote_domain = None
        self.__current_version = None
        self.__observers = []
        
        self._install_parent_dir = None
        self._local_path = None
    
        
    
    def install_newest_version(self):
        ''' Just a simple preference method to install the latest version '''
        version_number =  self.get_newest_version()['number']
        if self.install_version(version_number):
            self.__current_version = version_number
    
    
    
    def install_version(self, version_number):
        ''' Install the given version of the widget in question. '''
        
        log("installing widget %s version %s" % (self.name, version_number))
        if self._install_parent_dir is None:
            raise "Widget.py: Attempt of installing a widget class. Should be done via subclasses." 
        
        ver = self.get_version(version_number)
        file_url = os.path.join(self.__remote_domain, ver['file_url'])
        #print "installing version", version_number, " from", file_url
        
        dest_temp_dir = tempfile.mkdtemp()
        remote.download(file_url, dest_temp_dir)
        package_file = os.path.join(dest_temp_dir, os.path.basename(file_url))
        final_destination = local.unpack(package_file, self._install_parent_dir, self.name)
        
        self.local_path = final_destination
        self.notify_observers("INSTALLED")
        
        return True
    
    
    
    def remove(self):
        ''' Uninstalls the widget by removing it from the hard-drive. '''
        import local
        path = self.local_path
        log("Widget.py: deleting widget %s from %s" % (self.name, path) )
        local.file_operations.delete_directory(path)
        
        self.local_path = None
        self.notify_observers("REMOVED")
        
        return True
    
    
    
    def set_available_remotely(self, value):
        self.__available_remotely = value
        
    
    
    def get_available_remotely(self):
        return self.__available_remotely
    
    
    
    def get_versions(self):
        return self.__versions
    
    
    
    def add_version(self, version_number, version_data):
        if not self.__versions.has_key(version_number):
            log("Widget.py: adding version for %s" % self.__name)
            self.__versions[version_number] = version_data
        else:
            log("Widget.py: %s already has version %s" % (self.__name, version_number))
            self.__versions[version_number].update(version_data)
    
    
    
    def update_version(self, version_number, data):
        self.__versions[version_number] = data
    
    
    
    def get_version(self, version_number): return self.__versions[version_number]
    
    
    
    def get_newest_version(self):
        keys = self.get_versions().keys()
        keys.sort()
        keys.reverse()
        return self.get_version(keys[0])
    
    
    
    def update(self, new):
        ''' Takes a new widget (with the same name) 
            and updates the values of this one with its values. '''
        self.description = new.description
        self.authors = new.authors
        if new.remote_domain is not None:
            self.remote_domain = new.remote_domain
        new_vers = new.get_versions()
        for ver in new_vers:
            self.add_version(ver, new_vers[ver])
    
    
    
    def update_from_dict(self, dict):
        ''' Takes a dictionary and updates values from there '''
        self.description = dict['description']
        
        
    
    def add_observer(self, func):
        self.__observers.append(func)
    
        
        
    def notify_observers(self, event):
        ''' Notifies the observers of this widget by sending the event as a string coupled with
            itself. '''
        print self.name, "notifying about", event
        for o in self.__observers:
            o(event, self)
    
    
    
    def get_name(self): return self.__name
    
    def set_name(self, name): self.__name = name
    
    
    def get_description(self): return self.__description
    
    def set_description(self, d): self.__description = d
        
        
    def get_authors(self): return self.__authors
    
    def set_authors(self, as): self.__authors = as
    
    
    def get_remote_domain(self): return self.__remote_domain
    
    def set_remote_domain(self, d): self.__remote_domain = d
    
    
    def get_install_dir(self): return self._install_parent_dir
    
    def __str__(self):
        foo = self.__name + "\t - " + self.__description
        return foo
    
    
    def get_current_version(self): return self.__current_version
    
    def set_current_version(self, cur): self.__current_version = cur
    
    
    def get_local_path(self): return self._local_path
    
    def set_local_path(self, p): self._local_path = p
    
    
    
    # define our cool properties
    name = property(get_name, set_name, None, 'The name of the widget')
    description = property(get_description, set_description, None, 'The description of the widget')
    authors = property(get_authors, set_authors, None, 'A list of author names for this widget')
    remote_domain = property(get_remote_domain, set_remote_domain, None, 'The domain under which this widget is available. None if it was not available.')
    current_version = property(get_current_version, set_current_version, None, 'The current version of the installed widget, or None if not installed.')
    local_path = property(get_local_path, set_local_path, None, 'The local path of the widget, if it is installed.')