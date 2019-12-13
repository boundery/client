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

    try:
        print("Testing get_mounts")
        mounts = get_mounts()
        #XXX Reenable this when we can make github actions fake a FAT drive.
        print("XXX", mounts)
        #if len(mounts) != 1 or mounts[0][0] != 'BNDRY TEST':
        #    logging.error("get_mounts failed: '%s'" % mounts)
        #    return 10

        #XXX https://superuser.com/questions/667607/check-if-current-command-prompt-was-launched-as-the-administrator
        print("Testing sudo")
        sudoproc = sudo('net session')
        #XXX Check return code?
        sudo_out = sudoproc.stdout.read()
        if not sudo_out.startswith('200 info '):
            logging.error("sudo failed: '%s' '%s'" % (sudo_out, sudoproc.stderr.read()))
            return 20

        print("Testing get_ssids")
        get_ssids()
        print("Testing complete")
    except Exception as e:
        logging.error("Exception: %s" % e, exc_info=True)
        return 99

#XXX Get wifi password. Pypi has "ng" which claims to do so.
