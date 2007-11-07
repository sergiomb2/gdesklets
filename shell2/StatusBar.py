import gtk
import gobject
import threading, time


class StatusBar(gtk.Statusbar):
    
    def __init__(self):
        super(StatusBar, self).__init__()
        self.set_has_resize_grip(True)
        self.push(0, 'All ready')
        self.__progressmeter = gtk.ProgressBar()
        self.pack_start(self.__progressmeter, False, False, 6)
        self.__keep_on_pulsing = False


    def set_msg(self, msg):
        self.pop(0)
        self.push(0, msg)
    
    
    def pulse(self):
        self.__progressmeter.show()
        self.__keep_on_pulsing = True
        self.pulsator = ProgressMeterPulsar(self.__progressmeter)
        self.pulsator.start()
    
    
    def stop_pulse(self):
        self.__keep_on_pulsing = False
        self.pulsator.stop()
        self.__progressmeter.hide()
        
        
        
class ProgressMeterPulsar(threading.Thread):
    
    def __init__(self, pbar):
        threading.Thread.__init__(self)
        self.__pbar = pbar
        self.stop_now = threading.Event()
        
    def run(self):
        while not self.stop_now.isSet():
            gtk.gdk.threads_enter()
            self.__pbar.pulse()
            gtk.gdk.threads_leave()
            time.sleep(0.1)
        
    def stop(self):
        self.stop_now.set()