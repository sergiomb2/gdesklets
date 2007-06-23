from libdesklets.controls import Control
from libdesklets import hddtemp

from IHDDTemp import IHDDTemp


class HDDTemp(Control, IHDDTemp):

    def __init__(self):
        super(Control, self).__init__()
        self.__device = None


    def __get_device(self):
        assert self.__device
        return self.__device


    def __set_device(self, dev):
        assert isinstance(dev, str)
        assert dev in self.__get_available_devices()
        self.__device = dev


    def __get_poll(self):
        assert self.__device
        return hddtemp.poll(self.__device)

    
    def __get_available_devices(self):
        return hddtemp.available_devices()


    def __get_poll_all(self):
        return hddtemp.poll_all()



    available_devices   = property(fget = __get_available_devices)
    poll_all            = property(fget = __get_poll_all)
    device              = property(fget = __get_device,
                                   fset = __set_device)
    poll                = property(fget = __get_poll)

