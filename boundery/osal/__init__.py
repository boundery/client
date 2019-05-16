import os, sys

if os.name == "posix":
    if sys.platform.startswith("darwin"):
        assert(False)
    else:
        from .osal_linux import *
else:
    from .osal_windows import *

#XXX Get wifi password. Pypi has "ng" which claims to do so.

#https://stackoverflow.com/questions/5747007/get-root-dialog-in-python-on-mac-os-x-windows/31984663#31984663
#/Library/Application Support/ZeroTier/One/authtoken.secret
