from libdesklets.controls import Control
from IEventPipe import IEventPipe


#
# Control for piping events to other desklets.
#
# This control acts as a hub providing a push based notification system with
# different channels of interests.
#
# You can use this control to subscribe to channels in order to automatically
# receive messages:
#
#   epipe.subscriptions = ["SideCandy", "System"]
#
# By binding a handler to the "event" property, you can receive broadcasted
# messages:
#
#   epipe.bind("event", on_epipe_message)
#
# In order to broadcast a message to other desklets, you put the message into
# the "event" property:
#
#   epipe.event = ("SideCandy", "my message")
#
# A message is a list of elements, where the first element is the name of the
# channel, and the second is the name of the message. The list may also contain
# further, arbitrary elements, but the channel and the message name must be
# strings.
#
class EventPipe(Control, IEventPipe):

    # table: channel -> [subscribers]
    __subscribers = {}
    
    

    def __init__(self):

        self.__my_subscriptions = []
        self.__event = None
        
        
        Control.__init__(self)


    def __get_subs(self):

        return self.__my_subscriptions


    def __set_subs(self, subs):

        # remove from subscribers list
        for channel in self.__my_subscriptions:
            self.__subscribers[channel].remove(self)

        # add to subscribers list
        for channel in subs:
            if (not channel in self.__subscribers):
                self.__subscribers[channel] = []
            if (not self in self.__subscribers[channel]):
                self.__subscribers[channel].append(self)
                
        self.__my_subscriptions = subs


    def __get_event(self):

        return self.__event
    

    def __set_event(self, message):

        self.__broadcast(message)


    def __broadcast(self, message):

        channel = message[0]
        for s in self.__subscribers.get(channel, []):
            s._send_message(message)


    def _send_message(self, message):

        self.__event = message
        self._update("event")
        self.__event = None


    def _shutdown(self):

        # remove from subscribers list
        for channel in self.__my_subscriptions:
            self.__subscribers[channel].remove(self)


    subscriptions = property(__get_subs, __set_subs,
                             doc = "The subscribed channels")
    event = property(__get_event, __set_event, "The event message; set to send "
                                             "events, bind() to receive events")



def get_class(): return EventPipe
