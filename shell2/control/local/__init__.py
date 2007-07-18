''' Handles the local desklets and controls '''

import dircache
import os
from unpack import unpack            # untar the files
import file_operations   # remove, etc.
import core_interface_035 as core_interface

def get_desklets(directory):
    ''' Gets the local desklets from the given directory '''
    list = {}
    to_be_parsed = []
    dircache.reset()
    
    try:
        display_dir = dircache.listdir( directory )
    except OSError:
        # no desklet dir available
        return list
    
    for dir in display_dir:
        list.update( get_desklet_information(directory, dir) )

    return list



def get_desklet_information(directory, dir):
    
    list = {}
    to_be_parsed = [] # list of display files to parse
    
    desklet_contents = dircache.listdir( os.path.join(directory, dir) )
    # find all display files under the subdirectory
    for file in desklet_contents:
        if file[-8:] == ".display":
            to_be_parsed.append(file)
    
    # If there are multiple displays inside a directory, save
    # them all inside a "displays" dict under
    # the dirname
    if len(to_be_parsed) > 1:
        list[dir] = {}
        list[dir]["displays"] = {}
        max_version = 0 
        authors = []
        for display in to_be_parsed:
            full_path = directory+"/"+dir+"/"+display
            meta = parse_display_meta( full_path, dir )
            
            # find the largest version of all the displays and show that as the
            # version of the package
            max_version = max(max_version, meta["version"])
            list[dir]["displays"][ meta["name"] ] = meta
            try:
                # will fail here if the name is there already
                authors.index(meta['name'])
                authors.append(meta['name'])
            except: pass
            
        list[dir]["state"] = "installed"
        list[dir]["version"] = max_version
        list[dir]["name"] = dir
        list[dir]["preview"] = "" # make blank so that the available preview gets used
        list[dir]["description"] = ""
        list[dir]["category"] = "Multi-display"
        list[dir]["directory"] = dir
        list[dir]["author"] = authors
    
    elif len(to_be_parsed) == 1:
        full_path = directory+"/"+dir+"/"+to_be_parsed[0]
        meta = parse_display_meta( full_path )
        meta["directory"] = dir
        meta["displays"] = {meta["name"]: meta} # there is only one display in this package
        list[ meta["name"] ] = meta
    
    return list



def get_controls(directory):
    ''' Gets the local controls from the given directory '''
    list = {}

    dircache.reset()
    try: 
        control_dir = dircache.listdir( directory )
    except OSError:
        # no control dir available
        return list
    
    # pretty useless to have a dict where the name is under the name
    # perhaps in the future we'll have something like properties in
    # the dict...
    for dir in control_dir:
        list[dir] = {"name": dir, "directory": os.path.join(directory, dir)}

    return list



def parse_display_meta( target_file, package = "" ):
    ''' Opens the display file and parses it for meta information. Does
        not start the display. The "package" parameter gets saved inside
        multi-display-packages, so that the displays know where they belong '''
    f = open( target_file )
    read_meta_tag = False
    # first read the entire meta tag into a string
    while not read_meta_tag:
        line = f.readline()
        start_index = line.find( "<meta" )
        if line != "" and start_index != -1:
            found_end_tag = False
            meta_tag = line[start_index:]
            while not found_end_tag:
                line = f.readline()
                end_index = line.find( ">" )
                if line != "" and end_index != -1:
                    meta_tag += line[:end_index+1]
                    found_end_tag = True
                    read_meta_tag = True
                else:
                    meta_tag += line
        elif line == "":     # readline returned "" -> we reached the end of the file
            # print "No metatag found from ", target_file
            meta = {"name": os.path.basename(target_file), "author": "Unknown", "version" : "Unknown",
                "category": None, "description": "",
                "preview": None, "state": None, 
                "local_path": target_file, "package": package }
            return meta

    # then parse the attributes
    try:
        name_start = meta_tag.index( 'name=\"' ) + 6
        name_end = meta_tag.index( '"', name_start )
        name = unicode(meta_tag[ name_start:name_end ])
    except ValueError:
        name = "Desklet name unknown"

    try:
        author_start = meta_tag.index( 'author=\"' ) + 8
        author_end = meta_tag.index( '"', author_start   )
        author = unicode(meta_tag[ author_start:author_end ])
    except ValueError:
        author = "Unknown author"

    try:
        version_start = meta_tag.index( 'version=\"' ) + 9
        version_end = meta_tag.index( '"', version_start )
        version = unicode(meta_tag[ version_start:version_end ])
    except ValueError:
        version = ""

    try:
        category_start = meta_tag.index( 'category=\"' ) + 10
        category_end = meta_tag.index( '"', category_start )
        category = unicode(meta_tag[ category_start:category_end ])
    except ValueError:
        category = "Uncategorized"

    try:
        description_start = meta_tag.index( 'description=\"' ) + 13
        description_end = meta_tag.index( '"', description_start )
        description = unicode(meta_tag[ description_start:description_end ])
    except ValueError:
        description = "No description"

    try:
        preview_start = meta_tag.index( 'preview=\"' ) + 9
        preview_end = meta_tag.index( '"', preview_start )
        preview = unicode(meta_tag[ preview_start:preview_end ])
        display_path = os.path.dirname(target_file)
        preview = os.path.join(display_path, preview)
        
        # if there was no preview image available, then try to find one
        if not os.path.exists(preview):
            pass
            # print "  ! no preview image for", name, " @", preview
        
    except ValueError:
        preview = ""

    state = "installed"

    meta = {"name": name, "author": author, "version" :version,
            "category": category, "description": description,
            "preview": preview, "state": state, 
            "local_path": target_file, "package": package }

    return meta

