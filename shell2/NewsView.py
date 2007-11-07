import pygtk
import gtk

try:
    import gtkhtml2     # needed to render the news
    GTKHTML2_IS_AVAILABLE = True
except ImportError:
    GTKHTML2_IS_AVAILABLE = False
    
from TitleText import TitleText

class NewsView(gtk.VBox):
    
    def __init__(self, main):
        super(NewsView, self).__init__(False, 6)

        self.__assembly = main.get_assembly()
        self.pack_start( TitleText("News", main.get_title_font_color()), False)
        
        if GTKHTML2_IS_AVAILABLE:            
            newslabel = self.__construct_news_view()
            
            scrollwin = gtk.ScrolledWindow()
            scrollwin.set_size_request(250, -1)
            #scrollwin.set_width(300)
            scrollwin.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
            scrollwin.add(newslabel)
            self.pack_start(scrollwin)
        else:
            self.pack_start( gtk.Label("You need python-gtkhtml2 installed to view the news"))



    def __construct_news_view(self):
        news = self.__assembly.get_news()
        
        news_html = '<html><head></head><body style="background:white">'
        for n in news:
            news_html += '<div style="font-size:13px; text-decoration:underline">' \
                        + n['title'] + '</div> \n' + \
                        '<div>' \
                        + n['body'] + '</div> <hr />'
        news_html += '</body></html>'
        document = gtkhtml2.Document()
        # No event handlers at this time
        document.connect('request_url', self.request_url_event)
        document.connect('link_clicked', self.link_clicked_event)
        document.clear()
        document.open_stream('text/html')
        document.write_stream(news_html)
        document.close_stream()
        
        html_view = gtkhtml2.View()
        html_view.set_document(document)
        
        return html_view
    
    
    
    def request_url_event(self, event, param):
        print "url requested with", event



    def link_clicked_event(self, event, param):
        print "link clicked with", event, param


