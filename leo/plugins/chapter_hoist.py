#@+leo-ver=5-thin
#@+node:ekr.20060328125925: * @file ../plugins/chapter_hoist.py
#@+<< docstring >>
#@+node:ekr.20060328125925.1: ** << docstring >>
""" Creates hoist buttons.

This plugin puts two buttons in the icon area: a button called 'Save Hoist' and
a button called 'Dehoist'. The 'Save Hoist' button hoists the presently selected
node and creates a button which can later rehoist the same node. The 'Dehoist'
button performs one level of dehoisting

Requires at least version 0.19 of mod_scripting.

"""
#@-<< docstring >>

# By btheado. Edited by EKR.

from leo.core import leoGlobals as g
from leo.plugins.mod_scripting import scriptingController

#@+others
#@+node:ekr.20060328125925.4: ** init
def init ():
    """Return True if the plugin has loaded successfully."""
    # Note: call onCreate _after_ reading the .leo file.
    # That is, the 'after-create-leo-frame' hook is too early!
    g.registerHandler(('new','open2'),onCreate)
    g.plugin_signon(__name__)
    return True
#@+node:ekr.20060328125925.5: ** onCreate
def onCreate (tag, keys):
    """Handle the onCreate event in the chapterHoist plugin."""
    c = keys.get('c')
    if c:
        sc = scriptingController(c)
        chapterHoist(sc,c)
#@+node:ekr.20060328125925.6: ** class chapterHoist
class chapterHoist:
    #@+others
    #@+node:ekr.20060328125925.7: *3*  ctor
    def __init__ (self,sc,c):
        self.createSaveHoistButton(sc,c)
        self.createDehoistButton(sc,c)
    #@+node:ekr.20060328125925.8: *3* createSaveHoistButton
    def createSaveHoistButton(self,sc,c):

        def saveHoistCallback(event=None,self=self,sc=sc,c=c):
            self.createChapterHoistButton(sc,c,c.p)
            c.hoist()

        b = sc.createIconButton(
            args=None,
            text='save-hoist',
            command = saveHoistCallback,
            statusLine='Create hoist button current node')

        return b
    #@+node:ekr.20060328125925.9: *3* createDehoistButton
    def createDehoistButton(self,sc,c):

        def dehoistCallback(event=None,c=c):
            c.dehoist()
            return 'break'

        # Fix #426 with a kludge that satisfies k.registerCommand.
        dehoistCallback.__name__ = 'wrapper: dehoist'

        b = sc.createIconButton(
            args=None,
            text='dehoist',
            command=dehoistCallback,
            statusLine='Dehoist')

        return b
    #@+node:ekr.20060328125925.10: *3* createChapterHoistButton
    def createChapterHoistButton (self,sc,c,p):

        """Generates a hoist button for the headline at the given position"""
        h = p.h
        buttonText = sc.getButtonText(h)
        statusLine = "Hoist %s" % h

        def hoistButtonCallback (event=None,self=self,c=c,p=p.copy()):
            while c.canDehoist():
                c.dehoist()
            c.selectPosition(p)
            c.hoist()
            return 'break'

        sc.createIconButton(
            args=None,
            text=buttonText,
            command=hoistButtonCallback,
            statusLine=statusLine)
    #@-others
#@-others
#@-leo
