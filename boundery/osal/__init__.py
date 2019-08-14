import os, sys

if os.name == "posix":
    if sys.platform.startswith("darwin"):
        from .osal_macos import *
    else:
        from .osal_linux import *
else:
    from .osal_windows import *

def self_test():
    import logging
    if os.name == 'nt':
        zerotier = 'c:\Program Files (x86)\ZeroTier\One\zerotier-cli.bat'
    else:
        zerotier = 'zerotier-cli'

    try:
        print("Testing get_mounts")
        mounts = get_mounts()
        #if "BNDRY TEST" not in ','.join(mounts):
        if len(mounts) != 1: #XXX
            logging.error("get_mounts failed: '%s'" % mounts)
            return 10

        #XXX Just use --privsub directly here?
        print("Testing ZT info")
        zt = sudo(zerotier, 'info')
        zt_out = zt.stdout.read()
        if not zt_out.startswith('200 info '):
            logging.error("sudo failed: '%s'" % zt_out)
            return 20

        print("Testing get_ssids")
        get_ssids()
        print("Testing complete")
    except:
        logging.error("foo", exc_info=True)
        return 99

#XXX Get wifi password. Pypi has "ng" which claims to do so.
