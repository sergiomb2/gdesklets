#!/usr/bin/python

from Assembly import Assembly
import sys

class CmdClient(object):
    ''' A simple command line interface to the Desklet control '''
    
    def __init__(self, parameters):
        if parameters == []:
            self.__print_usage()
            sys.exit(1)
            
        print "Reading current and available widget information..."
        self.__assembly = Assembly()
        self.__assembly.start()
        print "... done"
        
        # check the parameters for the command and 
        # execute it
        cmd = parameters[0]
        if cmd == 'list':
            self.__print_desklets()
        elif cmd == 'list-active':
            self.__print_active_desklets()
        elif cmd == 'list-remote':
            self.__print_remote_desklets()
        elif cmd == 'list-local':
            self.__print_local_desklets()

        elif cmd == 'list-controls':
            self.__print_controls()
        elif cmd == 'list-controls-remote':
            self.__print_remote_controls()
        elif cmd == 'list-controls-local':
            self.__print_local_controls()
            
        elif cmd == 'install':
            self.__install(parameters[1])
        elif cmd == 'install-control':
            self.__install_control(parameters[1]) 
        
        elif cmd == 'remove':
            self.remove(parameters[1])
        elif cmd == 'remove-control':
            self.__remove_control(parameters[1]) 
        
        
    
    def __print_usage(self):
        print '''Usage:
    list            - show all available desklets (installed and remotely available)
    list-active     - list all active desklets
    list-remote     - list all remote desklets
    list-local      - list all local desklets
    
    list-controls   - show all available controls (installed and remotely available)
    list-controls-remote     - list all remote controls
    list-controls-local      - list all local controls
            
    open NAME       - activate the desklet given by NAME
           
    install NAME    - install the remote desklet given by NAME
    install-control NAME	- install the control given by NAME
    
    remove  NAME    - delete the local desklet given by NAME
    remove-control  NAME    - delete the local control given by NAME
            '''
            
            
            
    def __print_active_desklets(self):
        print "Active desklets"
        print self.__assembly.get_active_displays()



    def __print_local_desklets(self):
        print "Local desklets"
        desklets = self.__assembly.get_local_desklets()
        for d in desklets:
            do = desklets[d]
            print do



    def __print_remote_desklets(self):
        print "Remote desklets"
        desklets = self.__assembly.get_remote_desklets()
        for d in desklets:
            do = desklets[d]
            print do



    def __print_desklets(self):
        print "All desklets"
        desklets = self.__assembly.get_desklets()
        for d in desklets:
            do = desklets[d]
            print do
            
            
	def __print_local_controls(self):
		print "Local controls"
        controls = self.__assembly.get_local_controls()
        for d in controls:
            do = controls[d]
            print do



    def __print_remote_controls(self):
        print "Remote controls"
        controls = self.__assembly.get_remote_controls()
        for d in controls:
            do = controls[d]
            print do



    def __print_controls(self):
        print "All controls"
        controls = self.__assembly.get_controls()
        for d in controls:
            do = controls[d]
            print do
            
    
    
    def __install(self, name):
        print "Install ", name
        d = self.__assembly.get_desklet(name)
    	if d is not None:
    		d.install_newest_version()
    	else:
    		print "No desklet with the name ", name

	
	
	def __install_control(self, name):
		print "Install ", name
    	d = self.__assembly.get_control(name)
    	if d is not None:
    		d.install_newest_version()
    	else:
    		print "No control with the name ", name

	
	
	def __remove(self, name):
		print "Remove ", name
    	d = self.__assembly.get_desklet(name)
    	if d is not None:
    		d.remove()
    	else:
    		print "No desklet with the name ", name

	
	
	def __remove_control(self, name):
		print "Remove ", name
    	d = self.__assembly.get_control(name)
    	if d is not None:
    		d.remove()
    	else:
    		print "No control with the name ", name


if __name__ == '__main__':
    parameters = sys.argv[1:]
    c = CmdClient(parameters)