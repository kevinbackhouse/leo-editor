#@+leo-ver=5-thin
#@+node:ekr.20140907085654.18699: * @file ../plugins/qt_gui.py
"""This file contains the gui wrapper for Qt: g.app.gui."""
# pylint: disable=import-error
#@+<< imports >>
#@+node:ekr.20140918102920.17891: ** << imports >> (qt_gui.py)
import datetime
import functools
import re
import sys
import textwrap
from typing import Dict, List

from leo.core import leoColor
from leo.core import leoGlobals as g
from leo.core import leoGui
from leo.core.leoQt import isQt5, isQt6, Qsci, QtConst, QtCore, QtGui, QtWidgets
from leo.core.leoQt import ButtonRole, DialogCode, Icon, Information, Policy
from leo.core.leoQt import Shadow, Shape, StandardButton, Weight, WindowType
    # This import causes pylint to fail on this file and on leoBridge.py.
    # The failure is in astroid: raw_building.py.
from leo.plugins import qt_events
from leo.plugins import qt_frame
from leo.plugins import qt_idle_time
from leo.plugins import qt_text
# This defines the commands defined by @g.command.
from leo.plugins import qt_commands
assert qt_commands
#@-<< imports >>
#@+others
#@+node:ekr.20110605121601.18134: ** init (qt_gui.py)
def init():

    if g.unitTesting:  # Not Ok for unit testing!
        return False
    if not QtCore:
        return False
    if g.app.gui:
        return g.app.gui.guiName() == 'qt'
    g.app.gui = LeoQtGui()
    g.app.gui.finishCreate()
    g.plugin_signon(__name__)
    return True
#@+node:ekr.20140907085654.18700: ** class LeoQtGui(leoGui.LeoGui)
class LeoQtGui(leoGui.LeoGui):
    """A class implementing Leo's Qt gui."""
    #@+others
    #@+node:ekr.20110605121601.18477: *3*  qt_gui.__init__ (sets qtApp)
    def __init__(self):
        """Ctor for LeoQtGui class."""
        super().__init__('qt')
             # Initialize the base class.
        self.active = True
        self.consoleOnly = False  # Console is separate from the log.
        self.iconimages = {}
        self.globalFindDialog = None
        self.idleTimeClass = qt_idle_time.IdleTime
        self.insert_char_flag = False  # A flag for eventFilter.
        self.mGuiName = 'qt'
        self.main_window = None
            # The *singleton* QMainWindow.
        self.plainTextWidget = qt_text.PlainTextWrapper
        self.styleSheetManagerClass = StyleSheetManager
            # For c.idle_focus_helper and activate/deactivate events.
        #
        # Set to be aware of the systems native colors, fonts, etc.
        QtWidgets.QApplication.setDesktopSettingsAware(True)
        # Create objects...
        self.qtApp = QtWidgets.QApplication(sys.argv)
        self.reloadSettings()
        self.appIcon = self.getIconImage('leoapp32.png')
        #
        # Define various classes key stokes.
        #@+<< define FKeys >>
        #@+node:ekr.20180419110303.1: *4* << define FKeys >>
        self.FKeys = [
            'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12']
            # These do not generate keystrokes on MacOs.
        #@-<< define FKeys >>
        #@+<< define ignoreChars >>
        #@+node:ekr.20180419105250.1: *4* << define ignoreChars >>
        # Always ignore these characters
        self.ignoreChars = [
            # These are in ks.special characters.
            # They should *not* be ignored.
                # 'Left', 'Right', 'Up', 'Down',
                # 'Next', 'Prior',
                # 'Home', 'End',
                # 'Delete', 'Escape',
                # 'BackSpace', 'Linefeed', 'Return', 'Tab',
            # F-Keys are also ok.
                # 'F1','F2','F3','F4','F5','F6','F7','F8','F9','F10','F11','F12',
            'KP_0', 'KP_1', 'KP_2', 'KP_3', 'KP_4', 'KP_5', 'KP_6', 'KP_7', 'KP_8', 'KP_9',
            'KP_Multiply, KP_Separator,KP_Space, KP_Subtract, KP_Tab',
            'KP_F1', 'KP_F2', 'KP_F3', 'KP_F4',
            'KP_Add', 'KP_Decimal', 'KP_Divide', 'KP_Enter', 'KP_Equal',
                # Keypad chars should be have been converted to other keys.
                # Users should just bind to the corresponding normal keys.
            'CapsLock', 'Caps_Lock',
            'NumLock', 'Num_Lock',
            'ScrollLock',
            'Alt_L', 'Alt_R',
            'Control_L', 'Control_R',
            'Meta_L', 'Meta_R',
            'Shift_L', 'Shift_R',
            'Win_L', 'Win_R',
                # Clearly, these should never be generated.
            'Break', 'Pause', 'Sys_Req',
                # These are real keys, but they don't mean anything.
            'Begin', 'Clear',
                # Don't know what these are.
        ]
        #@-<< define ignoreChars >>
        #@+<< define specialChars >>
        #@+node:ekr.20180419081404.1: *4* << define specialChars >>
        # Keys whose names must never be inserted into text.
        self.specialChars = [
            # These are *not* special keys.
                # 'BackSpace', 'Linefeed', 'Return', 'Tab',
            'Left', 'Right', 'Up', 'Down',
                # Arrow keys
            'Next', 'Prior',
                # Page up/down keys.
            'Home', 'End',
                # Home end keys.
            'Delete', 'Escape',
                # Others.
            'Enter', 'Insert', 'Ins',
                # These should only work if bound.
            'Menu',
                # #901.
            'PgUp', 'PgDn',
                # #868.
        ]
        #@-<< define specialChars >>
        # Put up the splash screen()
        if (g.app.use_splash_screen and
            not g.app.batchMode and
            not g.app.silentMode and
            not g.unitTesting
        ):
            self.splashScreen = self.createSplashScreen()
        self.frameFactory = qt_frame.TabbedFrameFactory()
            # qtFrame.finishCreate does all the other work.

    def reloadSettings(self):
        pass
    #@+node:ekr.20110605121601.18484: *3*  qt_gui.destroySelf (calls qtApp.quit)
    def destroySelf(self):

        QtCore.pyqtRemoveInputHook()
        if 'shutdown' in g.app.debug:
            g.pr('LeoQtGui.destroySelf: calling qtApp.Quit')
        self.qtApp.quit()
    #@+node:ekr.20110605121601.18485: *3* qt_gui.Clipboard
    #@+node:ekr.20160917125946.1: *4* qt_gui.replaceClipboardWith
    def replaceClipboardWith(self, s):
        """Replace the clipboard with the string s."""
        cb = self.qtApp.clipboard()
        if cb:
            # cb.clear()  # unnecessary, breaks on some Qt versions
            s = g.toUnicode(s)
            QtWidgets.QApplication.processEvents()
            # Fix #241: QMimeData object error
            cb.setText(s)
            QtWidgets.QApplication.processEvents()
        else:
            g.trace('no clipboard!')
    #@+node:ekr.20160917125948.1: *4* qt_gui.getTextFromClipboard
    def getTextFromClipboard(self):
        """Get a unicode string from the clipboard."""
        cb = self.qtApp.clipboard()
        if cb:
            QtWidgets.QApplication.processEvents()
            return cb.text()
        g.trace('no clipboard!')
        return ''
    #@+node:ekr.20160917130023.1: *4* qt_gui.setClipboardSelection
    def setClipboardSelection(self, s):
        """
        Set the clipboard selection to s.
        There are problems with PyQt5.
        """
        if isQt5 or isQt6:
            # Alas, returning s reopens #218.
            return
        if s:
            # This code generates a harmless, but annoying warning on PyQt5.
            cb = self.qtApp.clipboard()
            cb.setText(s, mode=cb.Selection)
    #@+node:ekr.20110605121601.18487: *3* qt_gui.Dialogs & panels
    #@+node:ekr.20110605121601.18488: *4* qt_gui.alert
    def alert(self, c, message):
        if g.unitTesting:
            return
        dialog = QtWidgets.QMessageBox(None)
        dialog.setWindowTitle('Alert')
        dialog.setText(message)
        dialog.setIcon(Icon.Warning)
        dialog.addButton('Ok', ButtonRole.YesRole)
        try:
            c.in_qt_dialog = True
            dialog.raise_()
            dialog.exec_()
        finally:
            c.in_qt_dialog = False
    #@+node:ekr.20110605121601.18489: *4* qt_gui.makeFilter
    def makeFilter(self, filetypes):
        """Return the Qt-style dialog filter from filetypes list."""
        filters = ['%s (%s)' % (z) for z in filetypes]
            # Careful: the second %s is *not* replaced.
        return ';;'.join(filters)
    #@+node:ekr.20150615211522.1: *4* qt_gui.openFindDialog & helpers
    def openFindDialog(self, c):
        if g.unitTesting:
            return
        dialog = self.globalFindDialog
        if not dialog:
            dialog = self.createFindDialog(c)
            self.globalFindDialog = dialog
            # Fix #516: Do the following only once...
            if c:
                dialog.setStyleSheet(c.active_stylesheet)
                # Set the commander's FindTabManager.
                assert g.app.globalFindTabManager
                c.ftm = g.app.globalFindTabManager
                fn = c.shortFileName() or 'Untitled'
            else:
                fn = 'Untitled'
            dialog.setWindowTitle(f"Find in {fn}")
        if c:
            c.inCommand = False
        if dialog.isVisible():
            # The order is important, and tricky.
            dialog.focusWidget()
            dialog.show()
            dialog.raise_()
            dialog.activateWindow()
        else:
            dialog.show()
            dialog.exec_()
    #@+node:ekr.20150619053138.1: *5* qt_gui.createFindDialog
    def createFindDialog(self, c):
        """Create and init a non-modal Find dialog."""
        if c:
            g.app.globalFindTabManager = c.findCommands.ftm
        top = c and c.frame.top  # top is the DynamicWindow class.
        w = top.findTab
        dialog = QtWidgets.QDialog()
        # Fix #516: Hide the dialog. Never delete it.

        def closeEvent(event):
            event.ignore()
            dialog.hide()

        dialog.closeEvent = closeEvent
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.addWidget(w)
        self.attachLeoIcon(dialog)
        dialog.setLayout(layout)
        if c:
            c.styleSheetManager.set_style_sheets(w=dialog)
            g.app.gui.setFilter(c, dialog, dialog, 'find-dialog')
            # This makes most standard bindings available.
        dialog.setModal(False)
        return dialog
    #@+node:ekr.20110605121601.18492: *4* qt_gui.panels
    def createComparePanel(self, c):
        """Create a qt color picker panel."""
        return None  # This window is optional.

    def createFindTab(self, c, parentFrame):
        """Create a qt find tab in the indicated frame."""
        pass  # Now done in dw.createFindTab.

    def createLeoFrame(self, c, title):
        """Create a new Leo frame."""
        return qt_frame.LeoQtFrame(c, title, gui=self)

    def createSpellTab(self, c, spellHandler, tabName):
        if g.unitTesting:
            return None
        return qt_frame.LeoQtSpellTab(c, spellHandler, tabName)
    #@+node:ekr.20110605121601.18493: *4* qt_gui.runAboutLeoDialog
    def runAboutLeoDialog(self, c, version, theCopyright, url, email):
        """Create and run a qt About Leo dialog."""
        if g.unitTesting:
            return
        dialog = QtWidgets.QMessageBox(c and c.frame.top)
        dialog.setText(f"{version}\n{theCopyright}\n{url}\n{email}")
        dialog.setIcon(Icon.Information)
        yes = dialog.addButton('Ok', ButtonRole.YesRole)
        dialog.setDefaultButton(yes)
        try:
            c.in_qt_dialog = True
            dialog.raise_()
            dialog.exec_()
        finally:
            c.in_qt_dialog = False
    #@+node:ekr.20110605121601.18496: *4* qt_gui.runAskDateTimeDialog
    def runAskDateTimeDialog(self, c, title,
        message='Select Date/Time',
        init=None,
        step_min=None
    ):
        """Create and run a qt date/time selection dialog.

        init - a datetime, default now
        step_min - a dict, keys are QtWidgets.QDateTimeEdit Sections, like
          QtWidgets.QDateTimeEdit.MinuteSection, and values are integers,
          the minimum amount that section of the date/time changes
          when you roll the mouse wheel.

        E.g. (5 minute increments in minute field):

            g.app.gui.runAskDateTimeDialog(c, 'When?',
                message="When is it?",
                step_min={QtWidgets.QDateTimeEdit.MinuteSection: 5})

        """
        #@+<< define date/time classes >>
        #@+node:ekr.20211005103909.1: *5* << define date/time classes >>


        class DateTimeEditStepped(QtWidgets.QDateTimeEdit):
            """QDateTimeEdit which allows you to set minimum steps on fields, e.g.
              DateTimeEditStepped(parent, {QtWidgets.QDateTimeEdit.MinuteSection: 5})
            for a minimum 5 minute increment on the minute field.
            """

            def __init__(self, parent=None, init=None, step_min=None):
                if step_min is None:
                    step_min = {}
                self.step_min = step_min
                if init:
                    super().__init__(init, parent)
                else:
                    super().__init__(parent)

            def stepBy(self, step):
                cs = self.currentSection()
                if cs in self.step_min and abs(step) < self.step_min[cs]:
                    step = self.step_min[cs] if step > 0 else -self.step_min[cs]
                QtWidgets.QDateTimeEdit.stepBy(self, step)


        class Calendar(QtWidgets.QDialog):

            def __init__(self,
                parent=None,
                message='Select Date/Time',
                init=None,
                step_min=None
            ):
                if step_min is None:
                    step_min = {}
                super().__init__(parent)
                layout = QtWidgets.QVBoxLayout()
                self.setLayout(layout)
                layout.addWidget(QtWidgets.QLabel(message))
                self.dt = DateTimeEditStepped(init=init, step_min=step_min)
                self.dt.setCalendarPopup(True)
                layout.addWidget(self.dt)
                buttonBox = QtWidgets.QDialogButtonBox(StandardButton.Ok | StandardButton.Cancel)
                layout.addWidget(buttonBox)
                buttonBox.accepted.connect(self.accept)
                buttonBox.rejected.connect(self.reject)

        #@-<< define date/time classes >>
        if g.unitTesting:
            return None
        if step_min is None:
            step_min = {}
        if not init:
            init = datetime.datetime.now()
        dialog = Calendar(c and c.frame.top, message=message, init=init, step_min=step_min)
        if c:
            dialog.setStyleSheet(c.active_stylesheet)
            dialog.setWindowTitle(title)
            try:
                c.in_qt_dialog = True
                dialog.raise_()
                val = dialog.exec() if isQt6 else dialog.exec_()
            finally:
                c.in_qt_dialog = False
        else:
            dialog.setWindowTitle(title)
            dialog.raise_()
            val = dialog.exec() if isQt6 else dialog.exec_()
        if val == DialogCode.Accepted:
            return dialog.dt.dateTime().toPyDateTime()
        return None
    #@+node:ekr.20110605121601.18494: *4* qt_gui.runAskLeoIDDialog (not used)
    def runAskLeoIDDialog(self):
        """Create and run a dialog to get g.app.LeoID."""
        if g.unitTesting:
            return None
        message = (
            "leoID.txt not found\n\n" +
            "Please enter an id that identifies you uniquely.\n" +
            "Your cvs/bzr login name is a good choice.\n\n" +
            "Leo uses this id to uniquely identify nodes.\n\n" +
            "Your id must contain only letters and numbers\n" +
            "and must be at least 3 characters in length.")
        parent = None
        title = 'Enter Leo id'
        s, ok = QtWidgets.QInputDialog.getText(parent, title, message)
        return s
    #@+node:ekr.20110605121601.18491: *4* qt_gui.runAskOkCancelNumberDialog
    def runAskOkCancelNumberDialog(
        self, c, title, message, cancelButtonText=None, okButtonText=None):
        """Create and run askOkCancelNumber dialog ."""
        if g.unitTesting:
            return None
        # n,ok = QtWidgets.QInputDialog.getDouble(None,title,message)
        dialog = QtWidgets.QInputDialog()
        if c:
            dialog.setStyleSheet(c.active_stylesheet)
        dialog.setWindowTitle(title)
        dialog.setLabelText(message)
        if cancelButtonText:
            dialog.setCancelButtonText(cancelButtonText)
        if okButtonText:
            dialog.setOkButtonText(okButtonText)
        self.attachLeoIcon(dialog)
        dialog.raise_()
        ok = dialog.exec_()
        n = dialog.textValue()
        try:
            n = float(n)
        except ValueError:
            n = None
        return n if ok else None
    #@+node:ekr.20110605121601.18490: *4* qt_gui.runAskOkCancelStringDialog
    def runAskOkCancelStringDialog(self, c, title, message, cancelButtonText=None,
                                   okButtonText=None, default="", wide=False):
        """Create and run askOkCancelString dialog.

        wide - edit a long string
        """
        if g.unitTesting:
            return None
        dialog = QtWidgets.QInputDialog()
        if c:
            dialog.setStyleSheet(c.active_stylesheet)
        dialog.setWindowTitle(title)
        dialog.setLabelText(message)
        dialog.setTextValue(default)
        if wide:
            dialog.resize(int(g.windows()[0].get_window_info()[0] * .9), 100)
        if cancelButtonText:
            dialog.setCancelButtonText(cancelButtonText)
        if okButtonText:
            dialog.setOkButtonText(okButtonText)
        self.attachLeoIcon(dialog)
        dialog.raise_()
        ok = dialog.exec_()
        return str(dialog.textValue()) if ok else None
    #@+node:ekr.20110605121601.18495: *4* qt_gui.runAskOkDialog
    def runAskOkDialog(self, c, title, message=None, text="Ok"):
        """Create and run a qt askOK dialog ."""
        if g.unitTesting:
            return
        dialog = QtWidgets.QMessageBox(c and c.frame.top)
        stylesheet = getattr(c, 'active_stylesheet', None)
        if stylesheet:
            dialog.setStyleSheet(stylesheet)
        dialog.setWindowTitle(title)
        if message:
            dialog.setText(message)
        dialog.setIcon(Information.Information)
        dialog.addButton(text, ButtonRole.YesRole)
        try:
            c.in_qt_dialog = True
            dialog.raise_()
            dialog.exec_()
        finally:
            c.in_qt_dialog = False

    #@+node:ekr.20110605121601.18497: *4* qt_gui.runAskYesNoCancelDialog
    def runAskYesNoCancelDialog(self, c, title,
        message=None,
        yesMessage="&Yes",
        noMessage="&No",
        yesToAllMessage=None,
        defaultButton="Yes",
        cancelMessage=None,
    ):
        """
        Create and run an askYesNo dialog.

        Return one of ('yes', 'no', 'cancel', 'yes-to-all').

        """
        if g.unitTesting:
            return None
        dialog = QtWidgets.QMessageBox(c and c.frame.top)
        stylesheet = getattr(c, 'active_stylesheet', None)
        if stylesheet:
            dialog.setStyleSheet(stylesheet)
        if message:
            dialog.setText(message)
        dialog.setIcon(Information.Warning)
        dialog.setWindowTitle(title)
        # Creation order determines returned value.
        yes = dialog.addButton(yesMessage, ButtonRole.YesRole)
        no = dialog.addButton(noMessage, ButtonRole.NoRole)
        cancel = dialog.addButton(cancelMessage or 'Cancel', ButtonRole.RejectRole)
        if yesToAllMessage:
            dialog.addButton(yesToAllMessage, ButtonRole.YesRole)
        if defaultButton == "Yes":
            dialog.setDefaultButton(yes)
        elif defaultButton == "No":
            dialog.setDefaultButton(no)
        else:
            dialog.setDefaultButton(cancel)
        try:
            c.in_qt_dialog = True
            dialog.raise_()  # #2246.
            val = dialog.exec() if isQt6 else dialog.exec_()
        finally:
            c.in_qt_dialog = False
        # val is the same as the creation order.
        # Tested with both Qt6 and Qt5.
        return {
            0: 'yes', 1: 'no', 2: 'cancel', 3: 'yes-to-all',
        }.get(val, 'cancel')
    #@+node:ekr.20110605121601.18498: *4* qt_gui.runAskYesNoDialog
    def runAskYesNoDialog(self, c, title, message=None, yes_all=False, no_all=False):
        """
        Create and run an askYesNo dialog.
        Return one of ('yes','yes-all','no','no-all')

        :Parameters:
        - `c`: commander
        - `title`: dialog title
        - `message`: dialog message
        - `yes_all`: bool - show YesToAll button
        - `no_all`: bool - show NoToAll button
        """
        if g.unitTesting:
            return None
        dialog = QtWidgets.QMessageBox(c and c.frame.top)
        # Creation order determines returned value.
        yes = dialog.addButton('Yes', ButtonRole.YesRole)
        dialog.addButton('No', ButtonRole.NoRole)
        # dialog.addButton('Cancel', ButtonRole.RejectRole)
        if yes_all:
            dialog.addButton('Yes To All', ButtonRole.YesRole)
        if no_all:
            dialog.addButton('No To All', ButtonRole.NoRole)
        if c:
            dialog.setStyleSheet(c.active_stylesheet)
        dialog.setWindowTitle(title)
        if message:
            dialog.setText(message)
        dialog.setIcon(Information.Warning)
        dialog.setDefaultButton(yes)
        if c:
            try:
                c.in_qt_dialog = True
                dialog.raise_()
                val = dialog.exec() if isQt6 else dialog.exec_()
            finally:
                c.in_qt_dialog = False
        else:
            dialog.raise_()
            val = dialog.exec() if isQt6 else dialog.exec_()
        # val is the same as the creation order.
        # Tested with both Qt6 and Qt5.
        return {
            # Buglet: This assumes both yes-all and no-all buttons are active.
            0: 'yes', 1: 'no', 2: 'cancel', 3: 'yes-all', 4: 'no-all',
        }.get(val, 'cancel')
    #@+node:ekr.20110605121601.18499: *4* qt_gui.runOpenDirectoryDialog
    def runOpenDirectoryDialog(self, title, startdir):
        """Create and run an Qt open directory dialog ."""
        if g.unitTesting:
            return None
        dialog = QtWidgets.QFileDialog()
        self.attachLeoIcon(dialog)
        return dialog.getExistingDirectory(None, title, startdir)
    #@+node:ekr.20110605121601.18500: *4* qt_gui.runOpenFileDialog
    def runOpenFileDialog(self, c,
        title,
        filetypes,
        defaultextension='',
        multiple=False,
        startpath=None,
    ):
        """
        Create and run an Qt open file dialog.
        """
        # pylint: disable=arguments-differ
        if g.unitTesting:
            return ''
        #
        # 2018/03/14: Bug fixes:
        # - Use init_dialog_folder only if a path is not given
        # - *Never* Use os.curdir by default!
        if not startpath:
            startpath = g.init_dialog_folder(c, c and c.p, use_at_path=True)
                # Returns c.last_dir or os.curdir
        filter_ = self.makeFilter(filetypes)
        dialog = QtWidgets.QFileDialog()
        if c:
            dialog.setStyleSheet(c.active_stylesheet)
        self.attachLeoIcon(dialog)
        func = dialog.getOpenFileNames if multiple else dialog.getOpenFileName
        if c:
            try:
                c.in_qt_dialog = True
                val = func(parent=None, caption=title, directory=startpath, filter=filter_)
            finally:
                c.in_qt_dialog = False
        else:
            val = func(parent=None, caption=title, directory=startpath, filter=filter_)
        if isQt5 or isQt6:  # this is a *Py*Qt change rather than a Qt change
            val, junk_selected_filter = val
        if multiple:
            files = [g.os_path_normslashes(s) for s in val]
            if c and files:
                c.last_dir = g.os_path_dirname(files[-1])
            return files
        s = g.os_path_normslashes(val)
        if c and s:
            c.last_dir = g.os_path_dirname(s)
        return s
    #@+node:ekr.20110605121601.18501: *4* qt_gui.runPropertiesDialog
    def runPropertiesDialog(self,
        title='Properties',
        data=None,
        callback=None,
        buttons=None
    ):
        """Dispay a modal TkPropertiesDialog"""
        if not g.unitTesting:
            g.warning('Properties menu not supported for Qt gui')
        return 'Cancel', {}
    #@+node:ekr.20110605121601.18502: *4* qt_gui.runSaveFileDialog
    def runSaveFileDialog(
        self, c, initialfile='', title='Save', filetypes=None, defaultextension=''):
        """Create and run an Qt save file dialog ."""
        if g.unitTesting:
            return ''
        dialog = QtWidgets.QFileDialog()
        if c:
            dialog.setStyleSheet(c.active_stylesheet)
            self.attachLeoIcon(dialog)
            try:
                c.in_qt_dialog = True
                obj = dialog.getSaveFileName(
                    None,  # parent
                    title,
                    # os.curdir,
                    g.init_dialog_folder(c, c.p, use_at_path=True),
                    self.makeFilter(filetypes or []),
                )
            finally:
                c.in_qt_dialog = False
        else:
            self.attachLeoIcon(dialog)
            obj = dialog.getSaveFileName(
                None,  # parent
                title,
                # os.curdir,
                g.init_dialog_folder(None, None, use_at_path=True),
                self.makeFilter(filetypes or []),
            )
        # Bizarre: PyQt5 version can return a tuple!
        s = obj[0] if isinstance(obj, (list, tuple)) else obj
        s = s or ''
        if c and s:
            c.last_dir = g.os_path_dirname(s)
        return s
    #@+node:ekr.20110605121601.18503: *4* qt_gui.runScrolledMessageDialog
    def runScrolledMessageDialog(self,
        short_title='',
        title='Message',
        label='',
        msg='',
        c=None, **keys
    ):
        if g.unitTesting:
            return None

        def send():
            return g.doHook('scrolledMessage',
                short_title=short_title, title=title,
                label=label, msg=msg, c=c, **keys)

        if not c or not c.exists:
            #@+<< no c error>>
            #@+node:ekr.20110605121601.18504: *5* << no c error>>
            g.es_print_error('%s\n%s\n\t%s' % (
                "The qt plugin requires calls to g.app.gui.scrolledMessageDialog to include 'c'",
                "as a keyword argument",
                g.callers()
            ))
            #@-<< no c error>>
        else:
            retval = send()
            if retval:
                return retval
            #@+<< load viewrendered plugin >>
            #@+node:ekr.20110605121601.18505: *5* << load viewrendered plugin >>
            pc = g.app.pluginsController
            # Load viewrendered (and call vr.onCreate) *only* if not already loaded.
            if (
                not pc.isLoaded('viewrendered.py')
                and not pc.isLoaded('viewrendered3.py')
            ):
                vr = pc.loadOnePlugin('viewrendered.py')
                if vr:
                    g.blue('viewrendered plugin loaded.')
                    vr.onCreate('tag', {'c': c})
            #@-<< load viewrendered plugin >>
            retval = send()
            if retval:
                return retval
            #@+<< no dialog error >>
            #@+node:ekr.20110605121601.18506: *5* << no dialog error >>
            g.es_print_error(
                f'No handler for the "scrolledMessage" hook.\n\t{g.callers()}')
            #@-<< no dialog error >>
        #@+<< emergency fallback >>
        #@+node:ekr.20110605121601.18507: *5* << emergency fallback >>
        dialog = QtWidgets.QMessageBox(None)
        dialog.setWindowFlags(WindowType.Dialog)
            # That is, not a fixed size dialog.
        dialog.setWindowTitle(title)
        if msg:
            dialog.setText(msg)
        dialog.setIcon(Icon.Information)
        dialog.addButton('Ok', ButtonRole.YesRole)
        try:
            c.in_qt_dialog = True
            if isQt6:
                dialog.exec()
            else:
                dialog.exec_()
        finally:
            c.in_qt_dialog = False
        #@-<< emergency fallback >>
    #@+node:ekr.20110607182447.16456: *3* qt_gui.Event handlers
    #@+node:ekr.20190824094650.1: *4* qt_gui.close_event
    def close_event(self, event):

        noclose = False
        if g.app.sessionManager and g.app.loaded_session:
            g.app.sessionManager.save_snapshot()
        for c in g.app.commanders():
            allow = c.exists and g.app.closeLeoWindow(c.frame)
            if not allow:
                noclose = True
        if noclose:
            event.ignore()
        else:
            event.accept()
    #@+node:ekr.20110605121601.18481: *4* qt_gui.onDeactiveEvent
    # deactivated_name = ''

    deactivated_widget = None

    def onDeactivateEvent(self, event, c, obj, tag):
        """
        Gracefully deactivate the Leo window.
        Called several times for each window activation.
        """
        w = self.get_focus()
        w_name = w and w.objectName()
        if 'focus' in g.app.debug:
            g.trace(repr(w_name))
        self.active = False
            # Used only by c.idle_focus_helper.
        #
        # Careful: never save headline widgets.
        if w_name == 'headline':
            self.deactivated_widget = c.frame.tree.treeWidget
        else:
            self.deactivated_widget = w if w_name else None
        #
        # Causes problems elsewhere...
            # if c.exists and not self.deactivated_name:
                # self.deactivated_name = self.widget_name(self.get_focus())
                # self.active = False
                # c.k.keyboardQuit(setFocus=False)
        g.doHook('deactivate', c=c, p=c.p, v=c.p, event=event)
    #@+node:ekr.20110605121601.18480: *4* qt_gui.onActivateEvent
    # Called from eventFilter

    def onActivateEvent(self, event, c, obj, tag):
        """
        Restore the focus when the Leo window is activated.
        Called several times for each window activation.
        """
        trace = 'focus' in g.app.debug
        w = self.get_focus() or self.deactivated_widget
        self.deactivated_widget = None
        w_name = w and w.objectName()
        # Fix #270: Vim keys don't always work after double Alt+Tab.
        # Fix #359: Leo hangs in LeoQtEventFilter.eventFilter
        # #1273: add teest on c.vim_mode.
        if c.exists and c.vim_mode and c.vimCommands and not self.active and not g.app.killed:
            c.vimCommands.on_activate()
        self.active = True
            # Used only by c.idle_focus_helper.
        if g.isMac:
            pass  # Fix #757: MacOS: replace-then-find does not work in headlines.
        else:
            # Leo 5.6: Recover from missing focus.
            # c.idle_focus_handler can't do this.
            if w and w_name in ('log-widget', 'richTextEdit', 'treeWidget'):
                # Restore focus **only** to body or tree
                if trace:
                    g.trace('==>', w_name)
                c.widgetWantsFocusNow(w)
            else:
                if trace:
                    g.trace(repr(w_name), '==> BODY')
                c.bodyWantsFocusNow()
        # Cause problems elsewhere.
            # if c.exists and self.deactivated_name:
                # self.active = True
                # w_name = self.deactivated_name
                # self.deactivated_name = None
                # if c.p.v:
                    # c.p.v.restoreCursorAndScroll()
                # if w_name.startswith('tree') or w_name.startswith('head'):
                    # c.treeWantsFocusNow()
                # else:
                    # c.bodyWantsFocusNow()
        g.doHook('activate', c=c, p=c.p, v=c.p, event=event)
    #@+node:ekr.20130921043420.21175: *4* qt_gui.setFilter
    # w's type is in (DynamicWindow,QMinibufferWrapper,LeoQtLog,LeoQtTree,
    # QTextEditWrapper,LeoQTextBrowser,LeoQuickSearchWidget,cleoQtUI)

    def setFilter(self, c, obj, w, tag):
        """
        Create an event filter in obj.
        w is a wrapper object, not necessarily a QWidget.
        """
        # gui = self
        assert isinstance(obj, QtWidgets.QWidget), obj
        theFilter = qt_events.LeoQtEventFilter(c, w=w, tag=tag)
        obj.installEventFilter(theFilter)
        w.ev_filter = theFilter
            # Set the official ivar in w.
    #@+node:ekr.20110605121601.18508: *3* qt_gui.Focus
    #@+node:ekr.20190601055031.1: *4* qt_gui.ensure_commander_visible
    def ensure_commander_visible(self, c1):
        """
        Check to see if c.frame is in a tabbed ui, and if so, make sure
        the tab is visible
        """
        # pylint: disable=arguments-differ
        #
        # START: copy from Code-->Startup & external files-->
        # @file runLeo.py -->run & helpers-->doPostPluginsInit & helpers (runLeo.py)
        # For the qt gui, select the first-loaded tab.
        if 'focus' in g.app.debug:
            g.trace(c1)
        if hasattr(g.app.gui, 'frameFactory'):
            factory = g.app.gui.frameFactory
            if factory and hasattr(factory, 'setTabForCommander'):
                c = c1
                factory.setTabForCommander(c)
                c.bodyWantsFocusNow()
        # END: copy
    #@+node:ekr.20190601054958.1: *4* qt_gui.get_focus
    def get_focus(self, c=None, raw=False, at_idle=False):
        """Returns the widget that has focus."""
        # pylint: disable=arguments-differ
        trace = 'focus' in g.app.debug
        trace_idle = False
        trace = trace and (trace_idle or not at_idle)
        app = QtWidgets.QApplication
        w = app.focusWidget()
        if w and not raw and isinstance(w, qt_text.LeoQTextBrowser):
            has_w = getattr(w, 'leo_wrapper', None)
            if has_w:
                if trace:
                    g.trace(w)
            elif c:
                # Kludge: DynamicWindow creates the body pane
                # with wrapper = None, so return the LeoQtBody.
                w = c.frame.body
        if trace:
            name = w.objectName() if hasattr(w, 'objectName') else w.__class__.__name__
            g.trace('(LeoQtGui)', name)
        return w
    #@+node:ekr.20190601054959.1: *4* qt_gui.set_focus
    def set_focus(self, c, w):
        """Put the focus on the widget."""
        # pylint: disable=arguments-differ
        if not w:
            return
        if getattr(w, 'widget', None):
            if not isinstance(w, QtWidgets.QWidget):
                # w should be a wrapper.
                w = w.widget
        if 'focus' in g.app.debug:
            name = w.objectName() if hasattr(w, 'objectName') else w.__class__.__name__
            g.trace('(LeoQtGui)', name)
        w.setFocus()
    #@+node:ekr.20110605121601.18510: *3* qt_gui.getFontFromParams
    size_warnings: List[str] = []

    def getFontFromParams(self, family, size, slant, weight, defaultSize=12):
        """Required to handle syntax coloring."""
        if isinstance(size, str):
            if size.endswith('pt'):
                size = size[:-2].strip()
            elif size.endswith('px'):
                if size not in self.size_warnings:
                    self.size_warnings.append(size)
                    g.es(f"px ignored in font setting: {size}")
                size = size[:-2].strip()
        try:
            size = int(size)
        except Exception:
            size = 0
        if size < 1:
            size = defaultSize
        d = {
            'black': Weight.Black,
            'bold': Weight.Bold,
            'demibold': Weight.DemiBold,
            'light': Weight.Light,
            'normal': Weight.Normal,
        }
        weight_val = d.get(weight.lower(), Weight.Normal)
        italic = slant == 'italic'
        if not family:
            family = g.app.config.defaultFontFamily
        if not family:
            family = 'DejaVu Sans Mono'
        try:
            font = QtGui.QFont(family, size, weight_val, italic)
            if sys.platform.startswith('linux'):
                font.setHintingPreference(font.PreferFullHinting)
            # g.es(font,font.hintingPreference())
            return font
        except Exception:
            g.es("exception setting font", g.callers(4))
            g.es(
                f"family: {family}\n"
                f"  size: {size}\n"
                f" slant: {slant}\n"
                f"weight: {weight}")
            # g.es_exception() # This just confuses people.
            return g.app.config.defaultFont
    #@+node:ekr.20110605121601.18511: *3* qt_gui.getFullVersion
    def getFullVersion(self, c=None):
        """Return the PyQt version (for signon)"""
        try:
            qtLevel = f"version {QtCore.QT_VERSION_STR}"
        except Exception:
            # g.es_exception()
            qtLevel = '<qtLevel>'
        return f"PyQt {qtLevel}"
    #@+node:ekr.20110605121601.18514: *3* qt_gui.Icons
    #@+node:ekr.20110605121601.18515: *4* qt_gui.attachLeoIcon
    def attachLeoIcon(self, window):
        """Attach a Leo icon to the window."""
        #icon = self.getIconImage('leoApp.ico')
        if self.appIcon:
            window.setWindowIcon(self.appIcon)
    #@+node:ekr.20110605121601.18516: *4* qt_gui.getIconImage
    def getIconImage(self, name):
        """Load the icon and return it."""
        # Return the image from the cache if possible.
        if name in self.iconimages:
            image = self.iconimages.get(name)
            return image
        try:
            iconsDir = g.os_path_join(g.app.loadDir, "..", "Icons")
            homeIconsDir = g.os_path_join(g.app.homeLeoDir, "Icons")
            for theDir in (homeIconsDir, iconsDir):
                fullname = g.os_path_finalize_join(theDir, name)
                if g.os_path_exists(fullname):
                    if 0:  # Not needed: use QTreeWidget.setIconsize.
                        pixmap = QtGui.QPixmap()
                        pixmap.load(fullname)
                        image = QtGui.QIcon(pixmap)
                    else:
                        image = QtGui.QIcon(fullname)
                    self.iconimages[name] = image
                    return image
            # No image found.
            return None
        except Exception:
            g.es_print("exception loading:", fullname)
            g.es_exception()
            return None
    #@+node:ekr.20110605121601.18517: *4* qt_gui.getImageImage
    @functools.lru_cache(maxsize=128)
    def getImageImage(self, name):
        """Load the image in file named `name` and return it."""
        fullname = self.getImageFinder(name)
        try:
            pixmap = QtGui.QPixmap()
            pixmap.load(fullname)
            return pixmap
        except Exception:
            g.es("exception loading:", name)
            g.es_exception()
            return None
    #@+node:tbrown.20130316075512.28478: *4* qt_gui.getImageFinder
    dump_given = False
    @functools.lru_cache(maxsize=128)
    def getImageFinder(self, name):
        """Theme aware image (icon) path searching."""
        trace = 'themes' in g.app.debug
        exists = g.os_path_exists
        getString = g.app.config.getString

        def dump(var, val):
            print(f"{var:20}: {val}")

        join = g.os_path_join
        #
        # "Just works" for --theme and theme .leo files *provided* that
        # theme .leo files actually contain these settings!
        #
        theme_name1 = getString('color-theme')
        theme_name2 = getString('theme-name')
        roots = [
            g.os_path_join(g.computeHomeDir(), '.leo'),
            g.computeLeoDir(),
        ]
        theme_subs = [
            "themes/{theme}/Icons",
            "themes/{theme}",
            "Icons/{theme}",
        ]
        bare_subs = ["Icons", "."]
            # "." for icons referred to as Icons/blah/blah.png
        paths = []
        for theme_name in (theme_name1, theme_name2):
            for root in roots:
                for sub in theme_subs:
                    paths.append(join(root, sub.format(theme=theme_name)))
        for root in roots:
            for sub in bare_subs:
                paths.append(join(root, sub))
        table = [z for z in paths if exists(z)]
        for base_dir in table:
            path = join(base_dir, name)
            if exists(path):
                if trace:
                    g.trace(f"Found {name} in {base_dir}")
                return path
            # if trace: g.trace(name, 'not in', base_dir)
        if trace:
            g.trace('not found:', name)
        return None
    #@+node:ekr.20110605121601.18518: *4* qt_gui.getTreeImage
    @functools.lru_cache(maxsize=128)
    def getTreeImage(self, c, path):
        image = QtGui.QPixmap(path)
        if image.height() > 0 and image.width() > 0:
            return image, image.height()
        return None, None
    #@+node:ekr.20131007055150.17608: *3* qt_gui.insertKeyEvent
    def insertKeyEvent(self, event, i):
        """Insert the key given by event in location i of widget event.w."""
        assert isinstance(event, leoGui.LeoKeyEvent)
        qevent = event.event
        assert isinstance(qevent, QtGui.QKeyEvent)
        qw = getattr(event.w, 'widget', None)
        if qw and isinstance(qw, QtWidgets.QTextEdit):
            if 1:
                # Assume that qevent.text() *is* the desired text.
                # This means we don't have to hack eventFilter.
                qw.insertPlainText(qevent.text())
            else:
                # Make no such assumption.
                # We would like to use qevent to insert the character,
                # but this would invoke eventFilter again!
                # So set this flag for eventFilter, which will
                # return False, indicating that the widget must handle
                # qevent, which *presumably* is the best that can be done.
                g.app.gui.insert_char_flag = True
    #@+node:ekr.20190819072045.1: *3* qt_gui.make_main_window
    def make_main_window(self):
        """Make the *singleton* QMainWindow."""
        window = QtWidgets.QMainWindow()
        window.setObjectName('LeoGlobalMainWindow')
        # Calling window.show() here causes flash.
        self.attachLeoIcon(window)
        # Monkey-patch
        window.closeEvent = self.close_event
            # Use self: g.app.gui does not exist yet.
        self.runAtIdle(self.set_main_window_style_sheet)
            # No StyleSheetManager exists yet.
        return window

    def set_main_window_style_sheet(self):
        """Style the main window, using the first .leo file."""
        commanders = g.app.commanders()
        if commanders:
            c = commanders[0]
            ssm = c.styleSheetManager
            ssm.set_style_sheets(w=self.main_window)
            self.main_window.setWindowTitle(c.frame.title)  # #1506.
        else:
            g.trace("No open commanders!")
    #@+node:ekr.20110605121601.18528: *3* qt_gui.makeScriptButton
    def makeScriptButton(self, c,
        args=None,
        p=None,  # A node containing the script.
        script=None,  # The script itself.
        buttonText=None,
        balloonText='Script Button',
        shortcut=None, bg='LightSteelBlue1',
        define_g=True, define_name='__main__', silent=False,  # Passed on to c.executeScript.
    ):
        """
        Create a script button for the script in node p.
        The button's text defaults to p.headString."""
        k = c.k
        if p and not buttonText:
            buttonText = p.h.strip()
        if not buttonText:
            buttonText = 'Unnamed Script Button'
        #@+<< create the button b >>
        #@+node:ekr.20110605121601.18529: *4* << create the button b >>
        iconBar = c.frame.getIconBarObject()
        b = iconBar.add(text=buttonText)
        #@-<< create the button b >>
        #@+<< define the callbacks for b >>
        #@+node:ekr.20110605121601.18530: *4* << define the callbacks for b >>
        def deleteButtonCallback(event=None, b=b, c=c):
            if b:
                b.pack_forget()
            c.bodyWantsFocus()

        def executeScriptCallback(event=None,
            b=b,
            c=c,
            buttonText=buttonText,
            p=p and p.copy(),
            script=script
        ):
            if c.disableCommandsMessage:
                g.blue('', c.disableCommandsMessage)
            else:
                g.app.scriptDict = {'script_gnx': p.gnx}
                c.executeScript(args=args, p=p, script=script,
                define_g=define_g, define_name=define_name, silent=silent)
                # Remove the button if the script asks to be removed.
                if g.app.scriptDict.get('removeMe'):
                    g.es('removing', f"'{buttonText}'", 'button at its request')
                    b.pack_forget()
            # Do not assume the script will want to remain in this commander.

        #@-<< define the callbacks for b >>

        b.configure(command=executeScriptCallback)
        if shortcut:
            #@+<< bind the shortcut to executeScriptCallback >>
            #@+node:ekr.20110605121601.18531: *4* << bind the shortcut to executeScriptCallback >>
            # In qt_gui.makeScriptButton.
            func = executeScriptCallback
            if shortcut:
                shortcut = g.KeyStroke(shortcut)
            ok = k.bindKey('button', shortcut, func, buttonText)
            if ok:
                g.blue('bound @button', buttonText, 'to', shortcut)
            #@-<< bind the shortcut to executeScriptCallback >>
        #@+<< create press-buttonText-button command >>
        #@+node:ekr.20110605121601.18532: *4* << create press-buttonText-button command >> qt_gui.makeScriptButton
        # #1121. Like sc.cleanButtonText
        buttonCommandName = f"press-{buttonText.replace(' ', '-').strip('-')}-button"
        #
        # This will use any shortcut defined in an @shortcuts node.
        k.registerCommand(buttonCommandName, executeScriptCallback, pane='button')
        #@-<< create press-buttonText-button command >>
    #@+node:ekr.20170612065255.1: *3* qt_gui.put_help
    def put_help(self, c, s, short_title=''):
        """Put the help command."""
        s = textwrap.dedent(s.rstrip())
        if s.startswith('<') and not s.startswith('<<'):
            pass  # how to do selective replace??
        pc = g.app.pluginsController
        table = (
            'viewrendered3.py',
            'viewrendered.py',
        )
        for name in table:
            if pc.isLoaded(name):
                vr = pc.loadOnePlugin(name)
                break
        else:
            vr = pc.loadOnePlugin('viewrendered.py')
        if vr:
            kw = {
                'c': c,
                'flags': 'rst',
                'kind': 'rst',
                'label': '',
                'msg': s,
                'name': 'Apropos',
                'short_title': short_title,
                'title': ''}
            vr.show_scrolled_message(tag='Apropos', kw=kw)
            c.bodyWantsFocus()
            if g.unitTesting:
                vr.close_rendering_pane(event={'c': c})
        elif g.unitTesting:
            pass
        else:
            g.es(s)
        return vr  # For unit tests
    #@+node:ekr.20110605121601.18521: *3* qt_gui.runAtIdle
    def runAtIdle(self, aFunc):
        """This can not be called in some contexts."""
        QtCore.QTimer.singleShot(0, aFunc)
    #@+node:ekr.20110605121601.18483: *3* qt_gui.runMainLoop & runWithIpythonKernel
    #@+node:ekr.20130930062914.16000: *4* qt_gui.runMainLoop
    def runMainLoop(self):
        """Start the Qt main loop."""
        try:  # #2127: A crash here hard-crashes Leo: There is no main loop!
            g.app.gui.dismiss_splash_screen()
            g.app.gui.show_tips()
        except Exception:
            g.es_exception()
        if self.script:
            log = g.app.log
            if log:
                g.pr('Start of batch script...\n')
                log.c.executeScript(script=self.script)
                g.pr('End of batch script')
            else:
                g.pr('no log, no commander for executeScript in LeoQtGui.runMainLoop')
        elif g.app.useIpython and g.app.ipython_inited:
            self.runWithIpythonKernel()
        else:
            # This can be alarming when using Python's -i option.
            if isQt6:
                sys.exit(self.qtApp.exec())
            else:
                sys.exit(self.qtApp.exec_())
    #@+node:ekr.20130930062914.16001: *4* qt_gui.runWithIpythonKernel (commands)
    def runWithIpythonKernel(self):
        """Init Leo to run in an IPython shell."""
        try:
            from leo.core import leoIPython
            g.app.ipk = leoIPython.InternalIPKernel()
            g.app.ipk.run()
        except Exception:
            g.es_exception()
            print('can not init leo.core.leoIPython.py')
            sys.exit(1)
    #@+node:ekr.20200304125716.1: *3* qt_gui.onContextMenu
    def onContextMenu(self, c, w, point):
        """LeoQtGui: Common context menu handling."""
        # #1286.
        handlers = g.tree_popup_handlers
        menu = QtWidgets.QMenu(c.frame.top)  # #1995.
        menuPos = w.mapToGlobal(point)
        if not handlers:
            menu.addAction("No popup handlers")
        p = c.p.copy()
        done = set()
        for handler in handlers:
            # every handler has to add it's QActions by itself
            if handler in done:
                # do not run the same handler twice
                continue
            try:
                handler(c, p, menu)
            except Exception:
                g.es_print('Exception executing right-click handler')
                g.es_exception()
        menu.popup(menuPos)
        self._contextmenu = menu
    #@+node:ekr.20190822174038.1: *3* qt_gui.set_top_geometry
    already_sized = False

    def set_top_geometry(self, w, h, x, y):
        """Set the geometry of the main window."""
        if 'size' in g.app.debug:
            g.trace('(qt_gui) already_sized', self.already_sized, w, h, x, y)
        if not self.already_sized:
            self.already_sized = True
            self.main_window.setGeometry(QtCore.QRect(x, y, w, h))
    #@+node:ekr.20180117053546.1: *3* qt_gui.show_tips & helpers
    @g.command('show-next-tip')
    def show_next_tip(self, event=None):
        g.app.gui.show_tips(force=True)


    class DialogWithCheckBox(QtWidgets.QMessageBox):

        def __init__(self, controller, tip):
            super().__init__()
            c = g.app.log.c
            self.leo_checked = True
            self.setObjectName('TipMessageBox')
            self.setIcon(Icon.Information)  # #2127.
            # self.setMinimumSize(5000, 4000)
                # Doesn't work.
                # Prevent the dialog from jumping around when
                # selecting multiple tips.
            self.setWindowTitle('Leo Tips')
            self.setText(repr(tip))
            self.next_tip_button = self.addButton('Show Next Tip', ButtonRole.ActionRole)  # #2127
            self.addButton('Ok', ButtonRole.YesRole)  # #2127.
            c.styleSheetManager.set_style_sheets(w=self)
            # Workaround #693.
            layout = self.layout()
            cb = QtWidgets.QCheckBox()
            cb.setObjectName('TipCheckbox')
            cb.setText('Show Tip On Startup')
            cb.setCheckState(QtConst.CheckState.Checked)  # #2127.
            cb.stateChanged.connect(controller.onClick)
            layout.addWidget(cb, 4, 0, -1, -1)
            if 0:  # Does not work well.
                sizePolicy = QtWidgets.QSizePolicy
                vSpacer = QtWidgets.QSpacerItem(
                    200, 200, sizePolicy.Minimum, sizePolicy.Expanding)
                layout.addItem(vSpacer)

    def show_tips(self, force=False):
        from leo.core import leoTips
        if g.unitTesting:
            return
        c = g.app.log and g.app.log.c
        if not c:
            g.pr('qt_gui:show_tips: NO g.app.log')
            return  # pyzo guard.
        self.show_tips_flag = c.config.getBool('show-tips', default=False)
        if not force and not self.show_tips_flag:
            return
        tm = leoTips.TipManager()
        while True:  # QMessageBox is always a modal dialog.
            tip = tm.get_next_tip()
            m = self.DialogWithCheckBox(controller=self, tip=tip)
            try:
                c.in_qt_dialog = True
                m.exec_()
            finally:
                c.in_qt_dialog = False
            b = m.clickedButton()
            g.trace(b)
            self.update_tips_setting()
            if b != m.next_tip_button:
                break

    #@+node:ekr.20180117080131.1: *4* onButton (not used)
    def onButton(self, m):
        m.hide()
    #@+node:ekr.20180117073603.1: *4* onClick
    def onClick(self, state):
        self.show_tips_flag = bool(state)
    #@+node:ekr.20180117083930.1: *5* update_tips_setting
    def update_tips_setting(self):
        c = g.app.log.c
        if c and self.show_tips_flag != c.config.getBool('show-tips', default=False):
            c.config.setUserSetting('@bool show-tips', self.show_tips_flag)
    #@+node:ekr.20180127103142.1: *4* onNext
    def onNext(self, *args, **keys):
        g.trace(args, keys)
        return True
    #@+node:ekr.20111215193352.10220: *3* qt_gui.Splash Screen
    #@+node:ekr.20110605121601.18479: *4* qt_gui.createSplashScreen
    def createSplashScreen(self):
        """Put up a splash screen with the Leo logo."""
        splash = None
        if sys.platform.startswith('win'):
            table = ('SplashScreen.jpg', 'SplashScreen.png', 'SplashScreen.ico')
        else:
            table = ('SplashScreen.xpm',)
        for name in table:
            fn = g.os_path_finalize_join(g.app.loadDir, '..', 'Icons', name)
            if g.os_path_exists(fn):
                pm = QtGui.QPixmap(fn)
                if not pm.isNull():
                    splash = QtWidgets.QSplashScreen(pm, WindowType.WindowStaysOnTopHint)
                    splash.show()
                    # This sleep is required to do the repaint.
                    QtCore.QThread.msleep(10)
                    splash.repaint()
                    break
        return splash
    #@+node:ekr.20110613103140.16424: *4* qt_gui.dismiss_splash_screen
    def dismiss_splash_screen(self):

        gui = self
        # Warning: closing the splash screen must be done in the main thread!
        if g.unitTesting:
            return
        if gui.splashScreen:
            gui.splashScreen.hide()
            # gui.splashScreen.deleteLater()
            gui.splashScreen = None
    #@+node:ekr.20140825042850.18411: *3* qt_gui.Utils...
    #@+node:ekr.20110605121601.18522: *4* qt_gui.isTextWidget/Wrapper
    def isTextWidget(self, w):
        """Return True if w is some kind of Qt text widget."""
        if Qsci:
            return isinstance(w, (Qsci.QsciScintilla, QtWidgets.QTextEdit)), w
        return isinstance(w, QtWidgets.QTextEdit), w

    def isTextWrapper(self, w):
        """Return True if w is a Text widget suitable for text-oriented commands."""
        if w is None:
            return False
        if isinstance(w, (g.NullObject, g.TracingNullObject)):
            return True
        return getattr(w, 'supportsHighLevelInterface', None)
    #@+node:ekr.20110605121601.18527: *4* qt_gui.widget_name
    def widget_name(self, w):
        # First try the widget's getName method.
        if not 'w':
            name = '<no widget>'
        elif hasattr(w, 'getName'):
            name = w.getName()
        elif hasattr(w, 'objectName'):
            name = str(w.objectName())
        elif hasattr(w, '_name'):
            name = w._name
        else:
            name = repr(w)
        return name
    #@+node:ekr.20111027083744.16532: *4* qt_gui.enableSignalDebugging
    if isQt5:
        # pylint: disable=no-name-in-module
        # To do: https://doc.qt.io/qt-5/qsignalspy.html
        from PyQt5.QtTest import QSignalSpy
        assert QSignalSpy
    elif isQt6:
        # pylint: disable=c-extension-no-member,no-name-in-module
        import PyQt6.QtTest as QtTest
        # mypy complains about assigning to a type.
        QSignalSpy = QtTest.QSignalSpy  # type:ignore
        assert QSignalSpy
    else:
        # enableSignalDebugging(emitCall=foo) and spy your signals until you're sick to your stomach.
        _oldConnect = QtCore.QObject.connect
        _oldDisconnect = QtCore.QObject.disconnect
        _oldEmit = QtCore.QObject.emit

        def _wrapConnect(self, callableObject):
            """Returns a wrapped call to the old version of QtCore.QObject.connect"""

            @staticmethod  # type:ignore
            def call(*args):
                callableObject(*args)
                self._oldConnect(*args)

            return call

        def _wrapDisconnect(self, callableObject):
            """Returns a wrapped call to the old version of QtCore.QObject.disconnect"""

            @staticmethod  # type:ignore
            def call(*args):
                callableObject(*args)
                self._oldDisconnect(*args)

            return call

        def enableSignalDebugging(self, **kwargs):
            """Call this to enable Qt Signal debugging. This will trap all
            connect, and disconnect calls."""
            f = lambda * args: None
            connectCall = kwargs.get('connectCall', f)
            disconnectCall = kwargs.get('disconnectCall', f)
            emitCall = kwargs.get('emitCall', f)

            def printIt(msg):

                def call(*args):
                    print(msg, args)

                return call

            # Monkey-patch.

            QtCore.QObject.connect = self._wrapConnect(connectCall)
            QtCore.QObject.disconnect = self._wrapDisconnect(disconnectCall)

            def new_emit(self, *args):
                emitCall(self, *args)
                self._oldEmit(self, *args)

            QtCore.QObject.emit = new_emit
    #@+node:ekr.20190819091957.1: *3* qt_gui.Widgets...
    #@+node:ekr.20190819094016.1: *4* qt_gui.createButton
    def createButton(self, parent, name, label):
        w = QtWidgets.QPushButton(parent)
        w.setObjectName(name)
        w.setText(label)
        return w
    #@+node:ekr.20190819091122.1: *4* qt_gui.createFrame
    def createFrame(self, parent, name,
        hPolicy=None, vPolicy=None,
        lineWidth=1,
        shadow=None,
        shape=None,
    ):
        """Create a Qt Frame."""
        if shadow is None:
            shadow = Shadow.Plain
        if shape is None:
            shape = Shape.NoFrame
        #
        w = QtWidgets.QFrame(parent)
        self.setSizePolicy(w, kind1=hPolicy, kind2=vPolicy)
        w.setFrameShape(shape)
        w.setFrameShadow(shadow)
        w.setLineWidth(lineWidth)
        w.setObjectName(name)
        return w
    #@+node:ekr.20190819091851.1: *4* qt_gui.createGrid
    def createGrid(self, parent, name, margin=0, spacing=0):
        w = QtWidgets.QGridLayout(parent)
        w.setContentsMargins(QtCore.QMargins(margin, margin, margin, margin))
        w.setSpacing(spacing)
        w.setObjectName(name)
        return w
    #@+node:ekr.20190819093830.1: *4* qt_gui.createHLayout & createVLayout
    def createHLayout(self, parent, name, margin=0, spacing=0):
        hLayout = QtWidgets.QHBoxLayout(parent)
        hLayout.setObjectName(name)
        hLayout.setSpacing(spacing)
        hLayout.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
        return hLayout

    def createVLayout(self, parent, name, margin=0, spacing=0):
        vLayout = QtWidgets.QVBoxLayout(parent)
        vLayout.setObjectName(name)
        vLayout.setSpacing(spacing)
        vLayout.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
        return vLayout
    #@+node:ekr.20190819094302.1: *4* qt_gui.createLabel
    def createLabel(self, parent, name, label):
        w = QtWidgets.QLabel(parent)
        w.setObjectName(name)
        w.setText(label)
        return w
    #@+node:ekr.20190819092523.1: *4* qt_gui.createTabWidget
    def createTabWidget(self, parent, name, hPolicy=None, vPolicy=None):
        w = QtWidgets.QTabWidget(parent)
        self.setSizePolicy(w, kind1=hPolicy, kind2=vPolicy)
        w.setObjectName(name)
        return w
    #@+node:ekr.20190819091214.1: *4* qt_gui.setSizePolicy
    def setSizePolicy(self, widget, kind1=None, kind2=None):
        if kind1 is None:
            kind1 = Policy.Ignored
        if kind2 is None:
            kind2 = Policy.Ignored
        sizePolicy = QtWidgets.QSizePolicy(kind1, kind2)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(widget.sizePolicy().hasHeightForWidth())
        widget.setSizePolicy(sizePolicy)
    #@-others
#@+node:tbrown.20150724090431.1: ** class StyleClassManager
class StyleClassManager:
    style_sclass_property = 'style_class'  # name of QObject property for styling
    #@+others
    #@+node:tbrown.20150724090431.2: *3* update_view
    def update_view(self, w):
        """update_view - Make Qt apply w's style

        :param QWidgit w: widgit to style
        """

        w.setStyleSheet("/* */")  # forces visual update
    #@+node:tbrown.20150724090431.3: *3* add_sclass
    def add_sclass(self, w, prop):
        """Add style class or list of classes prop to QWidget w"""
        if not prop:
            return
        props = self.sclasses(w)
        if isinstance(prop, str):
            props.append(prop)
        else:
            props.extend(prop)

        self.set_sclasses(w, props)
    #@+node:tbrown.20150724090431.4: *3* clear_sclasses
    def clear_sclasses(self, w):
        """Remove all style classes from QWidget w"""
        w.setProperty(self.style_sclass_property, '')
    #@+node:tbrown.20150724090431.5: *3* has_sclass
    def has_sclass(self, w, prop):
        """Check for style class or list of classes prop on QWidget w"""
        if not prop:
            return None
        props = self.sclasses(w)
        if isinstance(prop, str):
            ans = [prop in props]
        else:
            ans = [i in props for i in prop]
        return all(ans)
    #@+node:tbrown.20150724090431.6: *3* remove_sclass
    def remove_sclass(self, w, prop):
        """Remove style class or list of classes prop from QWidget w"""
        if not prop:
            return
        props = self.sclasses(w)
        if isinstance(prop, str):
            props = [i for i in props if i != prop]
        else:
            props = [i for i in props if i not in prop]

        self.set_sclasses(w, props)
    #@+node:tbrown.20150724090431.7: *3* sclass_tests
    def sclass_tests(self):
        """Test style class property manipulation functions"""

        # pylint: disable=len-as-condition


        class Test_W:
            """simple standin for QWidget for testing"""

            def __init__(self):
                self.x = ''

            def property(self, name, default=None):
                return self.x or default

            def setProperty(self, name, value):
                self.x = value

        w = Test_W()

        assert not self.has_sclass(w, 'nonesuch')
        assert not self.has_sclass(w, ['nonesuch'])
        assert not self.has_sclass(w, ['nonesuch', 'either'])
        assert len(self.sclasses(w)) == 0

        self.add_sclass(w, 'test')

        assert not self.has_sclass(w, 'nonesuch')
        assert self.has_sclass(w, 'test')
        assert self.has_sclass(w, ['test'])
        assert not self.has_sclass(w, ['test', 'either'])
        assert len(self.sclasses(w)) == 1

        self.add_sclass(w, 'test')
        assert len(self.sclasses(w)) == 1
        self.add_sclass(w, ['test', 'test', 'other'])
        assert len(self.sclasses(w)) == 2
        assert self.has_sclass(w, 'test')
        assert self.has_sclass(w, 'other')
        assert self.has_sclass(w, ['test', 'other', 'test'])
        assert not self.has_sclass(w, ['test', 'other', 'nonesuch'])

        self.remove_sclass(w, ['other', 'nothere'])
        assert self.has_sclass(w, 'test')
        assert not self.has_sclass(w, 'other')
        assert len(self.sclasses(w)) == 1

        self.toggle_sclass(w, 'third')
        assert len(self.sclasses(w)) == 2
        assert self.has_sclass(w, ['test', 'third'])
        self.toggle_sclass(w, 'third')
        assert len(self.sclasses(w)) == 1
        assert not self.has_sclass(w, ['test', 'third'])

        self.clear_sclasses(w)
        assert len(self.sclasses(w)) == 0
        assert not self.has_sclass(w, 'test')
    #@+node:tbrown.20150724090431.8: *3* sclasses
    def sclasses(self, w):
        """return list of style classes for QWidget w"""
        return str(w.property(self.style_sclass_property) or '').split()
    #@+node:tbrown.20150724090431.9: *3* set_sclasses
    def set_sclasses(self, w, classes):
        """Set style classes for QWidget w to list in classes"""
        w.setProperty(self.style_sclass_property, f" {' '.join(set(classes))} ")
    #@+node:tbrown.20150724090431.10: *3* toggle_sclass
    def toggle_sclass(self, w, prop):
        """Toggle style class or list of classes prop on QWidget w"""
        if not prop:
            return
        props = set(self.sclasses(w))

        if isinstance(prop, str):
            prop = set([prop])
        else:
            prop = set(prop)

        current = props.intersection(prop)
        props.update(prop)
        props = props.difference(current)

        self.set_sclasses(w, props)
    #@-others
#@+node:ekr.20140913054442.17860: ** class StyleSheetManager
class StyleSheetManager:
    """A class to manage (reload) Qt style sheets."""
    #@+others
    #@+node:ekr.20180316091829.1: *3*  ssm.Birth
    #@+node:ekr.20140912110338.19371: *4* ssm.__init__
    def __init__(self, c, safe=False):
        """Ctor the ReloadStyle class."""
        self.c = c
        self.color_db = leoColor.leo_color_database
        self.safe = safe
        self.settings_p = g.findNodeAnywhere(c, '@settings')
        self.mng = StyleClassManager()
        # This warning is inappropriate in some contexts.
            # if not self.settings_p:
                # g.es("No '@settings' node found in outline.  See:")
                # g.es("http://leoeditor.com/tutorial-basics.html#configuring-leo")
    #@+node:ekr.20170222051716.1: *4* ssm.reload_settings
    def reload_settings(self, sheet=None):
        """
        Recompute and apply the stylesheet.
        Called automatically by the reload-settings commands.
        """
        if not sheet:
            sheet = self.get_style_sheet_from_settings()
        if sheet:
            w = self.get_master_widget()
            w.setStyleSheet(sheet)
        # self.c.redraw()

    reloadSettings = reload_settings
    #@+node:ekr.20180316091500.1: *3* ssm.Paths...
    #@+node:ekr.20180316065346.1: *4* ssm.compute_icon_directories
    def compute_icon_directories(self):
        """
        Return a list of *existing* directories that could contain theme-related icons.
        """
        exists = g.os_path_exists
        home = g.app.homeDir
        join = g.os_path_finalize_join
        leo = join(g.app.loadDir, '..')
        table = [
            join(home, '.leo', 'Icons'),
            # join(home, '.leo'),
            join(leo, 'themes', 'Icons'),
            join(leo, 'themes'),
            join(leo, 'Icons'),
        ]
        table = [z for z in table if exists(z)]
        for directory in self.compute_theme_directories():
            if directory not in table:
                table.append(directory)
            directory2 = join(directory, 'Icons')
            if directory2 not in table:
                table.append(directory2)
        return [g.os_path_normslashes(z) for z in table if g.os_path_exists(z)]
    #@+node:ekr.20180315101238.1: *4* ssm.compute_theme_directories
    def compute_theme_directories(self):
        """
        Return a list of *existing* directories that could contain theme .leo files.
        """
        lm = g.app.loadManager
        table = lm.computeThemeDirectories()[:]
        directory = g.os_path_normslashes(g.app.theme_directory)
        if directory and directory not in table:
            table.insert(0, directory)
        return table
            # All entries are known to exist and have normalized slashes.
    #@+node:ekr.20170307083738.1: *4* ssm.find_icon_path
    def find_icon_path(self, setting):
        """Return the path to the open/close indicator icon."""
        c = self.c
        s = c.config.getString(setting)
        if not s:
            return None  # Not an error.
        for directory in self.compute_icon_directories():
            path = g.os_path_finalize_join(directory, s)
            if g.os_path_exists(path):
                return path
        g.es_print('no icon found for:', setting)
        return None
    #@+node:ekr.20180316091920.1: *3* ssm.Settings
    #@+node:ekr.20110605121601.18176: *4* ssm.default_style_sheet
    def default_style_sheet(self):
        """Return a reasonable default style sheet."""
        # Valid color names: http://www.w3.org/TR/SVG/types.html#ColorKeywords
        g.trace('===== using default style sheet =====')
        return '''\

    /* A QWidget: supports only background attributes.*/
    QSplitter::handle {
        background-color: #CAE1FF; /* Leo's traditional lightSteelBlue1 */
    }
    QSplitter {
        border-color: white;
        background-color: white;
        border-width: 3px;
        border-style: solid;
    }
    QTreeWidget {
        background-color: #ffffec; /* Leo's traditional tree color */
    }
    QsciScintilla {
        background-color: pink;
    }
    '''
    #@+node:ekr.20140916170549.19551: *4* ssm.get_data
    def get_data(self, setting):
        """Return the value of the @data node for the setting."""
        c = self.c
        return c.config.getData(setting, strip_comments=False, strip_data=False) or []
    #@+node:ekr.20140916170549.19552: *4* ssm.get_style_sheet_from_settings
    def get_style_sheet_from_settings(self):
        """
        Scan for themes or @data qt-gui-plugin-style-sheet nodes.
        Return the text of the relevant node.
        """
        aList1 = self.get_data('qt-gui-plugin-style-sheet')
        aList2 = self.get_data('qt-gui-user-style-sheet')
        if aList2:
            aList1.extend(aList2)
        sheet = ''.join(aList1)
        sheet = self.expand_css_constants(sheet)
        return sheet
    #@+node:ekr.20140915194122.19476: *4* ssm.print_style_sheet
    def print_style_sheet(self):
        """Show the top-level style sheet."""
        w = self.get_master_widget()
        sheet = w.styleSheet()
        print(f"style sheet for: {w}...\n\n{sheet}")
    #@+node:ekr.20110605121601.18175: *4* ssm.set_style_sheets
    def set_style_sheets(self, all=True, top=None, w=None):
        """Set the master style sheet for all widgets using config settings."""
        if g.app.loadedThemes:
            return
        c = self.c
        if top is None:
            top = c.frame.top
        selectors = ['qt-gui-plugin-style-sheet']
        if all:
            selectors.append('qt-gui-user-style-sheet')
        sheets = []
        for name in selectors:
            sheet = c.config.getData(name, strip_comments=False)
                # don't strip `#selector_name { ...` type syntax
            if sheet:
                if '\n' in sheet[0]:
                    sheet = ''.join(sheet)
                else:
                    sheet = '\n'.join(sheet)
            if sheet and sheet.strip():
                line0 = f"\n/* ===== From {name} ===== */\n\n"
                sheet = line0 + sheet
                sheets.append(sheet)
        if sheets:
            sheet = "\n".join(sheets)
            # store *before* expanding, so later expansions get new zoom
            c.active_stylesheet = sheet
            sheet = self.expand_css_constants(sheet)
            if not sheet:
                sheet = self.default_style_sheet()
            if w is None:
                w = self.get_master_widget(top)
            w.setStyleSheet(sheet)
    #@+node:ekr.20180316091943.1: *3* ssm.Stylesheet
    # Computations on stylesheets themeselves.
    #@+node:ekr.20140915062551.19510: *4* ssm.expand_css_constants & helpers
    css_warning_given = False

    def expand_css_constants(self, sheet, settingsDict=None):
        """Expand @ settings into their corresponding constants."""
        c = self.c
        trace = 'zoom' in g.app.debug
        # Warn once if the stylesheet uses old style style-sheet comment
        if settingsDict is None:
            settingsDict = c.config.settingsDict  # A TypedDict.
        if 0:
            g.trace('===== settingsDict...')
            for key in settingsDict.keys():
                print(f"{key:40}: {settingsDict.get(key)}")
        constants, deltas = self.adjust_sizes(settingsDict)
        if trace:
            print('')
            g.trace(f"zoom constants: {constants}")
            g.printObj(deltas, tag='zoom deltas')  # A defaultdict
        sheet = self.replace_indicator_constants(sheet)
        for pass_n in range(10):
            to_do = self.find_constants_referenced(sheet)
            if not to_do:
                break
            old_sheet = sheet
            sheet = self.do_pass(constants, deltas, settingsDict, sheet, to_do)
            if sheet == old_sheet:
                break
        else:
            g.trace('Too many iterations')
        if to_do:
            g.trace('Unresolved @constants')
            g.printObj(to_do)
        sheet = self.resolve_urls(sheet)
        sheet = sheet.replace('\\\n', '')  # join lines ending in \
        return sheet
    #@+node:ekr.20150617085045.1: *5* ssm.adjust_sizes
    def adjust_sizes(self, settingsDict):
        """Adjust constants to reflect c._style_deltas."""
        c = self.c
        constants = {}  # old: self.find_constants_defined(sheet)
        deltas = c._style_deltas
        for delta in c._style_deltas:
            # adjust @font-size-body by font_size_delta
            # easily extendable to @font-size-*
            val = c.config.getString(delta)
            passes = 10
            while passes and val and val.startswith('@'):
                key = g.app.config.canonicalizeSettingName(val[1:])
                val = settingsDict.get(key)
                if val:
                    val = val.val
                passes -= 1
            if deltas[delta] and (val is not None):
                size = ''.join(i for i in val if i in '01234567890.')
                units = ''.join(i for i in val if i not in '01234567890.')
                size = max(1, int(size) + deltas[delta])
                constants['@' + delta] = f"{size}{units}"
        return constants, deltas
    #@+node:ekr.20180316093159.1: *5* ssm.do_pass
    def do_pass(self, constants, deltas, settingsDict, sheet, to_do):

        to_do.sort(key=len, reverse=True)
        for const in to_do:
            value = None
            if const in constants:
                # This constant is about to be removed.
                value = constants[const]
                if const[1:] not in deltas and not self.css_warning_given:
                    self.css_warning_given = True
                    g.es_print(f"'{const}' from style-sheet comment definition, ")
                    g.es_print("please use regular @string / @color type @settings.")
            else:
                key = g.app.config.canonicalizeSettingName(const[1:])
                    # lowercase, without '@','-','_', etc.
                value = settingsDict.get(key)
                if value is not None:
                    # New in Leo 5.5: Do NOT add comments here.
                    # They RUIN style sheets if they appear in a nested comment!
                        # value = '%s /* %s */' % (value.val, key)
                    value = value.val
                elif key in self.color_db:
                    # New in Leo 5.5: Do NOT add comments here.
                    # They RUIN style sheets if they appear in a nested comment!
                    value = self.color_db.get(key)
                        # value = '%s /* %s */' % (value, key)
            if value:
                # Partial fix for #780.
                try:
                    sheet = re.sub(
                        const + "(?![-A-Za-z0-9_])",
                            # don't replace shorter constants occuring in larger
                        value,
                        sheet,
                    )
                except Exception:
                    g.es_print('Exception handling style sheet')
                    g.es_print(sheet)
                    g.es_exception()
            else:
                pass
                # tricky, might be an undefined identifier, but it might
                # also be a @foo in a /* comment */, where it's harmless.
                # So rely on whoever calls .setStyleSheet() to do the right thing.
        return sheet
    #@+node:tbrown.20131120093739.27085: *5* ssm.find_constants_referenced
    def find_constants_referenced(self, text):
        """find_constants - Return a list of constants referenced in the supplied text,
        constants match::

            @[A-Za-z_][-A-Za-z0-9_]*
            i.e. @foo_1-5

        :Parameters:
        - `text`: text to search
        """
        aList = sorted(set(re.findall(r"@[A-Za-z_][-A-Za-z0-9_]*", text)))
        # Exempt references to Leo constructs.
        for s in ('@button', '@constants', '@data', '@language'):
            if s in aList:
                aList.remove(s)
        return aList
    #@+node:tbrown.20130411121812.28335: *5* ssm.find_constants_defined (no longer used)
    def find_constants_defined(self, text):
        r"""find_constants - Return a dict of constants defined in the supplied text.

        NOTE: this supports a legacy way of specifying @<identifiers>, regular
        @string and @color settings should be used instead, so calling this
        wouldn't be needed.  expand_css_constants() issues a warning when
        @<identifiers> are found in the output of this method.

        Constants match::

            ^\s*(@[A-Za-z_][-A-Za-z0-9_]*)\s*=\s*(.*)$
            i.e.
            @foo_1-5=a
                @foo_1-5 = a more here

        :Parameters:
        - `text`: text to search
        """
        pattern = re.compile(r"^\s*(@[A-Za-z_][-A-Za-z0-9_]*)\s*=\s*(.*)$")
        ans: Dict[str, str] = {}
        text = text.replace('\\\n', '')  # merge lines ending in \
        for line in text.split('\n'):
            test = pattern.match(line)
            if test:
                ans.update([test.groups()])  # type:ignore  # Mysterious
        # constants may refer to other constants, de-reference here
        change = True
        level = 0
        while change and level < 10:
            level += 1
            change = False
            for k in ans:
                # pylint: disable=unnecessary-lambda
                # process longest first so @solarized-base0 is not replaced
                # when it's part of @solarized-base03
                for o in sorted(ans, key=lambda x: len(x), reverse=True):
                    if o in ans[k]:
                        change = True
                        ans[k] = ans[k].replace(o, ans[o])
        if level == 10:
            print("Ten levels of recursion processing styles, abandoned.")
            g.es("Ten levels of recursion processing styles, abandoned.")
        return ans
    #@+node:ekr.20150617090104.1: *5* ssm.replace_indicator_constants
    def replace_indicator_constants(self, sheet):
        """
        In the stylesheet, replace (if they exist)::

            image: @tree-image-closed
            image: @tree-image-open

        by::

            url(path/closed.png)
            url(path/open.png)

        path can be relative to ~ or to leo/Icons.

        Assuming that ~/myIcons/closed.png exists, either of these will work::

            @string tree-image-closed = nodes-dark/triangles/closed.png
            @string tree-image-closed = myIcons/closed.png

        Return the updated stylesheet.
        """
        close_path = self.find_icon_path('tree-image-closed')
        open_path = self.find_icon_path('tree-image-open')
        # Make all substitutions in the stylesheet.
        table = (
            (open_path, re.compile(r'\bimage:\s*@tree-image-open', re.IGNORECASE)),
            (close_path, re.compile(r'\bimage:\s*@tree-image-closed', re.IGNORECASE)),
            # (open_path,  re.compile(r'\bimage:\s*at-tree-image-open', re.IGNORECASE)),
            # (close_path, re.compile(r'\bimage:\s*at-tree-image-closed', re.IGNORECASE)),
        )
        for path, pattern in table:
            for mo in pattern.finditer(sheet):
                old = mo.group(0)
                new = f"image: url({path})"
                sheet = sheet.replace(old, new)
        return sheet
    #@+node:ekr.20180320054305.1: *5* ssm.resolve_urls
    def resolve_urls(self, sheet):
        """Resolve all relative url's so they use absolute paths."""
        trace = 'themes' in g.app.debug
        pattern = re.compile(r'url\((.*)\)')
        join = g.os_path_finalize_join
        directories = self.compute_icon_directories()
        paths_traced = False
        if trace:
            paths_traced = True
            g.trace('Search paths...')
            g.printObj(directories)
        # Pass 1: Find all replacements without changing the sheet.
        replacements = []
        for mo in pattern.finditer(sheet):
            url = mo.group(1)
            if url.startswith(':/'):
                url = url[2:]
            elif g.os_path_isabs(url):
                if trace:
                    g.trace('ABS:', url)
                continue
            for directory in directories:
                path = join(directory, url)
                if g.os_path_exists(path):
                    if trace:
                        g.trace(f"{url:35} ==> {path}")
                    old = mo.group(0)
                    new = f"url({path})"
                    replacements.append((old, new),)
                    break
            else:
                g.trace(f"{url:35} ==> NOT FOUND")
                if not paths_traced:
                    paths_traced = True
                    g.trace('Search paths...')
                    g.printObj(directories)
        # Pass 2: Now we can safely make the replacements.
        for old, new in reversed(replacements):
            sheet = sheet.replace(old, new)
        return sheet
    #@+node:ekr.20140912110338.19372: *4* ssm.munge
    def munge(self, stylesheet):
        """
        Return the stylesheet without extra whitespace.

        To avoid false mismatches, this should approximate what Qt does.
        To avoid false matches, this should not munge too much.
        """
        s = ''.join([s.lstrip().replace('  ', ' ').replace(' \n', '\n')
            for s in g.splitLines(stylesheet)])
        return s.rstrip()
            # Don't care about ending newline.
    #@+node:ekr.20180317062556.1: *3* sss.Theme files
    #@+node:ekr.20180316092116.1: *3* ssm.Widgets
    #@+node:ekr.20140913054442.19390: *4* ssm.get_master_widget
    def get_master_widget(self, top=None):
        """
        Carefully return the master widget.
        c.frame.top is a DynamicWindow.
        """
        if top is None:
            top = self.c.frame.top
        master = top.leo_master or top
        return master
    #@+node:ekr.20140913054442.19391: *4* ssm.set selected_style_sheet
    def set_selected_style_sheet(self):
        """For manual testing: update the stylesheet using c.p.b."""
        if not g.unitTesting:
            c = self.c
            sheet = c.p.b
            sheet = self.expand_css_constants(sheet)
            w = self.get_master_widget(c.frame.top)
            w.setStyleSheet(sheet)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
