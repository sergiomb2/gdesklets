import urllib2
import os

def download(url, dest):
    ''' Download a package from url to the directory dest. '''
    
    # simple escape.. needs a better one perhaps
    escaped_url = url.replace(" ", "%20")
    
    print "downloading from ", escaped_url
    
    url_opener = urllib2.build_opener()
    
    request = urllib2.Request(escaped_url)
    request.add_header('User-Agent', 'Desklets Control/0.5 +http://www.gdesklets.org')
    
    stream = url_opener.open(request)
    file_basename = os.path.basename(url)
    final_destination = os.path.join(dest, file_basename)
    
    fd = open(final_destination, 'w')
    
    # the actual transfer
    fd.write(stream.read())
    
    stream.close()
    fd.close()
    
    print "downloaded to ", dest, " total path is ", final_destination