import os, sys

if os.name == "posix":
    if sys.platform.startswith("darwin"):
        from .osal_macos import *
    else:
        from .osal_linux import *
else:
    from .osal_windows import *

#XXX Get wifi password. Pypi has "ng" which claims to do so.
