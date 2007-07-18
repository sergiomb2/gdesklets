''' All kinds of operations for local file handling that don't fit into the 
	other categories. 
	
	TODO: better, cross platform implementation. '''

import os 

def delete_directory(file):
    os.system("rm -rf \"%s\"" % (file))

def delete_file(file):
    os.system("rm \"%s\"" % (file))
