import os, sys

if os.name == "posix":
    if sys.platform.startswith("darwin"):
        from .osal_macos import *
        sudo_test = ['cat', '/etc/sudoers']
        sudo_expected = '#'
    else:
        from .osal_linux import *
        sudo_test = ['cat', '/etc/gshadow']
        sudo_expected = 'root:'
else:
    from .osal_windows import *
    sudo_test = ['net', 'session']
    sudo_expected = 'There are no entries in the list.'

def self_test():
    import logging

    try:
        print("Testing get_mounts")
        mounts = get_mounts()
        if len(mounts) != 1 or mounts[0][0] != 'BNDRY TEST':
            logging.error("get_mounts failed: '%s'" % mounts)
            return 10

        print("Testing sudo")
        sudoproc = sudo(*sudo_test)
        sudo_out = sudoproc.stdout.read()
        if not sudo_out.startswith(sudo_expected):
            logging.error("sudo failed: '%s' '%s'" % (sudo_out, sudoproc.stderr.read()))
            return 20

        print("Testing get_ssids")
        get_ssids()
        print("Testing complete")
    except Exception as e:
        logging.error("Exception: %s" % e, exc_info=True)
        return 99

#XXX Get wifi password. Pypi has "ng" which claims to do so.
