from main import HOME, SENSORPATHS

import os, sys

if "." not in sys.path: sys.path.append(".")
if HOME not in sys.path: sys.path.append(HOME)


#
# Factory class for dynamically loaded Sensors.
#
class _SensorFactory:

    def __init__(self):

        # a set to remember the modules loaded so far
        self.__modules = {}



    #
    # Creates and returns a Sensor of the given type or None if the Sensor
    # could not be created.
    #
    def create_sensor(self, name, args):

        # find and import the sensor
        oldcwd = os.getcwd()
        sensor = None
        module = None

        try:

            for p in SENSORPATHS:

                try:
                    os.chdir(p)
                except OSError:
                    continue

                # reload old modules to force using the latest version; this
                # means we can edit modules while running gDesklets
                # TODO: clean up

                try:
                    sensordir = os.path.abspath(name)
                    if (not os.path.exists(sensordir)): continue

                    if (name in sys.modules): del sys.modules[name]
                    module = __import__(name)
                    path = sensordir

                    break

                except ImportError, e:
                    from utils.ErrorFormatter import ErrorFormatter
                    details = ErrorFormatter().format(sys.exc_info())
                    print details
                    continue


            if (module):
                self.__modules[name] = (module, path)

                # initalize the sensor
                os.chdir(path)
                sensor = module.new_sensor(args)

            else:
                print "Could not load sensor %(name)s" % vars()
                from utils.ErrorFormatter import ErrorFormatter
                details = ErrorFormatter().format(sys.exc_info())
                print details

                raise UserError(_("Could not find sensor '%(name)s'") % vars(),
                      _("A sensor could not be found. This usually means that "
                        "it has not been installed."),
                                show_details = False)


            return sensor

        finally:
            os.chdir(oldcwd)


_singleton = _SensorFactory()
def SensorFactory(): return _singleton
