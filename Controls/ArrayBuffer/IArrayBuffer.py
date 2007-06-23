#----------------------------------------------------------------------------------#
#
# FILE:                 __init__.py
# AUTHOR:               Peter Quinn
# DATE:                 20.02.2005
# VERSION:              1.30
#
# DESCRIPTION:  A object buffer that makes it easier to scroll and update arrays of
#                               objects.
#
# INTERFACE:   read           R     Read the window view array
#              read_all       R     Read the entire buffer array
#              delete         W     Deletes one line from the buffer
#              fill           W     Fills the buffer with an object
#              write          W     Write an array to the buffer
#              filltype       RW    Get / Set buffer fill type with an object
#              window_pos     RW    Get / Set viewable window position
#              window_size    RW    Get / Set viewable window size
#              size           RW    Get / Set buffer size
#              cursor         RW    Get / Set cursor position
#
#----------------------------------------------------------------------------------#

from libdesklets.controls import Interface, Permission

#----------------------------------------------------------------------------------#
#
# IArrayBuffer Interface
#
class IArrayBuffer(Interface):

    read        = Permission.READ
    read_all    = Permission.READ
    delete      = Permission.WRITE
    fill        = Permission.WRITE
    write       = Permission.WRITE
    filltype    = Permission.READWRITE
    window_pos  = Permission.READWRITE
    window_size = Permission.READWRITE
    size        = Permission.READWRITE
    cursor      = Permission.READWRITE

