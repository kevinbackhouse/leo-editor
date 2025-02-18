# Created by wax-off script: 7/30/2021.

# Imports added by hand from leoGlobals.py:

import unittest
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Set, Tuple, Union
from leo.core.leoCommands import Commands as Cmdr
from leo.core.leoNodes import Position as Pos

# Comment out all stubs for inner functions. Remove functions appearing in docstrings.

def callback(func: Callable) -> Any: ...
    # def a_callback(...): ...
    # def callback_wrapper(*args, **keys): ...
def check_cmd_instance_dict(c: Cmdr, g: Any) -> None: ...
class Command:
    #    def A_Command(event): ...
    def __init__(self, name: str, **kwargs: Any) -> None: ...
    def __call__(self, func: Callable) -> Callable: ...
def command_alias(alias: str, func: Callable) -> None: ...
class CommanderCommand:
   #     def command_name(self, *args, **kwargs): ...
    def __init__(self, name: str, **kwargs: Any) -> None: ...
    def __call__(self, func: Callable) -> Callable: ...
    #    def commander_command_wrapper(event: Any) -> None: ...
def ivars2instance(c: Cmdr, g: Any, ivars: List[str]) -> Any: ...
def new_cmd_decorator(name: str, ivars: List[str]) -> Callable: ...
    # def _decorator(func: Callable) -> Callable: ...
    # def new_cmd_wrapper(event: Any) -> None: ...
def standard_timestamp() -> str: ...
def get_backup_path(sub_directory: str) -> Optional[str]: ...
class BindingInfo:
    def __init__(
        self,
        kind: str,
        commandName: str='',
        func: Any=None,
        nextMode: Any=None,
        pane: Any=None,
        stroke: Any=None,
    ) -> None: ...
    def __hash__(self) -> Any: ...
    def __repr__(self) -> str: ...
    def dump(self) -> str: ...
    def isModeBinding(self) -> bool: ...
def isBindingInfo(obj: Any) -> bool: ...
class Bunch:
    def __init__(self, **keywords: Any) -> None: ...
    def __repr__(self) -> str: ...
    def ivars(self) -> Any: ...
    def keys(self) -> Any: ...
    def toString(self) -> str: ...
    def __setitem__(self, key: str, value: Any) -> Any: ...
    def __getitem__(self, key: str) -> Any: ...
    def get(self, key: str, theDefault: Any=None) -> Any: ...
    def __contains__(self, key: str) -> bool: ...
class EmergencyDialog:
    def __init__(self, title: str, message: str) -> None: ...
    def createButtons(self, buttons: List[Dict[str, Any]]) -> List[Any]: ...
    def createTopFrame(self) -> None: ...
    def okButton(self) -> None: ...
    def onKey(self, event: Any) -> None: ...
    def run(self) -> None: ...
class FileLikeObject:
    def __init__(self, encoding: str='utf-8', fromString: str=None) -> None: ...
    def clear(self) -> None: ...
    def close(self) -> None: ...
    def flush(self) -> None: ...
    def get(self) -> str: ...
    def readline(self) -> str: ...
    def write(self, s: str) -> None: ...
class GeneralSetting:
    def __init__(self, kind: str,
        encoding: str=None,
        ivar: str=None,
        setting: str=None,
        val: Any=None,
        path: str=None,
        tag: str='setting',
        unl: str=None,
    ) -> None: ...
    def __repr__(self) -> str: ...
class KeyStroke:
    def __init__(self, binding: str) -> None: ...
    def __eq__(self, other: Any) -> bool: ...
    def __lt__(self, other: Any) -> bool: ...
    def __le__(self, other: Any) -> bool: ...
    def __ne__(self, other: Any) -> bool: ...
    def __gt__(self, other: Any) -> bool: ...
    def __ge__(self, other: Any) -> bool: ...
    def __hash__(self) -> Any: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def dump(self) -> None: ...
    def finalize_binding(self, binding: str) -> str: ...
    def finalize_char(self, s: str) -> str: ...
    def strip_shift(self, s: str) -> str: ...
    def find(self, pattern: str) -> int: ...
    def lower(self) -> str: ...
    def startswith(self, s: str) -> bool: ...
    def find_mods(self, s: str) -> List[str]: ...
    def isAltCtrl(self) -> bool: ...
    def isFKey(self) -> bool: ...
    def isPlainKey(self) -> bool: ...
    def isNumPadKey(self) -> bool: ...
    def isPlainNumPad(self) -> bool: ...
    def removeNumPadModifier(self) -> None: ...
    def prettyPrint(self) -> str: ...
    def strip_mods(self, s: str) -> str: ...
    def toGuiChar(self) -> str: ...
    def toInsertableChar(self) -> str: ...
def isStroke(obj: Any) -> bool: ...
def isStrokeOrNone(obj: Any) -> bool: ...
class MatchBrackets:
    def __init__(self, c: Cmdr, p: Pos, language: str) -> None: ...
    def is_regex(self, s: str, i: int) -> bool: ...
    def scan_regex(self, s: str, i: int) -> int: ...
    def scan_string(self, s: str, i: int) -> int: ...
    def expand_range(self,
        s: str,
        left: int,
        right: int,
        max_right: int,
        expand: bool=False,
    ) -> Tuple[Any, Any, Any, Any]: ...
    def find_matching_bracket(self, ch1: str, s: str, i: int) -> Any: ...
    def scan(self, ch1: str, target: str, s: str, i: int) -> Optional[int]: ...
    def scan_comment(self, s: str, i: int) -> Optional[int]: ...
    def starts_comment(self, s: str, i: int) -> bool: ...
    def scan_back(self, ch1: str, target: str, s: str, i: int) -> Optional[int]: ...
    def back_scan_comment(self, s: str, i: int) -> int: ...
    def ends_comment(self, s: str, i: int) -> bool: ...
    def oops(self, s: str) -> None: ...
    def run(self) -> None: ...
class PosList(list):
    def __init__(self, c: Cmdr, aList: List[Cmdr]=None) -> None: ...
    def dump(self, sort: bool=False, verbose: bool=False) -> str: ...
    def select(self, pat: str, regex: bool=False, removeClones: bool=True) -> "PosList": ...
    def removeClones(self, aList: List[Pos]) -> List[Pos]: ...
class ReadLinesClass:
    def __init__(self, s: str) -> None: ...
    def next(self) -> None: ...
class RedirectClass:
    def __init__(self) -> None: ...
    def isRedirected(self) -> bool: ...
    def flush(self, *args: Any) -> None: ...
    def rawPrint(self, s: str) -> None: ...
    def redirect(self, stdout: bool=True) -> None: ...
    def undirect(self, stdout: bool=True) -> None: ...
    def write(self, s: str) -> None: ...
def redirectStderr() -> None: ...
def redirectStdout() -> None: ...
def restoreStderr() -> None: ...
def restoreStdout() -> None: ...
def stdErrIsRedirected() -> bool: ...
def stdOutIsRedirected() -> bool: ...
def rawPrint(s: str) -> None: ...
class SherlockTracer:
    def __init__(
        self,
        patterns: List[Any],
        dots: bool=True,
        show_args: bool=True,
        show_return: bool=True,
        verbose: bool=True,
    ): ...
    def __call__(self, frame: Any, event: Any, arg: Any) -> Any: ...
    def bad_pattern(self, pattern: Any) -> None: ...
    def check_pattern(self, pattern: str) -> bool: ...
    def dispatch(self, frame: Any, event: Any, arg: Any) -> Any: ...
    def do_call(self, frame: Any, unused_arg: Any) -> None: ...
    def get_args(self, frame: Any) -> str: ...
    def do_line(self, frame: Any, arg: Any) -> None: ...
    def do_return(self, frame: Any, arg: Any) -> None: ...
    def format_ret(self, arg: Any) -> str: ...
    def fn_is_enabled(self, func: Any, patterns: List[str]) -> bool: ...
    #    def ignore_function() -> None: ...
    def get_full_name(self, locals_: Any, name: str) -> str: ...
    def is_enabled(self,
        file_name: str,
        function_name: str,
        patterns: List[str]=None,
    ) -> bool: ...
    #    def ignore_file() -> None: ...
    #    def ignore_function() -> None: ...
    def print_stats(self, patterns: List[str]=None) -> None: ...
    def run(self, frame: Any=None) -> None: ...
    def push(self, patterns: List[str]) -> None: ...
    def pop(self) -> None: ...
    def set_patterns(self, patterns: List[str]) -> None: ...
    def show(self, item: Any) -> str: ...
    def stop(self) -> None: ...
class TkIDDialog(EmergencyDialog):
    def __init__(self) -> None: ...
    def onKey(self, event: Any) -> None: ...
    def createTopFrame(self) -> None: ...
    def okButton(self) -> None: ...
class Tracer:
    def __init__(self, limit: int=0, trace: bool=False, verbose: bool=False) -> None: ...
    def computeName(self, frame: Any) -> str: ...
    def report(self) -> None: ...
    def stop(self) -> None: ...
    def tracer(self, frame: Any, event: Any, arg: Any) -> Optional[Callable]: ...
    def updateStats(self, name: str) -> None: ...
def startTracer(limit: int=0, trace: bool=False, verbose: bool=False) -> Callable: ...
class NullObject:
    def __init__(self, ivars: Union[str,List[str]]=None, *args: Any, **kwargs: Any) -> None: ...
    def __call__(self, *args: Any, **keys: Any) -> "NullObject": ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def __delattr__(self, attr: str) -> None: ...
    def __getattr__(self, attr: str) -> Any: ...
    def __setattr__(self, attr: str, val: Any) -> None: ...
    def __bool__(self) -> bool: ...
    def __contains__(self, item: Any) -> bool: ...
    def __getitem__(self, key: str) -> None: ...
    def __setitem__(self, key: str, val: Any) -> None: ...
    def __iter__(self) -> "NullObject": ...
    def __len__(self) -> int: ...
    def __next__(self) -> None: ...
class TracingNullObject:
    def __init__(self, tag: str, ivars: Union[str,List[str]]=None, *args: Any, **kwargs: Any) -> None: ...
    def __call__(self, *args: Any, **kwargs: Any) -> "TracingNullObject": ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def __delattr__(self, attr: str) -> None: ...
    def __getattr__(self, attr: str) -> "TracingNullObject": ...
    def __setattr__(self, attr: str, val: Any) -> None: ...
    def __bool__(self) -> bool: ...
    def __contains__(self, item: Any) -> bool: ...
    def __getitem__(self, key: str) -> None: ...
    def __iter__(self) -> "TracingNullObject": ...
    def __len__(self) -> int: ...
    def __next__(self) -> None: ...
    def __setitem__(self, key: str, val: Any) -> None: ...
def null_object_print_attr(id_: int, attr: str) -> None: ...
def null_object_print(id_: int, kind: Any, *args: Any) -> None: ...
class TypedDict:
    def __init__(self, name: str, keyType: Any, valType: Any): ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...
    def __setitem__(self, key: Any, val: Any) -> None: ...
    def add_to_list(self, key: Any, val: Any) -> None: ...
    def _checkKeyType(self, key: str) -> None: ...
    def _checkValType(self, val: Any) -> None: ...
    def _reportTypeError(self, obj: Any, objType: Any) -> str: ...
    def copy(self, name: str=None) -> Any: ...
    def get(self, key: Any, default: Any=None) -> Any: ...
    def items(self) -> Any: ...
    def keys(self) -> Any: ...
    def values(self) -> Any: ...
    def get_setting(self, key: str) -> Any: ...
    def get_string_setting(self, key: str) -> Optional[str]: ...
    def name(self) -> str: ...
    def setName(self, name: str) -> None: ...
    def update(self, d: Dict[Any, Any]) -> None: ...
class UiTypeException(Exception): ...
def assertUi(uitype: str) -> None: ...
class TestLeoGlobals(unittest.TestCase):
    def test_comment_delims_from_extension(self) -> None: ...
    def test_is_sentinel(self) -> None: ...
def isTextWidget(w: Any) -> bool: ...
def isTextWrapper(w: Any) -> bool: ...
def alert(message: str, c: Cmdr=None) -> None: ...
def assert_is(obj: Any, list_or_class: Any, warn: bool=True) -> bool: ...
def _assert(condition: str, show_callers: bool=True) -> bool: ...
def callers(n: int=4, count: int=0, excludeCaller: bool=True, verbose: bool=False) -> str: ...
def _callerName(n: int, verbose: bool=False) -> str: ...
def caller(i: int=1) -> str: ...
def dump(s: str) -> str: ...
def oldDump(s: str) -> str: ...
def dump_encoded_string(encoding: str, s: str) -> None: ...
def module_date(mod: Any, format: str=None) -> str: ...
def plugin_date(plugin_mod: Any, format: str=None) -> str: ...
def file_date(theFile: Any, format: str=None) -> str: ...
def get_line(s: str, i: int) -> str: ...
def get_line_after(s: str, i: int) -> str: ...
def getIvarsDict(obj: Any) -> Dict[str, Any]: ...
def checkUnchangedIvars(
    obj: Any,
    d: Dict[str, Any],
    exceptions: Sequence[str]=None,
) -> bool: ...
def pause(s: str) -> None: ...
def pdb(message: str='') -> None: ...
def dictToString(d: Dict[str, Any], indent: str='', tag: str=None) -> str: ...
def listToString(obj: Any, indent: str='', tag: str=None) -> str: ...
def objToString(obj: Any, indent: str='', printCaller: bool=False, tag: str=None) -> str: ...
def run_pylint(fn: Any, rc: Any,
    dots: bool=True,  # Show level dots in Sherlock traces.
    patterns: Any=None,  # List of Sherlock trace patterns.
    sherlock: bool=False,  # Enable Sherlock tracing.
    show_return: bool=True,  # Show returns in Sherlock traces.
    stats_patterns: Any=None,  # Patterns for Sherlock statistics.
    verbose: bool=True,  # Show filenames in Sherlock traces.
) -> None: ...
def sleep(n: float) -> None: ...
def printObj(obj: Any, indent: str='', printCaller: bool=False, tag: str=None) -> None: ...
def tupleToString(obj: Any, indent: str='', tag: str=None) -> str: ...
def clearAllIvars(o: Any) -> None: ...
def enable_gc_debug() -> None: ...
def printGc() -> None: ...
def printGcObjects() -> int: ...
def printGcRefs() -> None: ...
def printGcSummary() -> None: ...
def printTimes(times: List[float]) -> None: ...
def clearStats() -> None: ...
def printStats(event: Any=None, name: str=None) -> None: ...
def stat(name: str=None) -> None: ...
def getTime() -> float: ...
def esDiffTime(message: str, start: float) -> float: ...
def printDiffTime(message: str, start: float) -> float: ...
def timeSince(start: float) -> str: ...
def comment_delims_from_extension(filename: str) -> Tuple[str, str, str]: ...
def findAllValidLanguageDirectives(p: Pos) -> List[str]: ...
def findTabWidthDirectives(c: Cmdr, p: Pos) -> Optional[str]: ...
def findFirstValidAtLanguageDirective(p: Pos) -> Optional[str]: ...
def findLanguageDirectives(c: Cmdr, p: Pos) -> Optional[str]: ...
#    def find_language(p_or_v): ...
def findReference(name: str, root: Pos) -> Optional[Pos]: ...
def get_directives_dict(p: Pos, root: Pos=None) -> Dict[str, str]: ...
def get_directives_dict_list(p: Pos) -> List[Dict[Any, Any]]: ...
def getLanguageFromAncestorAtFileNode(p: Pos) -> Optional[str]: ...
#    def find_language(p: Pos) -> Optional[str]: ...
def getLanguageAtPosition(c: Cmdr, p: Pos) -> str: ...
def getOutputNewline(c: Cmdr=None, name: str=None) -> str: ...
def inAtNosearch(p: Pos) -> bool: ...
def isDirective(s: str) -> bool: ...
def isValidLanguage(language: str) -> bool: ...
def scanAtCommentAndAtLanguageDirectives(aList: List[Any]) -> Optional[Dict[str, Any]]: ...
def scanAtEncodingDirectives(aList: List[Any]) -> Optional[str]: ...
def scanAtHeaderDirectives(aList: List[Any]) -> None: ...
def scanAtLineendingDirectives(aList: List[Any]) -> Optional[str]: ...
def scanAtPagewidthDirectives(aList: List[Any], issue_error_flag: bool=False) -> Optional[int]: ...
def scanAtPathDirectives(c: Cmdr, aList: List[Any]) -> str: ...
def scanAllAtPathDirectives(c: Cmdr, p: Pos) -> str: ...
def scanAtTabwidthDirectives(aList: List[Any], issue_error_flag: bool=False) -> Optional[int]: ...
def scanAllAtTabWidthDirectives(c: Cmdr, p: Pos) -> Optional[int]: ...
def scanAtWrapDirectives(aList: List[Any], issue_error_flag: bool=False) -> Optional[bool]: ...
def scanAllAtWrapDirectives(c: Cmdr, p: Pos) -> Optional[Any]: ...
def scanForAtIgnore(c: Cmdr, p: Pos) -> bool: ...
def scanForAtLanguage(c: Cmdr, p: Pos) -> str: ...
def scanForAtSettings(p: Pos) -> bool: ...
def set_delims_from_language(language: str) -> Tuple[Any, Any, Any]: ...
def set_delims_from_string(s: str) -> Tuple[Optional[str], Optional[str], Optional[str]]: ...
def set_language(s: str, i: int, issue_errors_flag: bool=False) -> Tuple[Optional[str],Optional[str],Optional[str],Optional[str]]: ...
def stripPathCruft(path: str) -> str: ...
def update_directives_pat() -> None: ...
def chdir(path: str) -> None: ...
def computeGlobalConfigDir() -> str: ...
def computeHomeDir() -> str: ...
def computeLeoDir() -> str: ...
def computeLoadDir() -> str: ...
def computeMachineName() -> str: ...
def computeStandardDirectories() -> str: ...
def computeWindowTitle(fileName: str) -> str: ...
def create_temp_file(textMode: bool=False) -> Tuple[Any, str]: ...
def createHiddenCommander(fn: str) -> Optional[Cmdr]: ...
def defaultLeoFileExtension(c: Cmdr=None) -> str: ...
def ensure_extension(name: str, ext: str) -> str: ...
def fullPath(c: Cmdr, p: Pos, simulate: bool=False) -> str: ...
def get_files_in_directory(directory: str, kinds: Any=None, recursive: bool=True) -> List[Any]: ...
def getBaseDirectory(c: Cmdr) -> str: ...
def getEncodingAt(p: Pos, s: str=None) -> str: ...
def guessExternalEditor(c: Cmdr=None) -> Optional[str]: ...
def init_dialog_folder(c: Cmdr, p: Pos, use_at_path: bool=True) -> str: ...
def is_binary_file(f: Any) -> bool: ...
def is_binary_external_file(fileName: str) -> bool: ...
def is_binary_string(s: str) -> bool: ...
def is_sentinel(line: str, delims: Sequence) -> bool: ...
def makeAllNonExistentDirectories(theDir: str) -> Optional[str]: ...
def makePathRelativeTo(fullPath: str, basePath: str) -> str: ...
def openWithFileName(fileName: str, old_c: Cmdr=None, gui: str=None) -> Cmdr: ...
def readFileIntoEncodedString(fn: str, silent: bool=False) -> Optional[bytes]: ...
def readFileIntoString(fileName: str,
    encoding: str='utf-8',  # BOM may override this.
    kind: str=None,  # @file, @edit, ...
    verbose: bool=True,
) -> Tuple[Any, Any]: ...
def readFileIntoUnicodeString(fn: str, encoding: str=None, silent: bool=False) -> Optional[str]: ...
def readlineForceUnixNewline(f: Any, fileName: str=None) -> str: ...
def sanitize_filename(s: str) -> str: ...
def setGlobalOpenDir(fileName: str) -> None: ...
def shortFileName(fileName:str, n: Any=None) -> str: ...
def splitLongFileName(fn: str, limit: int=40) -> str: ...
def writeFile(contents: str, encoding: str, fileName: str) -> bool: ...
def find_word(s: str, word: str, i: int=0) -> int: ...
def findRootsWithPredicate(c: Cmdr, root: Pos, predicate: Any=None) -> List[Pos]: ...
#        def predicate(p: Pos) -> bool: ...
def recursiveUNLSearch(
    unlList: List[str], c: Cmdr, depth: int=0, p: Pos=None, maxdepth: int=0, maxp: Pos=None,
    soft_idx: bool=False, hard_idx: bool=False) -> Tuple[bool, Any, Any]: ...
#    def moveToP(c: Cmdr, p: Pos, unlList: List[str]) -> None: ...
def recursiveUNLFind(unlList: List[Any], c: Cmdr, depth: int=0, p: Pos=None, maxdepth: int=0, maxp: Pos=None,
soft_idx: bool=False, hard_idx: bool=False) -> Tuple[bool, Any, Any]: ...
def recursiveUNLParts(text: str) -> Tuple: ...
def scanError(s: str) -> None: ...
def scanf(s: str, pat: str) -> List[str]: ...
def see_more_lines(s: str, ins: int, n: int=4) -> int: ...
def splitLines(s: str) -> List[str]: ...
def joinLines(aList: List[str]) -> str: ...
def skip_block_comment(s: str, i: int) -> int: ...
def skip_braces(s: str, i: int) -> int: ...
def skip_parens(s: str, i: int) -> int: ...
def skip_pascal_begin_end(s: str, i: int) -> int: ...
def skip_pascal_block_comment(s: str, i: int) -> int: ...
def skip_pascal_string(s: str, i: int) -> int: ...
def skip_heredoc_string(s: str, i: int) -> int: ...
def skip_pp_directive(s: str, i: int) -> int: ...
def skip_pp_if(s: str, i: int) -> Tuple[int, int]: ...
def skip_pp_part(s: str, i: int) -> Tuple[int, int]: ...
def skip_to_semicolon(s: str, i: int) -> int: ...
def skip_typedef(s: str, i: int) -> int: ...
def escaped(s: str, i: int) -> bool: ...
def find_line_start(s: str, i: int) -> int: ...
def find_on_line(s: str, i: int, pattern: str) -> int: ...
def is_special(s: str, directive: str) -> Tuple[bool, int]: ...
def is_c_id(ch: str) -> bool: ...
def is_nl(s: str, i: int) -> bool: ...
def is_ws(ch: str) -> bool: ...
def is_ws_or_nl(s: str, i: int) -> bool: ...
def match(s: str, i: int, pattern: str) -> bool: ...
def match_c_word(s: str, i: int, name: str) -> bool: ...
def match_ignoring_case(s1: str, s2:str) -> bool: ...
def match_word(s: str, i: int, pattern: str) -> bool: ...
def match_words(s: str, i: int, patterns: Sequence[str]) -> bool: ...
def skip_blank_lines(s: str, i: int) -> int: ...
def skip_c_id(s: str, i: int) -> int: ...
def skip_id(s: str, i: int, chars: Any=None) -> int: ...
def skip_line(s: str, i: int) -> int: ...
def skip_to_end_of_line(s: str, i: int) -> int: ...
def skip_to_start_of_line(s: str, i: int) -> int: ...
def skip_long(s: str, i: int) -> Tuple[int, Optional[int]]: ...
def skip_nl(s: str, i: int) -> int: ...
def skip_non_ws(s: str, i: int) -> int: ...
def skip_pascal_braces(s: str, i: int) -> int: ...
def skip_python_string(s: str, i: int) -> int: ...
def skip_string(s: str, i: int) -> int: ...
def skip_to_char(s: str, i: int, ch: str) -> Tuple[int, str]: ...
def skip_ws(s: str, i: int) -> int: ...
def skip_ws_and_nl(s: str, i: int) -> int: ...
def backupGitIssues(c: Cmdr, base_url: str=None) -> None: ...
def execGitCommand(command: str, directory: str=None) -> List[str]: ...
def getGitIssues(c: Cmdr,
    base_url: str=None, label_list: List[Any]=None, milestone: str=None,
    state: Any=None,  # in (None, 'closed', 'open')
) -> None: ...
class GitIssueController:
    def backup_issues(self,
        base_url: str,
        c: Cmdr,
        label_list: List[Any],
        root: Pos,
        state: str=None,
    ) -> None: ...
    def get_all_issues(self,
        label_list: List[str],
        root: Pos,
        state: str,
        limit: int=100,
    ) -> None: ...
    def get_issues(self, base_url: str, label_list: List[Any], milestone: Any, root: Pos, state: str) -> None: ...
    def get_one_issue(self, label: str, state: str, limit: int=20) -> None: ...
    def get_one_page(self, label: str, page: Any, r: Any, root: Pos) -> Tuple[bool, int]: ...
    def print_header(self, r: Any) -> None: ...
def getGitVersion(directory: str=None) -> Tuple[Any, Any, Any]: ...
#    def find(kind: str) -> str: ...
def gitBranchName(path: str=None) -> str: ...
def gitCommitNumber(path: str=None) -> str: ...
def gitInfoForFile(filename: str) -> Tuple[str, str]: ...
def gitInfoForOutline(c: Cmdr) -> Tuple[str, str]: ...
def gitDescribe(path: str=None) -> Tuple[str, str, str]: ...
def gitHeadPath(path_s: str) -> Optional[str]: ...
def gitInfo(path: str=None) -> Tuple[str, str]: ...
def dummy_act_on_node(c: Cmdr, p: Pos, event: Any) -> None: ...
def doHook(tag: str, *args: Any, **keywords: Any) -> Any: ...
def loadOnePlugin(pluginName: str, verbose: bool=False) -> bool: ...
def registerExclusiveHandler(tags: Union[str, Sequence[str]], fn: Callable) -> bool: ...
def registerHandler(tags: Union[str, Sequence[str]], fn: Callable) -> bool: ...
def plugin_signon(module_name: str, verbose: bool=False) -> bool: ...
def unloadOnePlugin(moduleOrFileName: str, verbose: bool=False) -> bool: ...
def unregisterHandler(tags: Union[str, Sequence[str]], fn: Callable) -> bool: ...
def getHandlersForTag(tags: List[Any]) -> bool: ...
def getLoadedPlugins() -> bool: ...
def getPluginModule(moduleName: str) -> bool: ...
def pluginIsLoaded(fn: str) -> bool: ...
def disableIdleTimeHook() -> None: ...
def enableIdleTimeHook(*args: Any, **keys: Any) -> None: ...
def IdleTime(handler: Callable, delay: int=500, tag: str=None) -> Any: ...
def idleTimeHookHandler(timer: Callable) -> None: ...
def cantImport(moduleName: str, pluginName: str=None, verbose: bool=True) -> None: ...
def import_module(name: str, package: Any=None) -> Any: ...
def convertPythonIndexToRowCol(s: str, i: int) -> Tuple[int, int]: ...
def convertRowColToPythonIndex(s: str, row: int, col: int, lines: Any=None) -> int: ...
def getWord(s: str, i: int) -> Tuple[int, int]: ...
def getLine(s: str, i: int) -> Tuple[int, int]: ...
def toPythonIndex(s: str, index: int) -> int: ...
def flatten_list(obj: Any) -> Any: ...
def join_list(aList: List[Any], indent: str='', leading:str='', sep: str='', trailing: str='') -> Any: ...
def list_to_string(obj: Any) -> str: ...
def isascii(s: str) -> bool: ...
def angleBrackets(s: str) -> str: ...
def ensureLeadingNewlines(s: str, n: int) -> str: ...
def ensureTrailingNewlines(s: str, n: int) -> str: ...
def longestCommonPrefix(s1: str, s2: str) -> str: ...
def itemsMatchingPrefixInList(s: str, aList: List[str], matchEmptyPrefix: bool=False) -> Tuple[List[Any], str]: ...
def removeLeading(s: str, chars: str) -> str: ...
def removeTrailing(s: str, chars: str) -> str: ...
def stripBrackets(s: str) -> str: ...
def unCamel(s: str) -> List[str]: ...
def checkUnicode(s: str, encoding: str=None) -> str: ...
def getPythonEncodingFromString(s: str) -> Optional[str]: ...
def isBytes(s: str) -> bool: ...
def isCallable(obj: Any) -> bool: ...
def isInt(obj: Any) -> bool: ...
def isList(s: str) -> bool: ...
def isString(s: str) -> bool: ...
def isUnicode(s: str) -> bool: ...
def isValidEncoding(encoding: str) -> bool: ...
def isWordChar(ch: str) -> bool: ...
def isWordChar1(ch: str) -> bool: ...
def stripBOM(s: str) -> Tuple[Optional[str], str]: ...
def toEncodedString(s: str, encoding: str='utf-8', reportErrors: bool=False) -> bytes: ...
def toUnicode(s: Any, encoding: Optional[str]=None, reportErrors: bool=False) -> str: ...
def u(s: str) -> str: ...
def computeLeadingWhitespace(width: int, tab_width: int) -> str: ...
def computeLeadingWhitespaceWidth(s: str, tab_width: int) -> int: ...
def computeWidth(s: str, tab_width: int) -> int: ...
def adjustTripleString(s: str, tab_width: int) -> str: ...
def removeExtraLws(s: str, tab_width: int) -> str: ...
def wrap_lines(lines: List[str], pageWidth: int, firstLineWidth: int=None) -> List[str]: ...
def get_leading_ws(s: str) -> str: ...
def optimizeLeadingWhitespace(line: str, tab_width: int) -> str: ...
def regularizeTrailingNewlines(s: str, kind: str) -> None: ...
def removeBlankLines(s: str) -> str: ...
def removeLeadingBlankLines(s: str) -> str: ...
def removeLeadingWhitespace(s: str, first_ws: int, tab_width: int) -> str: ...
def removeTrailingWs(s: str) -> str: ...
def skip_leading_ws(s: str, i: int, ws: int, tab_width: int) -> int: ...
def skip_leading_ws_with_indent(s: str, i: int, tab_width: int) -> Tuple[int, int]: ...
def stripBlankLines(s: str) -> str: ...
def doKeywordArgs(keys: Any, d: Any=None) -> Dict[str, Any]: ...
def ecnl(tabName: str='Log') -> None: ...
def ecnls(n: int, tabName: str='Log') -> None: ...
def enl(tabName: str='Log') -> None: ...
def blue(*args: Any, **keys: Any) -> None: ...
def error(*args: Any, **keys: Any) -> None: ...
def note(*args: Any, **keys: Any) -> None: ...
def red(*args: Any, **keys: Any) -> None: ...
def warning(*args: Any, **keys: Any) -> None: ...
def es(*args: Any, **keys: Any) -> None: ...
def es_clickable_link(c: Cmdr, p: Pos, line_number:int , message: str) -> None: ...
def es_debug(*args: Any, **keys: Any) -> None: ...
def es_dump(s: str, n: int=30, title: str=None) -> None: ...
def es_error(*args: Any, **keys: Any) -> None: ...
def es_print_error(*args: Any, **keys: Any) -> None: ...
def es_event_exception(eventName: str, full: bool=False) -> None: ...
def es_exception(full: bool=True, c: Cmdr=None, color: str="red") -> Tuple[Optional[str], int]: ...
def es_exception_type(c: Cmdr=None, color: str="red") -> None: ...
def es_print(*args: Any, **keys: Any) -> None: ...
def print_exception(full: bool=True, c: Cmdr=None, flush: bool=False, color: str="red") -> Tuple[Optional[str], int]: ...
def es_trace(*args: Any, **keys: Any) -> None: ...
def getLastTracebackFileAndLineNumber() -> Tuple[str, int]: ...
def goto_last_exception(c: Cmdr) -> None: ...
def internalError(*args: Any) -> None: ...
def log_to_file(s: str, fn: str=None) -> None: ...
def pr(*args: Any, **keys: Any) -> None: ...
def prettyPrintType(obj: Any) -> str: ...
def print_bindings(name: str, window: Any) -> None: ...
def printEntireTree(c: Cmdr, tag: str='') -> None: ...
def printGlobals(message: str=None) -> None: ...
def printLeoModules(message: str=None) -> None: ...
def printStack() -> None: ...
def trace(*args: Any, **keys: Any) -> None: ...
def translateArgs(args: Iterable[Any], d: Dict[str, Any]) -> str: ...
def translateString(s: str) -> str: ...
def actualColor(color: Any) -> str: ...
def CheckVersion(s1: str, s2: str, condition: str=">=", stringCompare: bool=None, delimiter: str='.', trace: bool=False) -> Any: ...
def CheckVersionToInt(s: str) -> int: ...
def choose(cond: bool, a: Any, b: Any) -> Any: ...
def cls(event: Any=None) -> None: ...
def createScratchCommander(fileName: str=None) -> None: ...
def funcToMethod(f: Any, theClass: Any, name: str=None) -> None: ...
def init_zodb(pathToZodbStorage: str, verbose: bool=True) -> Any: ...
def input_(message: str='', c: Cmdr=None) -> str: ...
def isMacOS() -> bool: ...
def issueSecurityWarning(setting: str) -> None: ...
def makeDict(**keys: Any) -> Any: ...
def pep8_class_name(s: str) -> str: ...
def plural(obj: Any) -> str: ...
def truncate(s: str, n: int) -> str: ...
def windows() -> Optional[List[Any]]: ...
def glob_glob(pattern: str) -> List[str]: ...
def os_path_abspath(path: str) -> str: ...
def os_path_basename(path: str) -> str: ...
def os_path_dirname(path: str) -> str: ...
def os_path_exists(path: str) -> bool: ...
def os_path_expandExpression(s: str, **keys: Any) -> str: ...
def os_path_expanduser(path: str) -> str: ...
def os_path_finalize(path: str) -> str: ...
def os_path_finalize_join(*args: Any, **keys: Any) -> str: ...
def os_path_getmtime(path: str) -> Any: ...
def os_path_getsize(path: str) -> int: ...
def os_path_isabs(path: str) -> bool: ...
def os_path_isdir(path: str) -> bool: ...
def os_path_isfile(path: str) -> bool: ...
def os_path_join(*args: Any, **keys: Any) -> str: ...
def os_path_normcase(path: str) -> str: ...
def os_path_normpath(path: str) -> str: ...
def os_path_normslashes(path: str) -> str: ...
def os_path_realpath(path: str) -> str: ...
def os_path_split(path: str) -> Tuple[str, str]: ...
def os_path_splitext(path: str) -> Tuple[str, str]: ...
def os_startfile(fname: str) -> None: ...
#    def stderr2log(g: Any, ree: Any, fname: str) -> None: ...
#    def itPoll(fname: str, ree: Any, subPopen: Any, g: Any, ito: Any) -> None: ...
def createTopologyList(c: Cmdr, root: Pos=None, useHeadlines: bool=False) -> List[Any]: ...
def getDocString(s: str) -> str: ...
def getDocStringForFunction(func: Callable) -> str: ...
#    def name(func: Callable) -> str: ...
#    def get_defaults(func: Callable, i: int) -> Any: ...
def python_tokenize(s: str) -> List[Tuple[str, str, int]]: ...
def exec_file(path: str, d: Dict[str, Any], script: str=None) -> None: ...
def execute_shell_commands(commands: Union[str,List[str]], trace: bool=False) -> None: ...
#             def proc_poller(timer, proc=proc): ...
def execute_shell_commands_with_options(
    base_dir: str=None, c: Cmdr=None, command_setting: str=None,
    commands: str=None, path_setting: str=None, trace: bool=False, warning: str=None
) -> None: ...
def computeBaseDir(c: Cmdr, base_dir: str, path_setting: str, trace: bool=False) -> Optional[str]: ...
def computeCommands(c: Cmdr, commands: List[str], command_setting: str, trace: bool=False) -> List[str]: ...
def executeFile(filename: str, options: str='') -> None: ...
#    def subprocess_wrapper(cmdlst): ...
def findNodeAnywhere(c: Cmdr, headline: str, exact: bool=True) -> Optional[Pos]: ...
def findNodeByPath(c: Cmdr, path: str) -> Optional[Pos]: ...
def findNodeInChildren(c: Cmdr, p: Pos, headline: str, exact: bool=True) -> Optional[Pos]: ...
def findNodeInTree(c: Cmdr, p: Pos, headline: str, exact: bool=True) -> Optional[Pos]: ...
def findTopLevelNode(c: Cmdr, headline: str, exact: bool=True) -> Optional[Pos]: ...
def getScript(c: Cmdr, p: Pos, useSelectedText: bool=True, forcePythonSentinels: bool=True, useSentinels: bool=True) -> str: ...
def composeScript(c: Cmdr, p: Pos, s: str, forcePythonSentinels: bool=True, useSentinels: bool=True) -> str: ...
def extractExecutableString(c: Cmdr, p: Pos, s: str) -> str: ...
def handleScriptException(c: Cmdr, p: Pos, script: str, script1: str) -> None: ...
def insertCodingLine(encoding: str, script: str) -> str: ...
def findTestScript(c: Cmdr, h: str, where: Pos=None, warn: bool=True) -> Optional[str]: ...
def getTestVars() -> Tuple[Cmdr, Optional[Pos]]: ...
def run_unit_test_in_separate_process(command: str) -> None: ...
def toEncodedStringWithErrorCode(s: Union[bytes, str], encoding: str, reportErrors: bool=False) -> Tuple[bytes, bool]: ...
def toUnicodeWithErrorCode(s: Union[bytes, str], encoding: str, reportErrors: bool=False) -> Tuple[str, bool]: ...
def unquoteUrl(url: str) -> str: ...
def computeFileUrl(fn: str, c: Cmdr=None, p: Pos=None) -> str: ...
def getUrlFromNode(p: Pos) -> Optional[str]: ...
def handleUrl(url: str, c: Cmdr=None, p: Pos=None) -> None: ...
def handleUrlHelper(url: str, c: Cmdr, p: Pos) -> None: ...
def traceUrl(c: Cmdr, path: str, parsed: Any, url: str) -> None: ...
def handleUnl(unl: str, c: Cmdr) -> Optional[Cmdr]: ...
def isValidUrl(url: str) -> bool: ...
def openUrl(p: Pos) -> None: ...
def openUrlOnClick(event: Any, url: str=None) -> Optional[str]: ...
def openUrlHelper(event: Any, url: str=None) -> Optional[str]: ...
