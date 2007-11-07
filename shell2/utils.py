''' Misc utils not related to the functionality of the desklet, 
    but instead used during testing '''

__LOG_SINGLETON = None

def log(str, s2='', s3='', l=0):
    global __LOG_SINGLETON
    if __LOG_SINGLETON is None:
        __LOG_SINGLETON = Logger()
    __LOG_SINGLETON.log(str, s2, s3, level=l)

class Logger(object):
    
    def __init__(self, output_level=0):
        self.min_level = output_level
    
    def log(self, string, s2='', s3='', s4='', s5='', s6='', level=0):
        ''' Used through the control. Makes it easy to redirect all debug output. '''
        if level >= self.min_level:
            print "- ", string, s2, s3, s4, s5, s6



def pretty_print(l, intend=''):
    if isinstance(l, list):
        for i in l:
            if isinstance(i, list) or isinstance(i, dict):
                pretty_print(i, intend+'  ')
            else:
                print intend,"-", i
    elif isinstance(l, dict):
        for i in l:
            if isinstance(l[i], list) or isinstance(l[i], dict):
                print intend,"-",i,"="
                pretty_print(l[i], intend+'  ')
            else:
                print intend,"-",i, "=", l[i]
    
    if intend=='': print "------------------------------------------------"
    
    
pp = pretty_print