import urllib2
import urllib # need the old one for quote()
import sys
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


def get_news(url, cache_dir):
    # make appropriate names for the local copy and local modification date files
    filename = 'news.pyon'
    local_copy = os.path.join(cache_dir, filename)
    local_modification = os.path.join(cache_dir, filename+'.modified')
    
    content = _fetch_remote_file(url, local_copy, local_modification)
    
    # strip the environment
    env_globals = {'__builtin__': '',}
    env_locals = {}
    
    # eval returns a tuple
    if content is not None: 
        content = eval(content, env_globals, env_locals)[0]
    else: return []
    
    return content
    

def get_controls(base_url, list_uri, cache_dir):
    # make appropriate names for the local copy and local modification date files
    filename = base_url.split('//',1) # get the http:// part out
    filename = filename[1].split('/', 1)[0] # just get the domain part
    suffix = list_uri.rsplit('.', 1)[1]
    local_copy = os.path.join(cache_dir, filename+'.controls.'+suffix)
    local_modification = os.path.join(cache_dir, filename+'.controls.'+suffix+'.modified')
    
    remote_url = base_url+'/'+list_uri
    content = _fetch_remote_file(remote_url, local_copy, local_modification)
    
    # strip the environment
    env_globals = {'__builtin__': '',}
    env_locals = {}
    
    # eval returns a tuple
    if content is not None:
        content = eval(content, env_globals, env_locals)[0]
    else: return {}
    
    return content


def get_desklets(base_url, list_uri, cache_dir):
    # create the cache_dir
    try:
        os.mkdir(cache_dir)
    except:
        pass
    
    # make appropriate names for the local copy and local modification date files
    filename = base_url.split('//',1) # get the http:// part out
    filename = filename[1].split('/', 1)[0] # just get the domain part
    suffix = list_uri.rsplit('.', 1)[1]
    local_copy = os.path.join(cache_dir, filename+'.desklets.'+suffix)
    local_modification = os.path.join(cache_dir, filename+'.desklets.'+suffix+'.modified')
    
    remote_url = base_url+'/'+list_uri
    content = _fetch_remote_file(remote_url, local_copy, local_modification)
    
    # strip the environment
    env_globals = {'__builtin__': '',}
    env_locals = {}
    
    # eval returns a tuple
    if content is not None:
        content = eval(content, env_globals, env_locals)[0]
        content = _fetch_icons(content, cache_dir, base_url)
    else: return {}
     
    return content
    


def _fetch_remote_file(remote_file_url, local_copy_path, local_modification_date ):
        ''' Checks for the available file. If a newer version is found
            it will fetch it, but otherwise it'll use the local cache. 
            This is used for the pyon-files, not for downloading desklet packages. '''
        # look for a local copy
        local_copy_available = False
        content = ""
        
        # can't use urllib.quote() here because it replaces http:// into http%3A//
        remote_file_url = remote_file_url.replace(" ", "%20")
        # print "rfu", remote_file_url, "lcp", local_copy_path, "lmd", local_modification_date
        
        # Check for local copy
        try:
            file_name = local_copy_path
            f = open(local_copy_path)
            mod_f = open(local_modification_date)
            modification_time = mod_f.read()
            # print "Found local copy"
            local_copy_available = True
            #print "local modification date found from", local_modification_date, ":", modification_time
        except IOError:
            # print "No local copy found"
            modification_time = "0"
        
        # This try will only succeed if the local file is not up to date or does not exist
        try:
            raise ValueError("FOOOOOO!")
            request = urllib2.Request(remote_file_url)
            request.add_header('User-Agent', 'Desklets Control/0.5 +http://www.gdesklets.de')
            request.add_header('If-Modified-Since', modification_time)
            opener = urllib2.build_opener()
            stream = opener.open( request )

            content = stream.read()
   
            # create the directory if needed
            try:
                os.makedirs( os.path.dirname(local_copy_path) )
            except OSError:
                pass
            
            # cache the remote file as a local copy
            local_f = open(local_copy_path, 'w')
            local_f.write(content)
            
            # save the modification time in a file
            modification_time = stream.headers.dict['last-modified']
            mod_f = open(local_modification_date, 'w')
            mod_f.write(modification_time)

            print "* DeskletControl: updated the available displays file."

        # urllib2 raises an error even when the file was just not fetched
        # because it was not mofidied
        except urllib2.HTTPError:
            type, info, tb = sys.exc_info()
            error_string = str(info)

            # error 304 is "Not modified", so in that case we'll use the local copy
            if error_string.find('304'):
                print "* DeskletControl: local available displays file is up to date."
                local_f = open(local_copy_path)
                content = local_f.read()

        # on other errors just return None (no network, etc.)
        except:
            type, info, tb = sys.exc_info()
            error_string = str(info)
            print "! DeskletControl: available desklets \
                    from the repository could not be fetched (using local cached file if available):", error_string
            # default to old file
            try:
                local_f = open(local_copy_path)
                content = local_f.read()
            except: return None

        return content



def _fetch_icons(list, destination_dir, base_url):
        ''' Goes through "list", a dictionary full of available desklets,
            gets the icons of the desklets from the server, caches them
            and updates the list to reflect the local paths. '''

        if not os.path.exists(destination_dir): os.mkdir(destination_dir)
        url_opener = urllib2.build_opener()
        
        for desklet_key in list:
            
            # get only the screenie for the latest version
            desklet = list[desklet_key]
            desklet_name = desklet['name']
            version_numbers = desklet['versions'].keys()
            version_numbers.sort()
            newest_version = desklet['versions'][version_numbers[-1]]
            
            # the uri is stored as the path. The icon has to be cached and the path changed to local
            newest_version["screenshot_url"] = urllib.quote(newest_version["screenshot_url"])
            uri = os.path.join(base_url, newest_version["screenshot_url"])
            
            if not os.path.exists(destination_dir): os.mkdir(destination_dir)
            # name the target file as png
            local_filename = os.path.join(destination_dir, desklet_name+'.png')
            
            # print "fetch icon from", uri
            
            # download if the pic does not exist
            if not os.path.exists(local_filename):
                request = urllib2.Request(uri)
                request.add_header('User-Agent', 'Desklets Control/0.5 +http://www.gdesklets.org')
                stream = url_opener.open( request )
                
                fd = open(local_filename, 'w')
                fd.write( stream.read() )
                stream.close()
                fd.close()
                # print "  - fetched pic from %s ", uri
                
            else: pass # print "  - pic %s already cached" % local_filename
            
            desklet["preview"] = local_filename

        return list
