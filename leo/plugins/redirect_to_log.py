#@+leo-ver=5-thin
#@+node:edream.110203113231.924: * @file ../plugins/redirect_to_log.py
"""Sends all output to the log pane."""

#@@language python
#@@tabwidth -4

from leo.core import leoGlobals as g

def init():
    """Return True if the plugin has loaded successfully."""
    ok = not g.unitTesting  # Not for unit tests.
    if ok: # Register the handlers...
        g.registerHandler("start2", onStart)
        g.plugin_signon(__name__)
    return ok

def onStart (tag,keywords):
    g.redirectStdout() # Redirect stdout
    g.redirectStderr() # Redirect stderr
#@-leo
