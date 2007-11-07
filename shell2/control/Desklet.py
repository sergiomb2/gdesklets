from Widget import Widget
import Settings
from utils import log
import local

class Desklet(Widget):
    
    def __init__(self, name, description, category, authors):
        super(Desklet, self).__init__(name, description, authors)
        self._install_parent_dir = Settings.get_setting('display_install_dir')
        self.__preview = None
        self.__category = category
        self.__is_active = False
        self.__displays = {}
        
        # use 0.35 
        from local import core_interface_035
        self.__core_interface = core_interface_035
        
    
    
    def activate(self, path):
        print "activating", self.name, "from ", path
        self.__core_interface.activate(path)
    
    
    
    def activate_all(self):
        ''' Activate all the display files this desklet has. '''
        for disp_name in self.displays:
            disp_path = self.displays[disp_name]['local_path']
            self.activate(disp_path)
    
    
    
    def deactivate(self):
        print "deactivating", self.__name, "from ", self.local_path
    


    def update(self, new):
        print "Desklet: update called!!"
        super(Desklet, self).update(new)
        self.preview = new.preview
        
        
        
    def update_from_dict(self, dict):
        print "Desklet: update dict called!!"
        super(Desklet, self).update_from_dict(dict)
        self.set_displays(dict['displays'])
        
    

    def install_version(self, version_number):
        ''' Install the desklet and any dependencies it might have. '''
        deps = self.get_dependencies(version_number)
        for dep in deps:
            control_object = deps[dep]['object']
            log("looking for version %s of %s" % (deps[dep]['version_number'], control_object))
            control_object.install_version(deps[dep]['version_number'])
        
        super(Desklet, self).install_version(version_number)
        
        # update local information
        dict = local.get_desklet_information( self._install_parent_dir, self.name )
        print "!!!!!!!!!!!!!!!", dict
        self.update_from_dict(dict[self.name])
    
    
    
    def add_displays(self, display_dict):
        ''' Gets a dictionary of displays and adds those to this desklet. 
            Most desklets have only one, but multi-display-packages may contain
            several display files. '''
        self.__displays.update(display_dict)
        
        
        
    def set_preview(self,pre): self.__preview = pre
    
    def get_preview(self): return self.__preview
    
    
    
    def set_is_active(self, a): self.__is_active = a
    
    def get_is_active(self): return self.__is_active
    
    
    
    def set_displays(self,ds): self.__displays = ds
    
    def get_displays(self): return self.__displays
    
    
    
    def get_category(self): return self.__category
   
   
    
    def get_latest_dependencies(self): return self.get_newest_version()['dependencies']
    
    
    
    def get_dependencies(self, ver=None): 
        if ver is None:
            version = self.get_newest_version()
        else: 
            version = self.get_version(ver)
        return version['dependencies']
    
    
    
    category = property(get_category)
    displays = property(fget=get_displays, fset=set_displays, doc='The display files that this desklet contains and their metadata in a dictionary. Only available for installed desklets.')
    preview = property(fget=get_preview, fset=set_preview, doc='The preview image of the desklet')
    dependencies = property(fget=get_dependencies, fset=None, doc='The control dependencies for the newest version of this desklet')
    is_active = property(fget=get_is_active, fset=set_is_active, doc='Boolean to determine if the desklet is active or not')