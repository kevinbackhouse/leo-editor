# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20190813161639.1: * @file pyzo_in_leo.py
#@@first
"""pyzo_in_leo.py: Experimental plugin that adds all of pyzo's features to Leo."""
#@+<< pyzo_in_leo imports >>
#@+node:ekr.20190813161639.2: **  << pyzo_in_leo imports >>
import leo.core.leoGlobals as g
from leo.core.leoQt import QtCore, QtWidgets
import locale
import sys
#
# Must patch sys.path here.
plugins_dir = g.os_path_finalize_join(g.app.loadDir, '..', 'plugins')
sys.path.insert(0, plugins_dir)
#
# Start pyzo, de-fanged.
sys.argv = sys.argv[:1]
    # Avoid problems when multiple copies of Leo are open.
import pyzo
#@-<< pyzo_in_leo imports >>
#@+others
#@+node:ekr.20190813161639.4: ** init
init_warning_given = False

def init(): # pyzo_in_leo.py
    '''Return True if this plugin can be loaded.'''
    
    def oops(message):
        global init_warning_given
        if not init_warning_given:
            init_warning_given = True
            print('%s %s' % (__name__, message))
        return False
        
    if g.app.gui.guiName() != "qt":
        return oops('requires Qt gui')
    # if not pyzo:
        # return oops('requires pyzo')
    if not g.app.dock:
        return oops('is incompatible with --no-dock')
    g.plugin_signon(__name__)
    g.registerHandler('after-create-leo-frame', onCreate)
    return True
#@+node:ekr.20190814050859.1: ** load_all_docks
def load_all_docks(c):

    trace = True
    if trace: print('\nSTART load_all_docks\n')
    table = (
        'PyzoFileBrowser',
        'PyzoHistoryViewer',
        'PyzoInteractiveHelp',
        'PyzoLogger',
        'PyzoSourceStructure',
        'PyzoWebBrowser',
        'PyzoWorkspace',
    )
    for tool_id in table:
        pyzo.toolManager.loadTool(tool_id)
            # Put a floatable dock on the right.
    if trace: print('\nEND load_all_docks\n')
#@+node:ekr.20190813161921.1: ** make_dock (not used)
def make_dock(c, name, widget): # pyzo_in_leo.py
    """Create a dock with the given name and widget in c's main window."""
    dw = c.frame.top
    dock = dw.createDockWidget(
        closeable=True,
        moveable=True, # Implies floatable.
        height=100,
        name=name,
    )
    dw.leo_docks.append(dock)
    dock.setWidget(widget)
    area = QtCore.Qt.LeftDockWidgetArea
    dw.addDockWidget(area, dock)
    widget.show()
#@+node:ekr.20190813161639.5: ** onCreate
def onCreate(tag, keys): # pyzo_in_leo.py
    '''Create pyzo docks in Leo's own main window'''
    c = keys.get('c')
    ### if not c and c.frame:
    ###    return
    if c and c.frame:
        pyzo_start(c)
#@+node:ekr.20190816131343.1: ** pyzo_start & helpers
def pyzo_start(c):
    """A copy of pyzo.start, adapted for Leo."""
    trace = True
    
    if trace: print('\nBEGIN start_pyzo_in_leo\n')

    # Do some imports
    from pyzo.core import pyzoLogging  # to start logging asap
        # EKK: All print statements after this will appear in the logging dock.
    assert pyzoLogging
    
    # EKR:change.
    # from pyzo.core.main import MainWindow

    # Apply users' preferences w.r.t. date representation etc
    for x in ('', 'C', 'en_US', 'en_US.utf8', 'en_US.UTF-8'):
        try:
            locale.setlocale(locale.LC_ALL, x)
            break
        except locale.Error:
            pass

    # Set to be aware of the systems native colors, fonts, etc.
    QtWidgets.QApplication.setDesktopSettingsAware(True)
    
    # EKR:change.
    # Instantiate the application.
        # QtWidgets.qApp = MyApp(sys.argv)
    my_app_ctor(c, sys.argv)

    # EKR:change.
        # # Choose language, get locale
        # appLocale = setLanguage(config.settings.language)
    # EKR:change.
    # Create main window, using the selected locale
        # MainWindow(None, appLocale)
    main_window_ctor(c)

    # EKR:change.
        # Enter the main loop
        # QtWidgets.qApp.exec_()

    if trace: print('END pyzo_start\n')
#@+node:ekr.20190816131753.1: *3* main_window_ctor
def main_window_ctor(c):
    """Simulate MainWindow.__init__()."""
    trace = True
    if trace: print('\nBEGIN main_window_ctor\n')
    
    # EKR:change-new imports
    import pyzo.core.main as main
    from pyzo.core import commandline
    
    # EKR:change
    self = c.frame.top
    # EKR:change.
        # QtWidgets.QMainWindow.__init__(self, parent)

    self._closeflag = 0  # Used during closing/restarting

    # EKR:change.
        # # Init window title and application icon
        # self.setMainTitle()
    # EKR:change.
    main.loadAppIcons()
        # loadAppIcons()
    # EKR:change.
        # self.setWindowIcon(pyzo.icon)
    # EKR:change.
        # Restore window geometry.
        # self.resize(800, 600) # default size
        # self.restoreGeometry()
    # EKR:change.
        # Show splash screen (we need to set our color too)
        # w = SplashWidget(self, distro='no distro')
    # EKR:change.
        # self.setCentralWidget(w)
    # EKR:change.
       #  self.setStyleSheet("QMainWindow { background-color: #268bd2;}")

    # Show empty window and disable updates for a while

    # EKR:change.
        # self.show()
        # self.paintNow()
        # self.setUpdatesEnabled(False)
    # EKR:change.
        # Determine timeout for showing splash screen
        # splash_timeout = time.time() + 1.0
    # EKR:change.
        # Set locale of main widget, so that qt strings are translated
        # in the right way
        # if locale:
            # self.setLocale(locale)
  
    # Store myself
    pyzo.main = self # Same as c.frame.top.
    
    # EKR:change-Add do-nothing methods.
    pyzo.main.setMainTitle = g.TracingNullObject(tag='pyzo.main.setMainTitle()')
    pyzo.main.restart = g.TracingNullObject(tag='pyzo.main.restart()')

    # Init dockwidget settings
    self.setTabPosition(QtCore.Qt.AllDockWidgetAreas,QtWidgets.QTabWidget.South)
    self.setDockOptions(
            QtWidgets.QMainWindow.AllowNestedDocks |
            QtWidgets.QMainWindow.AllowTabbedDocks
            #|  QtWidgets.QMainWindow.AnimatedDocks
        )

    # Set window atrributes
    self.setAttribute(QtCore.Qt.WA_AlwaysShowToolTips, True)

    # EKR:change.
    # Load icons and fonts
    main.loadIcons()
    main.loadFonts()
        # loadIcons()
        # loadFonts()

    # EKR:change.
        # # Set qt style and test success
        # self.setQtStyle(None) # None means init!
    # EKR:change.
        # # Hold the splash screen if needed
        # while time.time() < splash_timeout:
            # QtWidgets.qApp.flush()
            # QtWidgets.qApp.processEvents()
            # time.sleep(0.05)
    # EKR:change.
    # Populate the window (imports more code)
    main_window_populate(c)
        # self._populate()

    # EKR:change.
    # Revert to normal background, and enable updates
    self.setStyleSheet('')
    self.setUpdatesEnabled(True)

    # EKR:change. Could this be a problem?
        # # Restore window state, force updating, and restore again
        # self.restoreState()
        # self.paintNow()
        # self.restoreState()

    # EKR:change.
    # Present user with wizard if he/she is new.
        # if pyzo.config.state.newUser:
            # from pyzo.util.pyzowizard import PyzoWizard
            # w = PyzoWizard(self)
            # w.show() # Use show() instead of exec_() so the user can interact with pyzo

    # EKR:change
        # # Create new shell config if there is None
        # if not pyzo.config.shellConfigs2:
            # from pyzo.core.kernelbroker import KernelInfo
            # pyzo.config.shellConfigs2.append( KernelInfo() )
    from pyzo.core.kernelbroker import KernelInfo
    ### pyzo.config.shellConfigs2.append( KernelInfo() )
    pyzo.config.shellConfigs2 = [KernelInfo()]

    # EKR:change Set background.
        # bg = getattr(pyzo.config.settings, 'dark_background', '#657b83')
            # # Default: solarized base00
        # try:
            # self.setStyleSheet("background: %s" % bg) 
        # except Exception:
            # g.es_exception()

    # Focus on editor
    e = pyzo.editors.getCurrentEditor()
    if e is not None:
        e.setFocus()

    # Handle any actions
    commandline.handle_cmd_args()
    
    if trace: print('END main_window_ctor\n')
#@+node:ekr.20190816132847.1: *3* main_window_populate
def main_window_populate(c):
    """Simulate MainWindow_populate"""
    trace = True
    if trace: print('\nBEGIN main_window_populate\n')

    # EKR:change
    self = c.frame.top
    
    # EKR:change-new imports
    from pyzo.core.main import callLater

    # Delayed imports
    from pyzo.core.editorTabs import EditorTabs
    from pyzo.core.shellStack import ShellStackWidget
    from pyzo.core import codeparser
    from pyzo.core.history import CommandHistory
    from pyzo.tools import ToolManager

    # Instantiate tool manager
    pyzo.toolManager = ToolManager()

    # EKR: Disabled in original.
        # Check to install conda now ...
        # from pyzo.util.bootstrapconda import check_for_conda_env
        # check_for_conda_env()

    # Instantiate and start source-code parser
    if pyzo.parser is None:
        pyzo.parser = codeparser.Parser()
        pyzo.parser.start()

    # Create editor stack and make the central widget
    pyzo.editors = EditorTabs(self)
    
    # EKR:change: don't to this!
        # self.setCentralWidget(pyzo.editors)
            # EKR: QMainWindow.setCentralWidget

    # Create floater for shell
    self._shellDock = dock = QtWidgets.QDockWidget(self)
    
    # EKR:change.
    dock.setFeatures(dock.DockWidgetMovable | dock.DockWidgetFloatable)
        # if pyzo.config.settings.allowFloatingShell:
            # dock.setFeatures(dock.DockWidgetMovable | dock.DockWidgetFloatable)
        # else:
            # dock.setFeatures(dock.DockWidgetMovable)
    dock.setObjectName('shells')
    dock.setWindowTitle('Shells')
    self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)

    # Create shell stack
    pyzo.shells = ShellStackWidget(self)
    dock.setWidget(pyzo.shells)

    # Initialize command history
    pyzo.command_history = CommandHistory('command_history.py')

    # Create the default shell when returning to the event queue
    callLater(pyzo.shells.addShell)

    # EKR:change.
    pyzo.status = None
    # Create statusbar
        # if pyzo.config.view.showStatusbar:
            # pyzo.status = self.statusBar()
        # else:
            # pyzo.status = None
            # self.setStatusBar(None)

    # Create menu
    from pyzo.core import menu
    pyzo.keyMapper = menu.KeyMapper()
    menu.buildMenus(self.menuBar())
    
    # Add the context menu to the editor
    pyzo.editors.addContextMenu()
    pyzo.shells.addContextMenu()
    
    # EKR:change
    load_all_docks(c)
        # # Load tools
        # if pyzo.config.state.newUser and not pyzo.config.state.loadedTools:
            # pyzo.toolManager.loadTool('pyzosourcestructure')
            # pyzo.toolManager.loadTool('pyzofilebrowser', 'pyzosourcestructure')
        # elif pyzo.config.state.loadedTools:
            # for toolId in pyzo.config.state.loadedTools:
                # pyzo.toolManager.loadTool(toolId)
            
    if trace: print('END main_window_populate\n')
#@+node:ekr.20190816131934.1: *3* pyzo_MyApp
def my_app_ctor(c, argv):
    """Simulate MyApp.__init__()."""
    pass
    
    # The MyApp class only defines this:
    
    # def event(self, event):
        # if isinstance(event, QtGui.QFileOpenEvent):
            # fname = str(event.file())
            # if fname and fname != 'pyzo':
                # sys.argv[1:] = []
                # sys.argv.append(fname)
                # res = commandline.handle_cmd_args()
                # if not commandline.is_our_server_running():
                    # print(res)
                    # sys.exit()
        # return QtWidgets.QApplication.event(self, event)
    
#@-others
#@@language python
#@@tabwidth -4
#@-leo
