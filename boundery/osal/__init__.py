import os, sys

if os.name == "posix":
    if sys.platform.startswith("darwin"):
        assert(False)
    else:
        from .osal_linux import *
else:
    #XXX Windows UAC (runas) doesn't hook up stdin/out. Named pipes?
    assert(False)

#netsh wlan show networks mode=bssid
#https://stackoverflow.com/questions/130763/request-uac-elevation-from-within-a-python-script

#https://stackoverflow.com/questions/5747007/get-root-dialog-in-python-on-mac-os-x-windows/31984663#31984663
