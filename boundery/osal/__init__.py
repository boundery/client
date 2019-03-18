import os, sys

if os.name == "posix":
    if sys.platform.startswith("darwin"):
        assert(False)
    else:
        from .osal_linux import *
else:
    #XXX Windows UAC (runas) doesn't hook up stdin/out. Named pipes?
    assert(False)
