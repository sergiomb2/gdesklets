#
# Class for encapsulating scriptlets. A scriptlet is a part of an inline script.
# Each <script> tag defines one scriptlet. So do the action handlers. The main
# purpose of this class is to store metadata together with scriptlets, in order
# to be able to identify them.
#
class Scriptlet:

    def __init__(self, script, filename):

        self.__script = script
        self.__filename = filename

    def __get_script(self): return self.__script
    def __get_filename(self): return self.__filename

    def __get_id(self):

        ident = "%s_%d" % (self.__filename, hash(self.__script))
        return ident



    script = property(__get_script)
    filename = property(__get_filename)
    
    # each scriptlet has an ID; two different but identical scriptlet instances
    # share the same ID, thus making scriptlets comparable
    script_id = property(__get_id)
