from libdesklets.controls import Interface, Permission

class ISystem(Interface):

    allfs            = Permission.READWRITE
    iface            = Permission.READWRITE
    mountdir         = Permission.READWRITE
    pid              = Permission.READWRITE
    which            = Permission.READWRITE

    cpu              = Permission.READ
    cpu_bogomips     = Permission.READ
    cpu_cache        = Permission.READ
    cpu_clock        = Permission.READ
    cpu_load         = Permission.READ
    cpu_model        = Permission.READ

    fsusage          = Permission.READ
    
    hostname         = Permission.READ    
    kernel_version   = Permission.READ
    loadavg          = Permission.READ
    memory           = Permission.READ
    mountlist        = Permission.READ
    net_devices      = Permission.READ
    net_load         = Permission.READ
    net_speed        = Permission.READ
    net_state        = Permission.READ

    operating_system = Permission.READ
    ppp              = Permission.READ
    proc_args        = Permission.READ
    proc_kernel      = Permission.READ
    proc_list        = Permission.READ
    proc_map         = Permission.READ
    proc_mem         = Permission.READ
    proc_segment     = Permission.READ
    proc_signal      = Permission.READ
    proc_state       = Permission.READ
    proc_time        = Permission.READ
    proc_uid         = Permission.READ
    swap             = Permission.READ
    uptime           = Permission.READ
    users            = Permission.READ

