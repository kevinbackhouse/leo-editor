# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20141012064706.18389: * @file leoAst.py
#@@first
# This file is part of Leo: https://leoeditor.com
# Leo's copyright notice is based on the MIT license: http://leoeditor.com/license.html
#@+<< docstring >>
#@+node:ekr.20200113081838.1: ** << docstring >> (leoAst.py)
"""
leoAst.py: This file does not depend on Leo in any way.

The classes in this file unify python's token-based and ast-based worlds by
creating two-way links between tokens in the token list and ast nodes in
the parse tree. For more details, see the "Overview" section below.


**Stand-alone operation**

usage:
    leoAst.py --help
    leoAst.py [--fstringify | --fstringify-diff | --orange | --orange-diff] PATHS
    leoAst.py --py-cov [ARGS]
    leoAst.py --pytest [ARGS]
    leoAst.py --unittest [ARGS]

examples:
    --py-cov "-f TestOrange"
    --pytest "-f TestOrange"
    --unittest TestOrange

positional arguments:
  PATHS              directory or list of files

optional arguments:
  -h, --help         show this help message and exit
  --fstringify       leonine fstringify
  --fstringify-diff  show fstringify diff
  --orange           leonine Black
  --orange-diff      show orange diff
  --py-cov           run pytest --cov on leoAst.py
  --pytest           run pytest on leoAst.py
  --unittest         run unittest on leoAst.py


**Overview**

leoAst.py unifies python's token-oriented and ast-oriented worlds.

leoAst.py defines classes that create two-way links between tokens
created by python's tokenize module and parse tree nodes created by
python's ast module:

The Token Order Generator (TOG) class quickly creates the following
links:

- An *ordered* children array from each ast node to its children.

- A parent link from each ast.node to its parent.

- Two-way links between tokens in the token list, a list of Token
  objects, and the ast nodes in the parse tree:

  - For each token, token.node contains the ast.node "responsible" for
    the token.

  - For each ast node, node.first_i and node.last_i are indices into
    the token list. These indices give the range of tokens that can be
    said to be "generated" by the ast node.

Once the TOG class has inserted parent/child links, the Token Order
Traverser (TOT) class traverses trees annotated with parent/child
links extremely quickly.


**Applicability and importance**

Many python developers will find asttokens meets all their needs.
asttokens is well documented and easy to use. Nevertheless, two-way
links are significant additions to python's tokenize and ast modules:

- Links from tokens to nodes are assigned to the nearest possible ast
  node, not the nearest statement, as in asttokens. Links can easily
  be reassigned, if desired.

- The TOG and TOT classes are intended to be the foundation of tools
  such as fstringify and black.

- The TOG class solves real problems, such as:
  https://stackoverflow.com/questions/16748029/

**Known bug**

This file has no known bugs *except* for Python version 3.8.

For Python 3.8, syncing tokens will fail for function call such as:

    f(1, x=2, *[3, 4], y=5)

that is, for calls where keywords appear before non-keyword args.

There are no plans to fix this bug. The workaround is to use Python version
3.9 or above.


**Figures of merit**

Simplicity: The code consists primarily of a set of generators, one
for every kind of ast node.

Speed: The TOG creates two-way links between tokens and ast nodes in
roughly the time taken by python's tokenize.tokenize and ast.parse
library methods. This is substantially faster than the asttokens,
black or fstringify tools. The TOT class traverses trees annotated
with parent/child links even more quickly.

Memory: The TOG class makes no significant demands on python's
resources. Generators add nothing to python's call stack.
TOG.node_stack is the only variable-length data. This stack resides in
python's heap, so its length is unimportant. In the worst case, it
might contain a few thousand entries. The TOT class uses no
variable-length data at all.

**Links**

Leo...
Ask for help:       https://groups.google.com/forum/#!forum/leo-editor
Report a bug:       https://github.com/leo-editor/leo-editor/issues
leoAst.py docs:     http://leoeditor.com/appendices.html#leoast-py

Other tools...
asttokens:          https://pypi.org/project/asttokens
black:              https://pypi.org/project/black/
fstringify:         https://pypi.org/project/fstringify/

Python modules...
tokenize.py:        https://docs.python.org/3/library/tokenize.html
ast.py              https://docs.python.org/3/library/ast.html

**Studying this file**

I strongly recommend that you use Leo when studying this code so that you
will see the file's intended outline structure.

Without Leo, you will see only special **sentinel comments** that create
Leo's outline structure. These comments have the form::

    `#@<comment-kind>:<user-id>.<timestamp>.<number>: <outline-level> <headline>`
"""
#@-<< docstring >>
#@+<< imports >>
#@+node:ekr.20200105054219.1: ** << imports >> (leoAst.py)
import argparse
import ast
import codecs
import difflib
import glob
import io
import os
import re
import sys
import textwrap
import tokenize
import traceback
from typing import List, Optional
#@-<< imports >>
v1, v2, junk1, junk2, junk3 = sys.version_info
py_version = (v1, v2)

# Async tokens exist only in Python 3.5 and 3.6.
# https://docs.python.org/3/library/token.html
has_async_tokens = (3, 5) <= py_version <= (3, 6)

# has_position_only_params = (v1, v2) >= (3, 8)
#@+others
#@+node:ekr.20191226175251.1: **  class LeoGlobals
#@@nosearch


class LeoGlobals:  # pragma: no cover
    """
    Simplified version of functions in leoGlobals.py.
    """

    total_time = 0.0  # For unit testing.

    #@+others
    #@+node:ekr.20191226175903.1: *3* LeoGlobals.callerName
    def callerName(self, n):
        """Get the function name from the call stack."""
        try:
            f1 = sys._getframe(n)
            code1 = f1.f_code
            return code1.co_name
        except Exception:
            return ''
    #@+node:ekr.20191226175426.1: *3* LeoGlobals.callers
    def callers(self, n=4):
        """
        Return a string containing a comma-separated list of the callers
        of the function that called g.callerList.
        """
        i, result = 2, []
        while True:
            s = self.callerName(n=i)
            if s:
                result.append(s)
            if not s or len(result) >= n:
                break
            i += 1
        return ','.join(reversed(result))
    #@+node:ekr.20191226190709.1: *3* leoGlobals.es_exception & helper
    def es_exception(self, full=True):
        typ, val, tb = sys.exc_info()
        for line in traceback.format_exception(typ, val, tb):
            print(line)
        fileName, n = self.getLastTracebackFileAndLineNumber()
        return fileName, n
    #@+node:ekr.20191226192030.1: *4* LeoGlobals.getLastTracebackFileAndLineNumber
    def getLastTracebackFileAndLineNumber(self):
        typ, val, tb = sys.exc_info()
        if typ == SyntaxError:
            # IndentationError is a subclass of SyntaxError.
            # SyntaxError *does* have 'filename' and 'lineno' attributes.
            return val.filename, val.lineno  # type:ignore
        #
        # Data is a list of tuples, one per stack entry.
        # The tuples have the form (filename, lineNumber, functionName, text).
        data = traceback.extract_tb(tb)
        item = data[-1]  # Get the item at the top of the stack.
        filename, n, functionName, text = item
        return filename, n
    #@+node:ekr.20200220065737.1: *3* LeoGlobals.objToString
    def objToString(self, obj, tag=None):
        """Simplified version of g.printObj."""
        result = []
        if tag:
            result.append(f"{tag}...")
        if isinstance(obj, str):
            obj = g.splitLines(obj)
        if isinstance(obj, list):
            result.append('[')
            for z in obj:
                result.append(f"  {z!r}")
            result.append(']')
        elif isinstance(obj, tuple):
            result.append('(')
            for z in obj:
                result.append(f"  {z!r}")
            result.append(')')
        else:
            result.append(repr(obj))
        result.append('')
        return '\n'.join(result)
    #@+node:ekr.20191226190425.1: *3* LeoGlobals.plural
    def plural(self, obj):
        """Return "s" or "" depending on n."""
        if isinstance(obj, (list, tuple, str)):
            n = len(obj)
        else:
            n = obj
        return '' if n == 1 else 's'
    #@+node:ekr.20191226175441.1: *3* LeoGlobals.printObj
    def printObj(self, obj, tag=None):
        """Simplified version of g.printObj."""
        print(self.objToString(obj, tag))
    #@+node:ekr.20191226190131.1: *3* LeoGlobals.splitLines
    def splitLines(self, s):
        """Split s into lines, preserving the number of lines and
        the endings of all lines, including the last line."""
        # g.stat()
        if s:
            return s.splitlines(True)
                # This is a Python string function!
        return []
    #@+node:ekr.20191226190844.1: *3* LeoGlobals.toEncodedString
    def toEncodedString(self, s, encoding='utf-8'):
        """Convert unicode string to an encoded string."""
        if not isinstance(s, str):
            return s
        try:
            s = s.encode(encoding, "strict")
        except UnicodeError:
            s = s.encode(encoding, "replace")
            print(f"toEncodedString: Error converting {s!r} to {encoding}")
        return s
    #@+node:ekr.20191226190006.1: *3* LeoGlobals.toUnicode
    def toUnicode(self, s, encoding='utf-8'):
        """Convert bytes to unicode if necessary."""
        tag = 'g.toUnicode'
        if isinstance(s, str):
            return s
        if not isinstance(s, bytes):
            print(f"{tag}: bad s: {s!r}")
            return ''
        b: bytes = s
        try:
            s2 = b.decode(encoding, 'strict')
        except(UnicodeDecodeError, UnicodeError):
            s2 = b.decode(encoding, 'replace')
            print(f"{tag}: unicode error. encoding: {encoding!r}, s2:\n{s2!r}")
            g.trace(g.callers())
        except Exception:
            g.es_exception()
            print(f"{tag}: unexpected error! encoding: {encoding!r}, s2:\n{s2!r}")
            g.trace(g.callers())
        return s2
    #@+node:ekr.20191226175436.1: *3* LeoGlobals.trace
    def trace(self, *args):
        """Print a tracing message."""
        # Compute the caller name.
        try:
            f1 = sys._getframe(1)
            code1 = f1.f_code
            name = code1.co_name
        except Exception:
            name = ''
        print(f"{name}: {' '.join(str(z) for z in args)}")
    #@+node:ekr.20191226190241.1: *3* LeoGlobals.truncate
    def truncate(self, s, n):
        """Return s truncated to n characters."""
        if len(s) <= n:
            return s
        s2 = s[: n - 3] + f"...({len(s)})"
        return s2 + '\n' if s.endswith('\n') else s2
    #@-others
#@+node:ekr.20200702114522.1: **  leoAst.py: top-level commands
#@+node:ekr.20200702114557.1: *3* command: fstringify_command
def fstringify_command(files):
    """
    Entry point for --fstringify.

    Fstringify the given file, overwriting the file.
    """
    for filename in files:  # pragma: no cover
        if os.path.exists(filename):
            print(f"fstringify {filename}")
            Fstringify().fstringify_file_silent(filename)
        else:
            print(f"file not found: {filename}")
#@+node:ekr.20200702121222.1: *3* command: fstringify_diff_command
def fstringify_diff_command(files):
    """
    Entry point for --fstringify-diff.

    Print the diff that would be produced by fstringify.
    """
    for filename in files:  # pragma: no cover
        if os.path.exists(filename):
            print(f"fstringify-diff {filename}")
            Fstringify().fstringify_file_diff(filename)
        else:
            print(f"file not found: {filename}")
#@+node:ekr.20200702115002.1: *3* command: orange_command
def orange_command(files):

    for filename in files:  # pragma: no cover
        if os.path.exists(filename):
            print(f"orange {filename}")
            Orange().beautify_file(filename)
        else:
            print(f"file not found: {filename}")
#@+node:ekr.20200702121315.1: *3* command: orange_diff_command
def orange_diff_command(files):

    for filename in files:  # pragma: no cover
        if os.path.exists(filename):
            print(f"orange-diff {filename}")
            Orange().beautify_file_diff(filename)
        else:
            print(f"file not found: {filename}")
#@+node:ekr.20160521104628.1: **  leoAst.py: top-level utils
if 1:  # pragma: no cover
    #@+others
    #@+node:ekr.20200702102239.1: *3* function: main (leoAst.py)
    def main():
        """Run commands specified by sys.argv."""
        description = textwrap.dedent("""\
            leo-editor/leo/unittests/core/test_leoAst.py contains unit tests (100% coverage).
        """)
        parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument('PATHS', nargs='*', help='directory or list of files')
        group = parser.add_mutually_exclusive_group(required=False)  # Don't require any args.
        add = group.add_argument
        add('--fstringify', dest='f', action='store_true', help='leonine fstringify')
        add('--fstringify-diff', dest='fd', action='store_true', help='show fstringify diff')
        add('--orange', dest='o', action='store_true', help='leonine Black')
        add('--orange-diff', dest='od', action='store_true', help='show orange diff')
        args = parser.parse_args()
        files = args.PATHS
        if len(files) == 1 and os.path.isdir(files[0]):
            files = glob.glob(f"{files[0]}{os.sep}*.py")
        if args.f:
            fstringify_command(files)
        if args.fd:
            fstringify_diff_command(files)
        if args.o:
            orange_command(files)
        if args.od:
            orange_diff_command(files)
    #@+node:ekr.20200107114409.1: *3* functions: reading & writing files
    #@+node:ekr.20200218071822.1: *4* function: regularize_nls
    def regularize_nls(s):
        """Regularize newlines within s."""
        return s.replace('\r\n', '\n').replace('\r', '\n')
    #@+node:ekr.20200106171502.1: *4* function: get_encoding_directive
    encoding_pattern = re.compile(r'^[ \t\f]*#.*?coding[:=][ \t]*([-_.a-zA-Z0-9]+)')
        # This is the pattern in PEP 263.

    def get_encoding_directive(bb):
        """
        Get the encoding from the encoding directive at the start of a file.

        bb: The bytes of the file.

        Returns the codec name, or 'UTF-8'.

        Adapted from pyzo. Copyright 2008 to 2020 by Almar Klein.
        """
        for line in bb.split(b'\n', 2)[:2]:
            # Try to make line a string
            try:
                line2 = line.decode('ASCII').strip()
            except Exception:
                continue
            # Does the line match the PEP 263 pattern?
            m = encoding_pattern.match(line2)
            if not m:
                continue
            # Is it a known encoding? Correct the name if it is.
            try:
                c = codecs.lookup(m.group(1))
                return c.name
            except Exception:
                pass
        return 'UTF-8'
    #@+node:ekr.20200103113417.1: *4* function: read_file
    def read_file(filename, encoding='utf-8'):
        """
        Return the contents of the file with the given name.
        Print an error message and return None on error.
        """
        tag = 'read_file'
        try:
            # Translate all newlines to '\n'.
            with open(filename, 'r', encoding=encoding) as f:
                s = f.read()
            return regularize_nls(s)
        except Exception:
            print(f"{tag}: can not read {filename}")
            return None
    #@+node:ekr.20200106173430.1: *4* function: read_file_with_encoding
    def read_file_with_encoding(filename):
        """
        Read the file with the given name,  returning (e, s), where:

        s is the string, converted to unicode, or '' if there was an error.

        e is the encoding of s, computed in the following order:

        - The BOM encoding if the file starts with a BOM mark.
        - The encoding given in the # -*- coding: utf-8 -*- line.
        - The encoding given by the 'encoding' keyword arg.
        - 'utf-8'.
        """
        # First, read the file.
        tag = 'read_with_encoding'
        try:
            with open(filename, 'rb') as f:
                bb = f.read()
        except Exception:
            print(f"{tag}: can not read {filename}")
        if not bb:
            return 'UTF-8', ''
        # Look for the BOM.
        e, bb = strip_BOM(bb)
        if not e:
            # Python's encoding comments override everything else.
            e = get_encoding_directive(bb)
        s = g.toUnicode(bb, encoding=e)
        s = regularize_nls(s)
        return e, s
    #@+node:ekr.20200106174158.1: *4* function: strip_BOM
    def strip_BOM(bb):
        """
        bb must be the bytes contents of a file.

        If bb starts with a BOM (Byte Order Mark), return (e, bb2), where:

        - e is the encoding implied by the BOM.
        - bb2 is bb, stripped of the BOM.

        If there is no BOM, return (None, bb)
        """
        assert isinstance(bb, bytes), bb.__class__.__name__
        table = (
                        # Test longer bom's first.
            (4, 'utf-32', codecs.BOM_UTF32_BE),
            (4, 'utf-32', codecs.BOM_UTF32_LE),
            (3, 'utf-8', codecs.BOM_UTF8),
            (2, 'utf-16', codecs.BOM_UTF16_BE),
            (2, 'utf-16', codecs.BOM_UTF16_LE),
        )
        for n, e, bom in table:
            assert len(bom) == n
            if bom == bb[: len(bom)]:
                return e, bb[len(bom) :]
        return None, bb
    #@+node:ekr.20200103163100.1: *4* function: write_file
    def write_file(filename, s, encoding='utf-8'):
        """
        Write the string s to the file whose name is given.

        Handle all exeptions.

        Before calling this function, the caller should ensure
        that the file actually has been changed.
        """
        try:
            # Write the file with platform-dependent newlines.
            with open(filename, 'w', encoding=encoding) as f:
                f.write(s)
        except Exception as e:
            g.trace(f"Error writing {filename}\n{e}")
    #@+node:ekr.20200113154120.1: *3* functions: tokens
    #@+node:ekr.20191223093539.1: *4* function: find_anchor_token
    def find_anchor_token(node, global_token_list):
        """
        Return the anchor_token for node, a token such that token.node == node.

        The search starts at node, and then all the usual child nodes.
        """

        node1 = node

        def anchor_token(node):
            """Return the anchor token in node.token_list"""
            # Careful: some tokens in the token list may have been killed.
            for token in get_node_token_list(node, global_token_list):
                if is_ancestor(node1, token):
                    return token
            return None

        # This table only has to cover fields for ast.Nodes that
        # won't have any associated token.

        fields = (
                        # Common...
            'elt', 'elts', 'body', 'value',
                        # Less common...
            'dims', 'ifs', 'names', 's',
            'test', 'values', 'targets',
        )
        while node:
            # First, try the node itself.
            token = anchor_token(node)
            if token:
                return token
            # Second, try the most common nodes w/o token_lists:
            if isinstance(node, ast.Call):
                node = node.func
            elif isinstance(node, ast.Tuple):
                node = node.elts  # type:ignore
            # Finally, try all other nodes.
            else:
                # This will be used rarely.
                for field in fields:
                    node = getattr(node, field, None)
                    if node:
                        token = anchor_token(node)
                        if token:
                            return token
                else:
                    break
        return None
    #@+node:ekr.20191231160225.1: *4* function: find_paren_token (changed signature)
    def find_paren_token(i, global_token_list):
        """Return i of the next paren token, starting at tokens[i]."""
        while i < len(global_token_list):
            token = global_token_list[i]
            if token.kind == 'op' and token.value in '()':
                return i
            if is_significant_token(token):
                break
            i += 1
        return None
    #@+node:ekr.20200113110505.4: *4* function: get_node_tokens_list
    def get_node_token_list(node, global_tokens_list):
        """
        tokens_list must be the global tokens list.
        Return the tokens assigned to the node, or [].
        """
        i = getattr(node, 'first_i', None)
        j = getattr(node, 'last_i', None)
        return [] if i is None else global_tokens_list[i : j + 1]
    #@+node:ekr.20191124123830.1: *4* function: is_significant & is_significant_token
    def is_significant(kind, value):
        """
        Return True if (kind, value) represent a token that can be used for
        syncing generated tokens with the token list.
        """
        # Making 'endmarker' significant ensures that all tokens are synced.
        return (
            kind in ('async', 'await', 'endmarker', 'name', 'number', 'string') or
            kind == 'op' and value not in ',;()')

    def is_significant_token(token):
        """Return True if the given token is a syncronizing token"""
        return is_significant(token.kind, token.value)
    #@+node:ekr.20191224093336.1: *4* function: match_parens
    def match_parens(filename, i, j, tokens):
        """Match parens in tokens[i:j]. Return the new j."""
        if j >= len(tokens):
            return len(tokens)
        # Calculate paren level...
        level = 0
        for n in range(i, j + 1):
            token = tokens[n]
            if token.kind == 'op' and token.value == '(':
                level += 1
            if token.kind == 'op' and token.value == ')':
                if level == 0:
                    break
                level -= 1
        # Find matching ')' tokens *after* j.
        if level > 0:
            while level > 0 and j + 1 < len(tokens):
                token = tokens[j + 1]
                if token.kind == 'op' and token.value == ')':
                    level -= 1
                elif token.kind == 'op' and token.value == '(':
                    level += 1
                elif is_significant_token(token):
                    break
                j += 1
        if level != 0:  # pragma: no cover.
            line_n = tokens[i].line_number
            raise AssignLinksError(
                f"\n"
                f"Unmatched parens: level={level}\n"
                f"            file: {filename}\n"
                f"            line: {line_n}\n")
        return j
    #@+node:ekr.20191223053324.1: *4* function: tokens_for_node
    def tokens_for_node(filename, node, global_token_list):
        """Return the list of all tokens descending from node."""
        # Find any token descending from node.
        token = find_anchor_token(node, global_token_list)
        if not token:
            if 0:  # A good trace for debugging.
                print('')
                g.trace('===== no tokens', node.__class__.__name__)
            return []
        assert is_ancestor(node, token)
        # Scan backward.
        i = first_i = token.index
        while i >= 0:
            token2 = global_token_list[i - 1]
            if getattr(token2, 'node', None):
                if is_ancestor(node, token2):
                    first_i = i - 1
                else:
                    break
            i -= 1
        # Scan forward.
        j = last_j = token.index
        while j + 1 < len(global_token_list):
            token2 = global_token_list[j + 1]
            if getattr(token2, 'node', None):
                if is_ancestor(node, token2):
                    last_j = j + 1
                else:
                    break
            j += 1
        last_j = match_parens(filename, first_i, last_j, global_token_list)
        results = global_token_list[first_i : last_j + 1]
        return results
    #@+node:ekr.20200101030236.1: *4* function: tokens_to_string
    def tokens_to_string(tokens):
        """Return the string represented by the list of tokens."""
        if tokens is None:
            # This indicates an internal error.
            print('')
            g.trace('===== token list is None ===== ')
            print('')
            return ''
        return ''.join([z.to_string() for z in tokens])
    #@+node:ekr.20191231072039.1: *3* functions: utils...
    # General utility functions on tokens and nodes.
    #@+node:ekr.20191119085222.1: *4* function: obj_id
    def obj_id(obj):
        """Return the last four digits of id(obj), for dumps & traces."""
        return str(id(obj))[-4:]
    #@+node:ekr.20191231060700.1: *4* function: op_name
    #@@nobeautify

    # https://docs.python.org/3/library/ast.html

    _op_names = {
        # Binary operators.
        'Add': '+',
        'BitAnd': '&',
        'BitOr': '|',
        'BitXor': '^',
        'Div': '/',
        'FloorDiv': '//',
        'LShift': '<<',
        'MatMult': '@',  # Python 3.5.
        'Mod': '%',
        'Mult': '*',
        'Pow': '**',
        'RShift': '>>',
        'Sub': '-',
        # Boolean operators.
        'And': ' and ',
        'Or': ' or ',
        # Comparison operators
        'Eq': '==',
        'Gt': '>',
        'GtE': '>=',
        'In': ' in ',
        'Is': ' is ',
        'IsNot': ' is not ',
        'Lt': '<',
        'LtE': '<=',
        'NotEq': '!=',
        'NotIn': ' not in ',
        # Context operators.
        'AugLoad': '<AugLoad>',
        'AugStore': '<AugStore>',
        'Del': '<Del>',
        'Load': '<Load>',
        'Param': '<Param>',
        'Store': '<Store>',
        # Unary operators.
        'Invert': '~',
        'Not': ' not ',
        'UAdd': '+',
        'USub': '-',
    }

    def op_name(node):
        """Return the print name of an operator node."""
        class_name = node.__class__.__name__
        assert class_name in _op_names, repr(class_name)
        return _op_names[class_name].strip()
    #@+node:ekr.20200107114452.1: *3* node/token creators...
    #@+node:ekr.20200103082049.1: *4* function: make_tokens
    def make_tokens(contents):
        """
        Return a list (not a generator) of Token objects corresponding to the
        list of 5-tuples generated by tokenize.tokenize.

        Perform consistency checks and handle all exeptions.
        """

        def check(contents, tokens):
            result = tokens_to_string(tokens)
            ok = result == contents
            if not ok:
                print('\nRound-trip check FAILS')
                print('Contents...\n')
                g.printObj(contents)
                print('\nResult...\n')
                g.printObj(result)
            return ok

        try:
            five_tuples = tokenize.tokenize(
                io.BytesIO(contents.encode('utf-8')).readline)
        except Exception:
            print('make_tokens: exception in tokenize.tokenize')
            g.es_exception()
            return None
        tokens = Tokenizer().create_input_tokens(contents, five_tuples)
        assert check(contents, tokens)
        return tokens
    #@+node:ekr.20191027075648.1: *4* function: parse_ast
    def parse_ast(s):
        """
        Parse string s, catching & reporting all exceptions.
        Return the ast node, or None.
        """

        def oops(message):
            print('')
            print(f"parse_ast: {message}")
            g.printObj(s)
            print('')

        try:
            s1 = g.toEncodedString(s)
            tree = ast.parse(s1, filename='before', mode='exec')
            return tree
        except IndentationError:
            oops('Indentation Error')
        except SyntaxError:
            oops('Syntax Error')
        except Exception:
            oops('Unexpected Exception')
            g.es_exception()
        return None
    #@+node:ekr.20191231110051.1: *3* node/token dumpers...
    #@+node:ekr.20191027074436.1: *4* function: dump_ast
    def dump_ast(ast, tag='dump_ast'):
        """Utility to dump an ast tree."""
        g.printObj(AstDumper().dump_ast(ast), tag=tag)
    #@+node:ekr.20191228095945.4: *4* function: dump_contents
    def dump_contents(contents, tag='Contents'):
        print('')
        print(f"{tag}...\n")
        for i, z in enumerate(g.splitLines(contents)):
            print(f"{i+1:<3} ", z.rstrip())
        print('')
    #@+node:ekr.20191228095945.5: *4* function: dump_lines
    def dump_lines(tokens, tag='Token lines'):
        print('')
        print(f"{tag}...\n")
        for z in tokens:
            if z.line.strip():
                print(z.line.rstrip())
            else:
                print(repr(z.line))
        print('')
    #@+node:ekr.20191228095945.7: *4* function: dump_results
    def dump_results(tokens, tag='Results'):
        print('')
        print(f"{tag}...\n")
        print(tokens_to_string(tokens))
        print('')
    #@+node:ekr.20191228095945.8: *4* function: dump_tokens
    def dump_tokens(tokens, tag='Tokens'):
        print('')
        print(f"{tag}...\n")
        if not tokens:
            return
        print("Note: values shown are repr(value) *except* for 'string' tokens.")
        tokens[0].dump_header()
        for i, z in enumerate(tokens):
            # Confusing.
                # if (i % 20) == 0: z.dump_header()
            print(z.dump())
        print('')
    #@+node:ekr.20191228095945.9: *4* function: dump_tree
    def dump_tree(tokens, tree, tag='Tree'):
        print('')
        print(f"{tag}...\n")
        print(AstDumper().dump_tree(tokens, tree))
    #@+node:ekr.20200107040729.1: *4* function: show_diffs
    def show_diffs(s1, s2, filename=''):
        """Print diffs between strings s1 and s2."""
        lines = list(difflib.unified_diff(
            g.splitLines(s1),
            g.splitLines(s2),
            fromfile=f"Old {filename}",
            tofile=f"New {filename}",
        ))
        print('')
        tag = f"Diffs for {filename}" if filename else 'Diffs'
        g.printObj(lines, tag=tag)
    #@+node:ekr.20191223095408.1: *3* node/token nodes...
    # Functions that associate tokens with nodes.
    #@+node:ekr.20200120082031.1: *4* function: find_statement_node
    def find_statement_node(node):
        """
        Return the nearest statement node.
        Return None if node has only Module for a parent.
        """
        if isinstance(node, ast.Module):
            return None
        parent = node
        while parent:
            if is_statement_node(parent):
                return parent
            parent = parent.parent
        return None
    #@+node:ekr.20191223054300.1: *4* function: is_ancestor
    def is_ancestor(node, token):
        """Return True if node is an ancestor of token."""
        t_node = token.node
        if not t_node:
            assert token.kind == 'killed', repr(token)
            return False
        while t_node:
            if t_node == node:
                return True
            t_node = t_node.parent
        return False
    #@+node:ekr.20200120082300.1: *4* function: is_long_statement
    def is_long_statement(node):
        """
        Return True if node is an instance of a node that might be split into
        shorter lines.
        """
        return isinstance(node, (
            ast.Assign, ast.AnnAssign, ast.AsyncFor, ast.AsyncWith, ast.AugAssign,
            ast.Call, ast.Delete, ast.ExceptHandler, ast.For, ast.Global,
            ast.If, ast.Import, ast.ImportFrom,
            ast.Nonlocal, ast.Return, ast.While, ast.With, ast.Yield, ast.YieldFrom))
    #@+node:ekr.20200120110005.1: *4* function: is_statement_node
    def is_statement_node(node):
        """Return True if node is a top-level statement."""
        return is_long_statement(node) or isinstance(node, (
            ast.Break, ast.Continue, ast.Pass, ast.Try))
    #@+node:ekr.20191231082137.1: *4* function: nearest_common_ancestor
    def nearest_common_ancestor(node1, node2):
        """
        Return the nearest common ancestor node for the given nodes.

        The nodes must have parent links.
        """

        def parents(node):
            aList = []
            while node:
                aList.append(node)
                node = node.parent
            return list(reversed(aList))

        result = None
        parents1 = parents(node1)
        parents2 = parents(node2)
        while parents1 and parents2:
            parent1 = parents1.pop(0)
            parent2 = parents2.pop(0)
            if parent1 == parent2:
                result = parent1
            else:
                break
        return result
    #@+node:ekr.20191225061516.1: *3* node/token replacers...
    # Functions that replace tokens or nodes.
    #@+node:ekr.20191231162249.1: *4* function: add_token_to_token_list
    def add_token_to_token_list(token, node):
        """Insert token in the proper location of node.token_list."""
        if getattr(node, 'first_i', None) is None:
            node.first_i = node.last_i = token.index
        else:
            node.first_i = min(node.first_i, token.index)
            node.last_i = max(node.last_i, token.index)
    #@+node:ekr.20191225055616.1: *4* function: replace_node
    def replace_node(new_node, old_node):
        """Replace new_node by old_node in the parse tree."""
        parent = old_node.parent
        new_node.parent = parent
        new_node.node_index = old_node.node_index
        children = parent.children
        i = children.index(old_node)
        children[i] = new_node
        fields = getattr(old_node, '_fields', None)
        if fields:
            for field in fields:
                field = getattr(old_node, field)
                if field == old_node:
                    setattr(old_node, field, new_node)
                    break
    #@+node:ekr.20191225055626.1: *4* function: replace_token
    def replace_token(token, kind, value):
        """Replace kind and value of the given token."""
        if token.kind in ('endmarker', 'killed'):
            return
        token.kind = kind
        token.value = value
        token.node = None  # Should be filled later.
    #@-others
#@+node:ekr.20191027072910.1: ** Exception classes
class AssignLinksError(Exception):
    """Assigning links to ast nodes failed."""


class AstNotEqual(Exception):
    """The two given AST's are not equivalent."""


class FailFast(Exception):
    """Abort tests in TestRunner class."""
#@+node:ekr.20141012064706.18390: ** class AstDumper
class AstDumper:  # pragma: no cover
    """A class supporting various kinds of dumps of ast nodes."""
    #@+others
    #@+node:ekr.20191112033445.1: *3* dumper.dump_tree & helper
    def dump_tree(self, tokens, tree):
        """Briefly show a tree, properly indented."""
        self.tokens = tokens
        result = [self.show_header()]
        self.dump_tree_and_links_helper(tree, 0, result)
        return ''.join(result)
    #@+node:ekr.20191125035321.1: *4* dumper.dump_tree_and_links_helper
    def dump_tree_and_links_helper(self, node, level, result):
        """Return the list of lines in result."""
        if node is None:
            return
        # Let block.
        indent = ' ' * 2 * level
        children: List[ast.AST] = getattr(node, 'children', [])
        node_s = self.compute_node_string(node, level)
        # Dump...
        if isinstance(node, (list, tuple)):
            for z in node:
                self.dump_tree_and_links_helper(z, level, result)
        elif isinstance(node, str):
            result.append(f"{indent}{node.__class__.__name__:>8}:{node}\n")
        elif isinstance(node, ast.AST):
            # Node and parent.
            result.append(node_s)
            # Children.
            for z in children:
                self.dump_tree_and_links_helper(z, level + 1, result)
        else:
            result.append(node_s)
    #@+node:ekr.20191125035600.1: *3* dumper.compute_node_string & helpers
    def compute_node_string(self, node, level):
        """Return a string summarizing the node."""
        indent = ' ' * 2 * level
        parent = getattr(node, 'parent', None)
        node_id = getattr(node, 'node_index', '??')
        parent_id = getattr(parent, 'node_index', '??')
        parent_s = f"{parent_id:>3}.{parent.__class__.__name__} " if parent else ''
        class_name = node.__class__.__name__
        descriptor_s = f"{node_id}.{class_name}: " + self.show_fields(
            class_name, node, 30)
        tokens_s = self.show_tokens(node, 70, 100)
        lines = self.show_line_range(node)
        full_s1 = f"{parent_s:<16} {lines:<10} {indent}{descriptor_s} "
        node_s = f"{full_s1:<62} {tokens_s}\n"
        return node_s
    #@+node:ekr.20191113223424.1: *4* dumper.show_fields
    def show_fields(self, class_name, node, truncate_n):
        """Return a string showing interesting fields of the node."""
        val = ''
        if class_name == 'JoinedStr':
            values = node.values
            assert isinstance(values, list)
            # Str tokens may represent *concatenated* strings.
            results = []
            fstrings, strings = 0, 0
            for z in values:
                assert isinstance(z, (ast.FormattedValue, ast.Str))
                if isinstance(z, ast.Str):
                    results.append(z.s)
                    strings += 1
                else:
                    results.append(z.__class__.__name__)
                    fstrings += 1
            val = f"{strings} str, {fstrings} f-str"
        elif class_name == 'keyword':
            if isinstance(node.value, ast.Str):
                val = f"arg={node.arg}..Str.value.s={node.value.s}"
            elif isinstance(node.value, ast.Name):
                val = f"arg={node.arg}..Name.value.id={node.value.id}"
            else:
                val = f"arg={node.arg}..value={node.value.__class__.__name__}"
        elif class_name == 'Name':
            val = f"id={node.id!r}"
        elif class_name == 'NameConstant':
            val = f"value={node.value!r}"
        elif class_name == 'Num':
            val = f"n={node.n}"
        elif class_name == 'Starred':
            if isinstance(node.value, ast.Str):
                val = f"s={node.value.s}"
            elif isinstance(node.value, ast.Name):
                val = f"id={node.value.id}"
            else:
                val = f"s={node.value.__class__.__name__}"
        elif class_name == 'Str':
            val = f"s={node.s!r}"
        elif class_name in ('AugAssign', 'BinOp', 'BoolOp', 'UnaryOp'):  # IfExp
            name = node.op.__class__.__name__
            val = f"op={_op_names.get(name, name)}"
        elif class_name == 'Compare':
            ops = ','.join([op_name(z) for z in node.ops])
            val = f"ops='{ops}'"
        else:
            val = ''
        return g.truncate(val, truncate_n)
    #@+node:ekr.20191114054726.1: *4* dumper.show_line_range
    def show_line_range(self, node):

        token_list = get_node_token_list(node, self.tokens)
        if not token_list:
            return ''
        min_ = min([z.line_number for z in token_list])
        max_ = max([z.line_number for z in token_list])
        return f"{min_}" if min_ == max_ else f"{min_}..{max_}"
    #@+node:ekr.20191113223425.1: *4* dumper.show_tokens
    def show_tokens(self, node, n, m, show_cruft=False):
        """
        Return a string showing node.token_list.

        Split the result if n + len(result) > m
        """
        token_list = get_node_token_list(node, self.tokens)
        result = []
        for z in token_list:
            val = None
            if z.kind == 'comment':
                if show_cruft:
                    val = g.truncate(z.value, 10)  # Short is good.
                    result.append(f"{z.kind}.{z.index}({val})")
            elif z.kind == 'name':
                val = g.truncate(z.value, 20)
                result.append(f"{z.kind}.{z.index}({val})")
            elif z.kind == 'newline':
                # result.append(f"{z.kind}.{z.index}({z.line_number}:{len(z.line)})")
                result.append(f"{z.kind}.{z.index}")
            elif z.kind == 'number':
                result.append(f"{z.kind}.{z.index}({z.value})")
            elif z.kind == 'op':
                if z.value not in ',()' or show_cruft:
                    result.append(f"{z.kind}.{z.index}({z.value})")
            elif z.kind == 'string':
                val = g.truncate(z.value, 30)
                result.append(f"{z.kind}.{z.index}({val})")
            elif z.kind == 'ws':
                if show_cruft:
                    result.append(f"{z.kind}.{z.index}({len(z.value)})")
            else:
                # Indent, dedent, encoding, etc.
                # Don't put a blank.
                continue
            if result and result[-1] != ' ':
                result.append(' ')
        #
        # split the line if it is too long.
        # g.printObj(result, tag='show_tokens')
        if 1:
            return ''.join(result)
        line, lines = [], []
        for r in result:
            line.append(r)
            if n + len(''.join(line)) >= m:
                lines.append(''.join(line))
                line = []
        lines.append(''.join(line))
        pad = '\n' + ' ' * n
        return pad.join(lines)
    #@+node:ekr.20191110165235.5: *3* dumper.show_header
    def show_header(self):
        """Return a header string, but only the fist time."""
        return (
            f"{'parent':<16} {'lines':<10} {'node':<34} {'tokens'}\n"
            f"{'======':<16} {'=====':<10} {'====':<34} {'======'}\n")
    #@+node:ekr.20141012064706.18392: *3* dumper.dump_ast & helper
    annotate_fields = False
    include_attributes = False
    indent_ws = ' '

    def dump_ast(self, node, level=0):
        """
        Dump an ast tree. Adapted from ast.dump.
        """
        sep1 = '\n%s' % (self.indent_ws * (level + 1))
        if isinstance(node, ast.AST):
            fields = [(a, self.dump_ast(b, level + 1)) for a, b in self.get_fields(node)]
            if self.include_attributes and node._attributes:
                fields.extend([(a, self.dump_ast(getattr(node, a), level + 1))
                    for a in node._attributes])
            if self.annotate_fields:
                aList = ['%s=%s' % (a, b) for a, b in fields]
            else:
                aList = [b for a, b in fields]
            name = node.__class__.__name__
            sep = '' if len(aList) <= 1 else sep1
            return '%s(%s%s)' % (name, sep, sep1.join(aList))
        if isinstance(node, list):
            sep = sep1
            return 'LIST[%s]' % ''.join(
                ['%s%s' % (sep, self.dump_ast(z, level + 1)) for z in node])
        return repr(node)
    #@+node:ekr.20141012064706.18393: *4* dumper.get_fields
    def get_fields(self, node):

        return (
            (a, b) for a, b in ast.iter_fields(node)
                if a not in ['ctx',] and b not in (None, [])
        )
    #@-others
#@+node:ekr.20191227170628.1: ** TOG classes...
#@+node:ekr.20191113063144.1: *3*  class TokenOrderGenerator
class TokenOrderGenerator:
    """
    A class that traverses ast (parse) trees in token order.

    Overview: https://github.com/leo-editor/leo-editor/issues/1440#issue-522090981

    Theory of operation:
    - https://github.com/leo-editor/leo-editor/issues/1440#issuecomment-573661883
    - http://leoeditor.com/appendices.html#tokenorder-classes-theory-of-operation

    How to: http://leoeditor.com/appendices.html#tokenorder-class-how-to

    Project history: https://github.com/leo-editor/leo-editor/issues/1440#issuecomment-574145510
    """

    n_nodes = 0  # The number of nodes that have been visited.
    #@+others
    #@+node:ekr.20200103174914.1: *4* tog: Init...
    #@+node:ekr.20191228184647.1: *5* tog.balance_tokens
    def balance_tokens(self, tokens):
        """
        TOG.balance_tokens.

        Insert two-way links between matching paren tokens.
        """
        count, stack = 0, []
        for token in tokens:
            if token.kind == 'op':
                if token.value == '(':
                    count += 1
                    stack.append(token.index)
                if token.value == ')':
                    if stack:
                        index = stack.pop()
                        tokens[index].matching_paren = token.index
                        tokens[token.index].matching_paren = index
                    else:
                        g.trace(f"unmatched ')' at index {token.index}")
        # g.trace(f"tokens: {len(tokens)} matched parens: {count}")
        if stack:
            g.trace("unmatched '(' at {','.join(stack)}")
        return count
    #@+node:ekr.20191113063144.4: *5* tog.create_links
    def create_links(self, tokens, tree, file_name=''):
        """
        A generator creates two-way links between the given tokens and ast-tree.

        Callers should call this generator with list(tog.create_links(...))

        The sync_tokens method creates the links and verifies that the resulting
        tree traversal generates exactly the given tokens in exact order.

        tokens: the list of Token instances for the input.
                Created by make_tokens().
        tree:   the ast tree for the input.
                Created by parse_ast().
        """
        #
        # Init all ivars.
        self.file_name = file_name
            # For tests.
        self.level = 0
            # Python indentation level.
        self.node = None
            # The node being visited.
            # The parent of the about-to-be visited node.
        self.tokens = tokens
            # The immutable list of input tokens.
        self.tree = tree
            # The tree of ast.AST nodes.
        #
        # Traverse the tree.
        try:
            while True:
                next(self.visitor(tree))
        except StopIteration:
            pass
        #
        # Ensure that all tokens are patched.
        self.node = tree
        yield from self.gen_token('endmarker', '')
    #@+node:ekr.20191229071733.1: *5* tog.init_from_file
    def init_from_file(self, filename):  # pragma: no cover
        """
        Create the tokens and ast tree for the given file.
        Create links between tokens and the parse tree.
        Return (contents, encoding, tokens, tree).
        """
        self.level = 0
        self.filename = filename
        encoding, contents = read_file_with_encoding(filename)
        if not contents:
            return None, None, None, None
        self.tokens = tokens = make_tokens(contents)
        self.tree = tree = parse_ast(contents)
        list(self.create_links(tokens, tree))
        return contents, encoding, tokens, tree
    #@+node:ekr.20191229071746.1: *5* tog.init_from_string
    def init_from_string(self, contents, filename):  # pragma: no cover
        """
        Tokenize, parse and create links in the contents string.

        Return (tokens, tree).
        """
        self.filename = filename
        self.level = 0
        self.tokens = tokens = make_tokens(contents)
        self.tree = tree = parse_ast(contents)
        list(self.create_links(tokens, tree))
        return tokens, tree
    #@+node:ekr.20191223052749.1: *4* tog: Traversal...
    #@+node:ekr.20191113063144.3: *5* tog.begin_visitor
    begin_end_stack: List[str] = []
    node_index = 0  # The index into the node_stack.
    node_stack: List[ast.AST] = []  # The stack of parent nodes.

    def begin_visitor(self, node):
        """Enter a visitor."""
        # Update the stats.
        self.n_nodes += 1
        # Do this first, *before* updating self.node.
        node.parent = self.node
        if self.node:
            children = getattr(self.node, 'children', [])  # type:ignore
            children.append(node)
            self.node.children = children
        # Inject the node_index field.
        assert not hasattr(node, 'node_index'), g.callers()
        node.node_index = self.node_index
        self.node_index += 1
        # begin_visitor and end_visitor must be paired.
        self.begin_end_stack.append(node.__class__.__name__)
        # Push the previous node.
        self.node_stack.append(self.node)
        # Update self.node *last*.
        self.node = node
    #@+node:ekr.20200104032811.1: *5* tog.end_visitor
    def end_visitor(self, node):
        """Leave a visitor."""
        # begin_visitor and end_visitor must be paired.
        entry_name = self.begin_end_stack.pop()
        assert entry_name == node.__class__.__name__, f"{entry_name!r} {node.__class__.__name__}"
        assert self.node == node, (repr(self.node), repr(node))
        # Restore self.node.
        self.node = self.node_stack.pop()
    #@+node:ekr.20200110162044.1: *5* tog.find_next_significant_token
    def find_next_significant_token(self):
        """
        Scan from *after* self.tokens[px] looking for the next significant
        token.

        Return the token, or None. Never change self.px.
        """
        px = self.px + 1
        while px < len(self.tokens):
            token = self.tokens[px]
            px += 1
            if is_significant_token(token):
                return token
        # This will never happen, because endtoken is significant.
        return None  # pragma: no cover
    #@+node:ekr.20191121180100.1: *5* tog.gen*
    # Useful wrappers...

    def gen(self, z):
        yield from self.visitor(z)

    def gen_name(self, val):
        yield from self.visitor(self.sync_name(val))  # type:ignore

    def gen_op(self, val):
        yield from self.visitor(self.sync_op(val))  # type:ignore

    def gen_token(self, kind, val):
        yield from self.visitor(self.sync_token(kind, val))  # type:ignore
    #@+node:ekr.20191113063144.7: *5* tog.sync_token & set_links
    px = -1  # Index of the previously synced token.

    def sync_token(self, kind, val):
        """
        Sync to a token whose kind & value are given. The token need not be
        significant, but it must be guaranteed to exist in the token list.

        The checks in this method constitute a strong, ever-present, unit test.

        Scan the tokens *after* px, looking for a token T matching (kind, val).
        raise AssignLinksError if a significant token is found that doesn't match T.
        Otherwise:
        - Create two-way links between all assignable tokens between px and T.
        - Create two-way links between T and self.node.
        - Advance by updating self.px to point to T.
        """
        node, tokens = self.node, self.tokens
        assert isinstance(node, ast.AST), repr(node)
        # g.trace(
            # f"px: {self.px:2} "
            # f"node: {node.__class__.__name__:<10} "
            # f"kind: {kind:>10}: val: {val!r}")
        #
        # Step one: Look for token T.
        old_px = px = self.px + 1
        while px < len(self.tokens):
            token = tokens[px]
            if (kind, val) == (token.kind, token.value):
                break  # Success.
            if kind == token.kind == 'number':
                val = token.value
                break  # Benign: use the token's value, a string, instead of a number.
            if is_significant_token(token):  # pragma: no cover
                line_s = f"line {token.line_number}:"
                val = str(val)  # for g.truncate.
                raise AssignLinksError(
                    f"       file: {self.filename}\n"
                    f"{line_s:>12} {token.line.strip()}\n"
                    f"Looking for: {kind}.{g.truncate(val, 40)!r}\n"
                    f"      found: {token.kind}.{token.value!r}\n"
                    f"token.index: {token.index}\n")
            # Skip the insignificant token.
            px += 1
        else:  # pragma: no cover
            val = str(val)  # for g.truncate.
            raise AssignLinksError(
                 f"       file: {self.filename}\n"
                 f"Looking for: {kind}.{g.truncate(val, 40)}\n"
                 f"      found: end of token list")
        #
        # Step two: Assign *secondary* links only for newline tokens.
        #           Ignore all other non-significant tokens.
        while old_px < px:
            token = tokens[old_px]
            old_px += 1
            if token.kind in ('comment', 'newline', 'nl'):
                self.set_links(node, token)
        #
        # Step three: Set links in the found token.
        token = tokens[px]
        self.set_links(node, token)
        #
        # Step four: Advance.
        self.px = px
    #@+node:ekr.20191125120814.1: *6* tog.set_links
    last_statement_node = None

    def set_links(self, node, token):
        """Make two-way links between token and the given node."""
        # Don't bother assigning comment, comma, parens, ws and endtoken tokens.
        if token.kind == 'comment':
            # Append the comment to node.comment_list.
            comment_list = getattr(node, 'comment_list', [])  # type:ignore
            node.comment_list = comment_list + [token]
            return
        if token.kind in ('endmarker', 'ws'):
            return
        if token.kind == 'op' and token.value in ',()':
            return
        # *Always* remember the last statement.
        statement = find_statement_node(node)
        if statement:
            self.last_statement_node = statement  # type:ignore
            assert not isinstance(self.last_statement_node, ast.Module)
        if token.node is not None:  # pragma: no cover
            line_s = f"line {token.line_number}:"
            raise AssignLinksError(
                    f"       file: {self.filename}\n"
                    f"{line_s:>12} {token.line.strip()}\n"
                    f"token index: {self.px}\n"
                    f"token.node is not None\n"
                    f" token.node: {token.node.__class__.__name__}\n"
                    f"    callers: {g.callers()}")
        # Assign newlines to the previous statement node, if any.
        if token.kind in ('newline', 'nl'):
            # Set an *auxilliary* link for the split/join logic.
            # Do *not* set token.node!
            token.statement_node = self.last_statement_node
            return
        if is_significant_token(token):
            # Link the token to the ast node.
            token.node = node  # type:ignore
            # Add the token to node's token_list.
            add_token_to_token_list(token, node)
    #@+node:ekr.20191124083124.1: *5* tog.sync_name and sync_op
    # It's valid for these to return None.

    def sync_name(self, val):
        aList = val.split('.')
        if len(aList) == 1:
            self.sync_token('name', val)
        else:
            for i, part in enumerate(aList):
                self.sync_token('name', part)
                if i < len(aList) - 1:
                    self.sync_op('.')

    def sync_op(self, val):
        """
        Sync to the given operator.

        val may be '(' or ')' *only* if the parens *will* actually exist in the
        token list.
        """
        self.sync_token('op', val)
    #@+node:ekr.20191113081443.1: *5* tog.visitor (calls begin/end_visitor)
    def visitor(self, node):
        """Given an ast node, return a *generator* from its visitor."""
        # This saves a lot of tests.
        trace = False
        if node is None:
            return
        if trace:
            # Keep this trace. It's useful.
            cn = node.__class__.__name__ if node else ' '
            caller1, caller2 = g.callers(2).split(',')
            g.trace(f"{caller1:>15} {caller2:<14} {cn}")
        # More general, more convenient.
        if isinstance(node, (list, tuple)):
            for z in node or []:
                if isinstance(z, ast.AST):
                    yield from self.visitor(z)
                else:  # pragma: no cover
                    # Some fields may contain ints or strings.
                    assert isinstance(z, (int, str)), z.__class__.__name__
            return
        # We *do* want to crash if the visitor doesn't exist.
        method = getattr(self, 'do_' + node.__class__.__name__)
        # Allow begin/end visitor to be generators.
        self.begin_visitor(node)
        yield from method(node)
        self.end_visitor(node)
    #@+node:ekr.20191113063144.13: *4* tog: Visitors...
    #@+node:ekr.20191113063144.32: *5*  tog.keyword: not called!
    # keyword arguments supplied to call (NULL identifier for **kwargs)

    # keyword = (identifier? arg, expr value)

    def do_keyword(self, node):  # pragma: no cover
        """A keyword arg in an ast.Call."""
        # This should never be called.
        # tog.hande_call_arguments calls self.gen(kwarg_arg.value) instead.
        filename = getattr(self, 'filename', '<no file>')
        raise AssignLinksError(
            f"file: {filename}\n"
            f"do_keyword should never be called\n"
            f"{g.callers(8)}")
    #@+node:ekr.20191113063144.14: *5* tog: Contexts
    #@+node:ekr.20191113063144.28: *6*  tog.arg
    # arg = (identifier arg, expr? annotation)

    def do_arg(self, node):
        """This is one argument of a list of ast.Function or ast.Lambda arguments."""
        yield from self.gen_name(node.arg)
        annotation = getattr(node, 'annotation', None)
        if annotation is not None:
            yield from self.gen_op(':')
            yield from self.gen(node.annotation)
    #@+node:ekr.20191113063144.27: *6*  tog.arguments
    # arguments = (
    #       arg* posonlyargs, arg* args, arg? vararg, arg* kwonlyargs,
    #       expr* kw_defaults, arg? kwarg, expr* defaults
    # )

    def do_arguments(self, node):
        """Arguments to ast.Function or ast.Lambda, **not** ast.Call."""
        #
        # No need to generate commas anywhere below.
        #
        # Let block. Some fields may not exist pre Python 3.8.
        n_plain = len(node.args) - len(node.defaults)
        posonlyargs = getattr(node, 'posonlyargs', [])  # type:ignore
        vararg = getattr(node, 'vararg', None)
        kwonlyargs = getattr(node, 'kwonlyargs', [])  # type:ignore
        kw_defaults = getattr(node, 'kw_defaults', [])  # type:ignore
        kwarg = getattr(node, 'kwarg', None)
        if 0:
            g.printObj(ast.dump(node.vararg) if node.vararg else 'None', tag='node.vararg')
            g.printObj([ast.dump(z) for z in node.args], tag='node.args')
            g.printObj([ast.dump(z) for z in node.defaults], tag='node.defaults')
            g.printObj([ast.dump(z) for z in posonlyargs], tag='node.posonlyargs')
            g.printObj([ast.dump(z) for z in kwonlyargs], tag='kwonlyargs')
            g.printObj([ast.dump(z) if z else 'None' for z in kw_defaults], tag='kw_defaults')
        # 1. Sync the position-only args.
        if posonlyargs:
            for n, z in enumerate(posonlyargs):
                # g.trace('pos-only', ast.dump(z))
                yield from self.gen(z)
            yield from self.gen_op('/')
        # 2. Sync all args.
        for i, z in enumerate(node.args):
            yield from self.gen(z)
            if i >= n_plain:
                yield from self.gen_op('=')
                yield from self.gen(node.defaults[i - n_plain])
        # 3. Sync the vararg.
        if vararg:
            # g.trace('vararg', ast.dump(vararg))
            yield from self.gen_op('*')
            yield from self.gen(vararg)
        # 4. Sync the keyword-only args.
        if kwonlyargs:
            if not vararg:
                yield from self.gen_op('*')
            for n, z in enumerate(kwonlyargs):
                # g.trace('keyword-only', ast.dump(z))
                yield from self.gen(z)
                val = kw_defaults[n]
                if val is not None:
                    yield from self.gen_op('=')
                    yield from self.gen(val)
        # 5. Sync the kwarg.
        if kwarg:
            # g.trace('kwarg', ast.dump(kwarg))
            yield from self.gen_op('**')
            yield from self.gen(kwarg)

    #@+node:ekr.20191113063144.15: *6* tog.AsyncFunctionDef
    # AsyncFunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list,
    #                expr? returns)

    def do_AsyncFunctionDef(self, node):

        if node.decorator_list:
            for z in node.decorator_list:
                # '@%s\n'
                yield from self.gen_op('@')
                yield from self.gen(z)
        # 'asynch def (%s): -> %s\n'
        # 'asynch def %s(%s):\n'
        async_token_type = 'async' if has_async_tokens else 'name'
        yield from self.gen_token(async_token_type, 'async')
        yield from self.gen_name('def')
        yield from self.gen_name(node.name)  # A string
        yield from self.gen_op('(')
        yield from self.gen(node.args)
        yield from self.gen_op(')')
        returns = getattr(node, 'returns', None)
        if returns is not None:
            yield from self.gen_op('->')
            yield from self.gen(node.returns)
        yield from self.gen_op(':')
        self.level += 1
        yield from self.gen(node.body)
        self.level -= 1
    #@+node:ekr.20191113063144.16: *6* tog.ClassDef
    def do_ClassDef(self, node, print_body=True):

        for z in node.decorator_list or []:
            # @{z}\n
            yield from self.gen_op('@')
            yield from self.gen(z)
        # class name(bases):\n
        yield from self.gen_name('class')
        yield from self.gen_name(node.name)  # A string.
        if node.bases:
            yield from self.gen_op('(')
            yield from self.gen(node.bases)
            yield from self.gen_op(')')
        yield from self.gen_op(':')
        # Body...
        self.level += 1
        yield from self.gen(node.body)
        self.level -= 1
    #@+node:ekr.20191113063144.17: *6* tog.FunctionDef
    # FunctionDef(
    #   identifier name, arguments args,
    #   stmt* body,
    #   expr* decorator_list,
    #   expr? returns,
    #   string? type_comment)

    def do_FunctionDef(self, node):

        # Guards...
        returns = getattr(node, 'returns', None)
        # Decorators...
            # @{z}\n
        for z in node.decorator_list or []:
            yield from self.gen_op('@')
            yield from self.gen(z)
        # Signature...
            # def name(args): -> returns\n
            # def name(args):\n
        yield from self.gen_name('def')
        yield from self.gen_name(node.name)  # A string.
        yield from self.gen_op('(')
        yield from self.gen(node.args)
        yield from self.gen_op(')')
        if returns is not None:
            yield from self.gen_op('->')
            yield from self.gen(node.returns)
        yield from self.gen_op(':')
        # Body...
        self.level += 1
        yield from self.gen(node.body)
        self.level -= 1
    #@+node:ekr.20191113063144.18: *6* tog.Interactive
    def do_Interactive(self, node):  # pragma: no cover

        yield from self.gen(node.body)
    #@+node:ekr.20191113063144.20: *6* tog.Lambda
    def do_Lambda(self, node):

        yield from self.gen_name('lambda')
        yield from self.gen(node.args)
        yield from self.gen_op(':')
        yield from self.gen(node.body)
    #@+node:ekr.20191113063144.19: *6* tog.Module
    def do_Module(self, node):

        # Encoding is a non-syncing statement.
        yield from self.gen(node.body)
    #@+node:ekr.20191113063144.21: *5* tog: Expressions
    #@+node:ekr.20191113063144.22: *6* tog.Expr
    def do_Expr(self, node):
        """An outer expression."""
        # No need to put parentheses.
        yield from self.gen(node.value)
    #@+node:ekr.20191113063144.23: *6* tog.Expression
    def do_Expression(self, node):  # pragma: no cover
        """An inner expression."""
        # No need to put parentheses.
        yield from self.gen(node.body)
    #@+node:ekr.20191113063144.24: *6* tog.GeneratorExp
    def do_GeneratorExp(self, node):

        # '<gen %s for %s>' % (elt, ','.join(gens))
        # No need to put parentheses or commas.
        yield from self.gen(node.elt)
        yield from self.gen(node.generators)
    #@+node:ekr.20210321171703.1: *6* tog.NamedExpr
    # NamedExpr(expr target, expr value)

    def do_NamedExpr(self, node):  # Python 3.8+

        yield from self.gen(node.target)
        yield from self.gen_op(':=')
        yield from self.gen(node.value)
    #@+node:ekr.20191113063144.26: *5* tog: Operands
    #@+node:ekr.20191113063144.29: *6* tog.Attribute
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self, node):

        yield from self.gen(node.value)
        yield from self.gen_op('.')
        yield from self.gen_name(node.attr)  # A string.
    #@+node:ekr.20191113063144.30: *6* tog.Bytes
    def do_Bytes(self, node):

        """
        It's invalid to mix bytes and non-bytes literals, so just
        advancing to the next 'string' token suffices.
        """
        token = self.find_next_significant_token()
        yield from self.gen_token('string', token.value)
    #@+node:ekr.20191113063144.33: *6* tog.comprehension
    # comprehension = (expr target, expr iter, expr* ifs, int is_async)

    def do_comprehension(self, node):

        # No need to put parentheses.
        yield from self.gen_name('for')  # #1858.
        yield from self.gen(node.target)  # A name
        yield from self.gen_name('in')
        yield from self.gen(node.iter)
        for z in node.ifs or []:
            yield from self.gen_name('if')
            yield from self.gen(z)
    #@+node:ekr.20191113063144.34: *6* tog.Constant
    def do_Constant(self, node):  # pragma: no cover
        """

        https://greentreesnakes.readthedocs.io/en/latest/nodes.html

        A constant. The value attribute holds the Python object it represents.
        This can be simple types such as a number, string or None, but also
        immutable container types (tuples and frozensets) if all of their
        elements are constant.
        """

        # Support Python 3.8.
        if node.value is None or isinstance(node.value, bool):
            # Weird: return a name!
            yield from self.gen_token('name', repr(node.value))
        elif node.value == Ellipsis:
            yield from self.gen_op('...')
        elif isinstance(node.value, str):
            yield from self.do_Str(node)
        elif isinstance(node.value, (int, float)):
            yield from self.gen_token('number', repr(node.value))
        elif isinstance(node.value, bytes):
            yield from self.do_Bytes(node)
        elif isinstance(node.value, tuple):
            yield from self.do_Tuple(node)
        elif isinstance(node.value, frozenset):
            yield from self.do_Set(node)
        else:
            # Unknown type.
            g.trace('----- Oops -----', repr(node.value), g.callers())
    #@+node:ekr.20191113063144.35: *6* tog.Dict
    # Dict(expr* keys, expr* values)

    def do_Dict(self, node):

        assert len(node.keys) == len(node.values)
        yield from self.gen_op('{')
        # No need to put commas.
        for i, key in enumerate(node.keys):
            key, value = node.keys[i], node.values[i]
            yield from self.gen(key)  # a Str node.
            yield from self.gen_op(':')
            if value is not None:
                yield from self.gen(value)
        yield from self.gen_op('}')
    #@+node:ekr.20191113063144.36: *6* tog.DictComp
    # DictComp(expr key, expr value, comprehension* generators)

    # d2 = {val: key for key, val in d}

    def do_DictComp(self, node):

        yield from self.gen_token('op', '{')
        yield from self.gen(node.key)
        yield from self.gen_op(':')
        yield from self.gen(node.value)
        for z in node.generators or []:
            yield from self.gen(z)
            yield from self.gen_token('op', '}')
    #@+node:ekr.20191113063144.37: *6* tog.Ellipsis
    def do_Ellipsis(self, node):  # pragma: no cover (Does not exist for python 3.8+)

        yield from self.gen_op('...')
    #@+node:ekr.20191113063144.38: *6* tog.ExtSlice
    # https://docs.python.org/3/reference/expressions.html#slicings

    # ExtSlice(slice* dims)

    def do_ExtSlice(self, node):  # pragma: no cover (deprecated)

        # ','.join(node.dims)
        for i, z in enumerate(node.dims):
            yield from self.gen(z)
            if i < len(node.dims) - 1:
                yield from self.gen_op(',')
    #@+node:ekr.20191113063144.40: *6* tog.Index
    def do_Index(self, node):  # pragma: no cover (deprecated)

        yield from self.gen(node.value)
    #@+node:ekr.20191113063144.39: *6* tog.FormattedValue: not called!
    # FormattedValue(expr value, int? conversion, expr? format_spec)

    def do_FormattedValue(self, node):  # pragma: no cover
        """
        This node represents the *components* of a *single* f-string.

        Happily, JoinedStr nodes *also* represent *all* f-strings,
        so the TOG should *never visit this node!
        """
        filename = getattr(self, 'filename', '<no file>')
        raise AssignLinksError(
            f"file: {filename}\n"
            f"do_FormattedValue should never be called")

        # This code has no chance of being useful...

            # conv = node.conversion
            # spec = node.format_spec
            # yield from self.gen(node.value)
            # if conv is not None:
                # yield from self.gen_token('number', conv)
            # if spec is not None:
                # yield from self.gen(node.format_spec)
    #@+node:ekr.20191113063144.41: *6* tog.JoinedStr & helpers
    # JoinedStr(expr* values)

    def do_JoinedStr(self, node):
        """
        JoinedStr nodes represent at least one f-string and all other strings
        concatentated to it.

        Analyzing JoinedStr.values would be extremely tricky, for reasons that
        need not be explained here.

        Instead, we get the tokens *from the token list itself*!
        """
        for z in self.get_concatenated_string_tokens():
            yield from self.gen_token(z.kind, z.value)
    #@+node:ekr.20191113063144.42: *6* tog.List
    def do_List(self, node):

        # No need to put commas.
        yield from self.gen_op('[')
        yield from self.gen(node.elts)
        yield from self.gen_op(']')
    #@+node:ekr.20191113063144.43: *6* tog.ListComp
    # ListComp(expr elt, comprehension* generators)

    def do_ListComp(self, node):

        yield from self.gen_op('[')
        yield from self.gen(node.elt)
        for z in node.generators:
            yield from self.gen(z)
        yield from self.gen_op(']')
    #@+node:ekr.20191113063144.44: *6* tog.Name & NameConstant
    def do_Name(self, node):

        yield from self.gen_name(node.id)

    def do_NameConstant(self, node):  # pragma: no cover (Does not exist in Python 3.8+)

        yield from self.gen_name(repr(node.value))

    #@+node:ekr.20191113063144.45: *6* tog.Num
    def do_Num(self, node):  # pragma: no cover (Does not exist in Python 3.8+)

        yield from self.gen_token('number', node.n)
    #@+node:ekr.20191113063144.47: *6* tog.Set
    # Set(expr* elts)

    def do_Set(self, node):

        yield from self.gen_op('{')
        yield from self.gen(node.elts)
        yield from self.gen_op('}')
    #@+node:ekr.20191113063144.48: *6* tog.SetComp
    # SetComp(expr elt, comprehension* generators)

    def do_SetComp(self, node):

        yield from self.gen_op('{')
        yield from self.gen(node.elt)
        for z in node.generators or []:
            yield from self.gen(z)
        yield from self.gen_op('}')
    #@+node:ekr.20191113063144.49: *6* tog.Slice
    # slice = Slice(expr? lower, expr? upper, expr? step)

    def do_Slice(self, node):

        lower = getattr(node, 'lower', None)
        upper = getattr(node, 'upper', None)
        step = getattr(node, 'step', None)
        if lower is not None:
            yield from self.gen(lower)
        # Always put the colon between upper and lower.
        yield from self.gen_op(':')
        if upper is not None:
            yield from self.gen(upper)
        # Put the second colon if it exists in the token list.
        if step is None:
            token = self.find_next_significant_token()
            if token and token.value == ':':
                yield from self.gen_op(':')
        else:
            yield from self.gen_op(':')
            yield from self.gen(step)
    #@+node:ekr.20191113063144.50: *6* tog.Str & helper
    def do_Str(self, node):
        """This node represents a string constant."""
        # This loop is necessary to handle string concatenation.
        for z in self.get_concatenated_string_tokens():
            yield from self.gen_token(z.kind, z.value)
    #@+node:ekr.20200111083914.1: *7* tog.get_concatenated_tokens
    def get_concatenated_string_tokens(self):
        """
        Return the next 'string' token and all 'string' tokens concatenated to
        it. *Never* update self.px here.
        """
        trace = False
        tag = 'tog.get_concatenated_string_tokens'
        i = self.px
        # First, find the next significant token.  It should be a string.
        i, token = i + 1, None
        while i < len(self.tokens):
            token = self.tokens[i]
            i += 1
            if token.kind == 'string':
                # Rescan the string.
                i -= 1
                break
            # An error.
            if is_significant_token(token):  # pragma: no cover
                break
        # Raise an error if we didn't find the expected 'string' token.
        if not token or token.kind != 'string':  # pragma: no cover
            if not token:
                token = self.tokens[-1]
            filename = getattr(self, 'filename', '<no filename>')
            raise AssignLinksError(
                f"\n"
                f"{tag}...\n"
                f"file: {filename}\n"
                f"line: {token.line_number}\n"
                f"   i: {i}\n"
                f"expected 'string' token, got {token!s}")
        # Accumulate string tokens.
        assert self.tokens[i].kind == 'string'
        results = []
        while i < len(self.tokens):
            token = self.tokens[i]
            i += 1
            if token.kind == 'string':
                results.append(token)
            elif token.kind == 'op' or is_significant_token(token):
                # Any significant token *or* any op will halt string concatenation.
                break
            # 'ws', 'nl', 'newline', 'comment', 'indent', 'dedent', etc.
        # The (significant) 'endmarker' token ensures we will have result.
        assert results
        if trace:
            g.printObj(results, tag=f"{tag}: Results")
        return results
    #@+node:ekr.20191113063144.51: *6* tog.Subscript
    # Subscript(expr value, slice slice, expr_context ctx)

    def do_Subscript(self, node):

        yield from self.gen(node.value)
        yield from self.gen_op('[')
        yield from self.gen(node.slice)
        yield from self.gen_op(']')
    #@+node:ekr.20191113063144.52: *6* tog.Tuple
    # Tuple(expr* elts, expr_context ctx)

    def do_Tuple(self, node):

        # Do not call gen_op for parens or commas here.
        # They do not necessarily exist in the token list!
        yield from self.gen(node.elts)
    #@+node:ekr.20191113063144.53: *5* tog: Operators
    #@+node:ekr.20191113063144.55: *6* tog.BinOp
    def do_BinOp(self, node):

        op_name_ = op_name(node.op)
        yield from self.gen(node.left)
        yield from self.gen_op(op_name_)
        yield from self.gen(node.right)
    #@+node:ekr.20191113063144.56: *6* tog.BoolOp
    # BoolOp(boolop op, expr* values)

    def do_BoolOp(self, node):

        # op.join(node.values)
        op_name_ = op_name(node.op)
        for i, z in enumerate(node.values):
            yield from self.gen(z)
            if i < len(node.values) - 1:
                yield from self.gen_name(op_name_)
    #@+node:ekr.20191113063144.57: *6* tog.Compare
    # Compare(expr left, cmpop* ops, expr* comparators)

    def do_Compare(self, node):

        assert len(node.ops) == len(node.comparators)
        yield from self.gen(node.left)
        for i, z in enumerate(node.ops):
            op_name_ = op_name(node.ops[i])
            if op_name_ in ('not in', 'is not'):
                for z in op_name_.split(' '):
                    yield from self.gen_name(z)
            elif op_name_.isalpha():
                yield from self.gen_name(op_name_)
            else:
                yield from self.gen_op(op_name_)
            yield from self.gen(node.comparators[i])
    #@+node:ekr.20191113063144.58: *6* tog.UnaryOp
    def do_UnaryOp(self, node):

        op_name_ = op_name(node.op)
        if op_name_.isalpha():
            yield from self.gen_name(op_name_)
        else:
            yield from self.gen_op(op_name_)
        yield from self.gen(node.operand)
    #@+node:ekr.20191113063144.59: *6* tog.IfExp (ternary operator)
    # IfExp(expr test, expr body, expr orelse)

    def do_IfExp(self, node):

        #'%s if %s else %s'
        yield from self.gen(node.body)
        yield from self.gen_name('if')
        yield from self.gen(node.test)
        yield from self.gen_name('else')
        yield from self.gen(node.orelse)
    #@+node:ekr.20191113063144.60: *5* tog: Statements
    #@+node:ekr.20191113063144.83: *6*  tog.Starred
    # Starred(expr value, expr_context ctx)

    def do_Starred(self, node):
        """A starred argument to an ast.Call"""
        yield from self.gen_op('*')
        yield from self.gen(node.value)
    #@+node:ekr.20191113063144.61: *6* tog.AnnAssign
    # AnnAssign(expr target, expr annotation, expr? value, int simple)

    def do_AnnAssign(self, node):

        # {node.target}:{node.annotation}={node.value}\n'
        yield from self.gen(node.target)
        yield from self.gen_op(':')
        yield from self.gen(node.annotation)
        if node.value is not None:  # #1851
            yield from self.gen_op('=')
            yield from self.gen(node.value)
    #@+node:ekr.20191113063144.62: *6* tog.Assert
    # Assert(expr test, expr? msg)

    def do_Assert(self, node):

        # Guards...
        msg = getattr(node, 'msg', None)
        # No need to put parentheses or commas.
        yield from self.gen_name('assert')
        yield from self.gen(node.test)
        if msg is not None:
            yield from self.gen(node.msg)
    #@+node:ekr.20191113063144.63: *6* tog.Assign
    def do_Assign(self, node):

        for z in node.targets:
            yield from self.gen(z)
            yield from self.gen_op('=')
        yield from self.gen(node.value)
    #@+node:ekr.20191113063144.64: *6* tog.AsyncFor
    def do_AsyncFor(self, node):

        # The def line...
        # Py 3.8 changes the kind of token.
        async_token_type = 'async' if has_async_tokens else 'name'
        yield from self.gen_token(async_token_type, 'async')
        yield from self.gen_name('for')
        yield from self.gen(node.target)
        yield from self.gen_name('in')
        yield from self.gen(node.iter)
        yield from self.gen_op(':')
        # Body...
        self.level += 1
        yield from self.gen(node.body)
        # Else clause...
        if node.orelse:
            yield from self.gen_name('else')
            yield from self.gen_op(':')
            yield from self.gen(node.orelse)
        self.level -= 1
    #@+node:ekr.20191113063144.65: *6* tog.AsyncWith
    def do_AsyncWith(self, node):

        async_token_type = 'async' if has_async_tokens else 'name'
        yield from self.gen_token(async_token_type, 'async')
        yield from self.do_With(node)
    #@+node:ekr.20191113063144.66: *6* tog.AugAssign
    # AugAssign(expr target, operator op, expr value)

    def do_AugAssign(self, node):

        # %s%s=%s\n'
        op_name_ = op_name(node.op)
        yield from self.gen(node.target)
        yield from self.gen_op(op_name_ + '=')
        yield from self.gen(node.value)
    #@+node:ekr.20191113063144.67: *6* tog.Await
    # Await(expr value)

    def do_Await(self, node):

        #'await %s\n'
        async_token_type = 'await' if has_async_tokens else 'name'
        yield from self.gen_token(async_token_type, 'await')
        yield from self.gen(node.value)
    #@+node:ekr.20191113063144.68: *6* tog.Break
    def do_Break(self, node):

        yield from self.gen_name('break')
    #@+node:ekr.20191113063144.31: *6* tog.Call & helpers
    # Call(expr func, expr* args, keyword* keywords)

    # Python 3 ast.Call nodes do not have 'starargs' or 'kwargs' fields.

    def do_Call(self, node):

        # The calls to gen_op(')') and gen_op('(') do nothing by default.
        # Subclasses might handle them in an overridden tog.set_links.
        yield from self.gen(node.func)
        yield from self.gen_op('(')
        # No need to generate any commas.
        yield from self.handle_call_arguments(node)
        yield from self.gen_op(')')
    #@+node:ekr.20191204114930.1: *7* tog.arg_helper
    def arg_helper(self, node):
        """
        Yield the node, with a special case for strings.
        """
        if isinstance(node, str):
            yield from self.gen_token('name', node)
        else:
            yield from self.gen(node)
    #@+node:ekr.20191204105506.1: *7* tog.handle_call_arguments
    def handle_call_arguments(self, node):
        """
        Generate arguments in the correct order.

        Call(expr func, expr* args, keyword* keywords)

        https://docs.python.org/3/reference/expressions.html#calls

        Warning: This code will fail on Python 3.8 only for calls
                 containing kwargs in unexpected places.
        """
        # *args:    in node.args[]:     Starred(value=Name(id='args'))
        # *[a, 3]:  in node.args[]:     Starred(value=List(elts=[Name(id='a'), Num(n=3)])
        # **kwargs: in node.keywords[]: keyword(arg=None, value=Name(id='kwargs'))
        #
        # Scan args for *name or *List
        args = node.args or []
        keywords = node.keywords or []

        def get_pos(obj):
            line1 = getattr(obj, 'lineno', None)
            col1 = getattr(obj, 'col_offset', None)
            return line1, col1, obj

        def sort_key(aTuple):
            line, col, obj = aTuple
            return line * 1000 + col

        if 0:
            g.printObj([ast.dump(z) for z in args], tag='args')
            g.printObj([ast.dump(z) for z in keywords], tag='keywords')

        if py_version >= (3, 9):
            places = [get_pos(z) for z in args + keywords]
            places.sort(key=sort_key)
            ordered_args = [z[2] for z in places]
            for z in ordered_args:
                if isinstance(z, ast.Starred):
                    yield from self.gen_op('*')
                    yield from self.gen(z.value)
                elif isinstance(z, ast.keyword):
                    if getattr(z, 'arg', None) is None:
                        yield from self.gen_op('**')
                        yield from self.arg_helper(z.value)
                    else:
                        yield from self.arg_helper(z.arg)
                        yield from self.gen_op('=')
                        yield from self.arg_helper(z.value)
                else:
                    yield from self.arg_helper(z)
        else:  # pragma: no cover
            #
            # Legacy code: May fail for Python 3.8
            #
            # Scan args for *arg and *[...]
            kwarg_arg = star_arg = None
            for z in args:
                if isinstance(z, ast.Starred):
                    if isinstance(z.value, ast.Name):  # *Name.
                        star_arg = z
                        args.remove(z)
                        break
                    elif isinstance(z.value, (ast.List, ast.Tuple)):  # *[...]
                        # star_list = z
                        break
                    raise AttributeError(f"Invalid * expression: {ast.dump(z)}")  # pragma: no cover
            # Scan keywords for **name.
            for z in keywords:
                if hasattr(z, 'arg') and z.arg is None:
                    kwarg_arg = z
                    keywords.remove(z)
                    break
            # Sync the plain arguments.
            for z in args:
                yield from self.arg_helper(z)
            # Sync the keyword args.
            for z in keywords:
                yield from self.arg_helper(z.arg)
                yield from self.gen_op('=')
                yield from self.arg_helper(z.value)
            # Sync the * arg.
            if star_arg:
                yield from self.arg_helper(star_arg)
            # Sync the ** kwarg.
            if kwarg_arg:
                yield from self.gen_op('**')
                yield from self.gen(kwarg_arg.value)
    #@+node:ekr.20191113063144.69: *6* tog.Continue
    def do_Continue(self, node):

        yield from self.gen_name('continue')
    #@+node:ekr.20191113063144.70: *6* tog.Delete
    def do_Delete(self, node):

        # No need to put commas.
        yield from self.gen_name('del')
        yield from self.gen(node.targets)
    #@+node:ekr.20191113063144.71: *6* tog.ExceptHandler
    def do_ExceptHandler(self, node):

        # Except line...
        yield from self.gen_name('except')
        if getattr(node, 'type', None):
            yield from self.gen(node.type)
        if getattr(node, 'name', None):
            yield from self.gen_name('as')
            yield from self.gen_name(node.name)
        yield from self.gen_op(':')
        # Body...
        self.level += 1
        yield from self.gen(node.body)
        self.level -= 1
    #@+node:ekr.20191113063144.73: *6* tog.For
    def do_For(self, node):

        # The def line...
        yield from self.gen_name('for')
        yield from self.gen(node.target)
        yield from self.gen_name('in')
        yield from self.gen(node.iter)
        yield from self.gen_op(':')
        # Body...
        self.level += 1
        yield from self.gen(node.body)
        # Else clause...
        if node.orelse:
            yield from self.gen_name('else')
            yield from self.gen_op(':')
            yield from self.gen(node.orelse)
        self.level -= 1
    #@+node:ekr.20191113063144.74: *6* tog.Global
    # Global(identifier* names)

    def do_Global(self, node):

        yield from self.gen_name('global')
        for z in node.names:
            yield from self.gen_name(z)
    #@+node:ekr.20191113063144.75: *6* tog.If & helpers
    # If(expr test, stmt* body, stmt* orelse)

    def do_If(self, node):
        #@+<< do_If docstring >>
        #@+node:ekr.20191122222412.1: *7* << do_If docstring >>
        """
        The parse trees for the following are identical!

          if 1:            if 1:
              pass             pass
          else:            elif 2:
              if 2:            pass
                  pass

        So there is *no* way for the 'if' visitor to disambiguate the above two
        cases from the parse tree alone.

        Instead, we scan the tokens list for the next 'if', 'else' or 'elif' token.
        """
        #@-<< do_If docstring >>
        # Use the next significant token to distinguish between 'if' and 'elif'.
        token = self.find_next_significant_token()
        yield from self.gen_name(token.value)
        yield from self.gen(node.test)
        yield from self.gen_op(':')
        #
        # Body...
        self.level += 1
        yield from self.gen(node.body)
        self.level -= 1
        #
        # Else and elif clauses...
        if node.orelse:
            self.level += 1
            token = self.find_next_significant_token()
            if token.value == 'else':
                yield from self.gen_name('else')
                yield from self.gen_op(':')
                yield from self.gen(node.orelse)
            else:
                yield from self.gen(node.orelse)
            self.level -= 1
    #@+node:ekr.20191113063144.76: *6* tog.Import & helper
    def do_Import(self, node):

        yield from self.gen_name('import')
        for alias in node.names:
            yield from self.gen_name(alias.name)
            if alias.asname:
                yield from self.gen_name('as')
                yield from self.gen_name(alias.asname)
    #@+node:ekr.20191113063144.77: *6* tog.ImportFrom
    # ImportFrom(identifier? module, alias* names, int? level)

    def do_ImportFrom(self, node):

        yield from self.gen_name('from')
        for i in range(node.level):
            yield from self.gen_op('.')
        if node.module:
            yield from self.gen_name(node.module)
        yield from self.gen_name('import')
        # No need to put commas.
        for alias in node.names:
            if alias.name == '*':  # #1851.
                yield from self.gen_op('*')
            else:
                yield from self.gen_name(alias.name)
            if alias.asname:
                yield from self.gen_name('as')
                yield from self.gen_name(alias.asname)
    #@+node:ekr.20191113063144.78: *6* tog.Nonlocal
    # Nonlocal(identifier* names)

    def do_Nonlocal(self, node):

        # nonlocal %s\n' % ','.join(node.names))
        # No need to put commas.
        yield from self.gen_name('nonlocal')
        for z in node.names:
            yield from self.gen_name(z)
    #@+node:ekr.20191113063144.79: *6* tog.Pass
    def do_Pass(self, node):

        yield from self.gen_name('pass')
    #@+node:ekr.20191113063144.81: *6* tog.Raise
    # Raise(expr? exc, expr? cause)

    def do_Raise(self, node):

        # No need to put commas.
        yield from self.gen_name('raise')
        exc = getattr(node, 'exc', None)
        cause = getattr(node, 'cause', None)
        tback = getattr(node, 'tback', None)
        yield from self.gen(exc)
        yield from self.gen(cause)
        yield from self.gen(tback)
    #@+node:ekr.20191113063144.82: *6* tog.Return
    def do_Return(self, node):

        yield from self.gen_name('return')
        yield from self.gen(node.value)
    #@+node:ekr.20191113063144.85: *6* tog.Try
    # Try(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)

    def do_Try(self, node):

        # Try line...
        yield from self.gen_name('try')
        yield from self.gen_op(':')
        # Body...
        self.level += 1
        yield from self.gen(node.body)
        yield from self.gen(node.handlers)
        # Else...
        if node.orelse:
            yield from self.gen_name('else')
            yield from self.gen_op(':')
            yield from self.gen(node.orelse)
        # Finally...
        if node.finalbody:
            yield from self.gen_name('finally')
            yield from self.gen_op(':')
            yield from self.gen(node.finalbody)
        self.level -= 1
    #@+node:ekr.20191113063144.88: *6* tog.While
    def do_While(self, node):

        # While line...
            # while %s:\n'
        yield from self.gen_name('while')
        yield from self.gen(node.test)
        yield from self.gen_op(':')
        # Body...
        self.level += 1
        yield from self.gen(node.body)
        # Else clause...
        if node.orelse:
            yield from self.gen_name('else')
            yield from self.gen_op(':')
            yield from self.gen(node.orelse)
        self.level -= 1
    #@+node:ekr.20191113063144.89: *6* tog.With
    # With(withitem* items, stmt* body)

    # withitem = (expr context_expr, expr? optional_vars)

    def do_With(self, node):

        expr: Optional[ast.AST] = getattr(node, 'context_expression', None)
        items: List[ast.AST] = getattr(node, 'items', [])
        yield from self.gen_name('with')
        yield from self.gen(expr)
        # No need to put commas.
        for item in items:
            yield from self.gen(item.context_expr)  # type:ignore
            optional_vars = getattr(item, 'optional_vars', None)
            if optional_vars is not None:
                yield from self.gen_name('as')
                yield from self.gen(item.optional_vars)  # type:ignore
        # End the line.
        yield from self.gen_op(':')
        # Body...
        self.level += 1
        yield from self.gen(node.body)
        self.level -= 1
    #@+node:ekr.20191113063144.90: *6* tog.Yield
    def do_Yield(self, node):

        yield from self.gen_name('yield')
        if hasattr(node, 'value'):
            yield from self.gen(node.value)
    #@+node:ekr.20191113063144.91: *6* tog.YieldFrom
    # YieldFrom(expr value)

    def do_YieldFrom(self, node):

        yield from self.gen_name('yield')
        yield from self.gen_name('from')
        yield from self.gen(node.value)
    #@-others
#@+node:ekr.20191226195813.1: *3*  class TokenOrderTraverser
class TokenOrderTraverser:
    """
    Traverse an ast tree using the parent/child links created by the
    TokenOrderInjector class.
    """
    #@+others
    #@+node:ekr.20191226200154.1: *4* TOT.traverse
    def traverse(self, tree):
        """
        Call visit, in token order, for all nodes in tree.

        Recursion is not allowed.

        The code follows p.moveToThreadNext exactly.
        """

        def has_next(i, node, stack):
            """Return True if stack[i] is a valid child of node.parent."""
            # g.trace(node.__class__.__name__, stack)
            parent = node.parent
            return bool(parent and parent.children and i < len(parent.children))

        # Update stats

        self.last_node_index = -1  # For visit
        # The stack contains child indices.
        node, stack = tree, [0]
        seen = set()
        while node and stack:
            # g.trace(
                # f"{node.node_index:>3} "
                # f"{node.__class__.__name__:<12} {stack}")
            # Visit the node.
            assert node.node_index not in seen, node.node_index
            seen.add(node.node_index)
            self.visit(node)
            # if p.v.children: p.moveToFirstChild()
            children: List[ast.AST] = getattr(node, 'children', [])
            if children:
                # Move to the first child.
                stack.append(0)
                node = children[0]
                # g.trace(' child:', node.__class__.__name__, stack)
                continue
            # elif p.hasNext(): p.moveToNext()
            stack[-1] += 1
            i = stack[-1]
            if has_next(i, node, stack):
                node = node.parent.children[i]
                continue
            # else...
            # p.moveToParent()
            node = node.parent
            stack.pop()
            # while p:
            while node and stack:
                # if p.hasNext():
                stack[-1] += 1
                i = stack[-1]
                if has_next(i, node, stack):
                    # Move to the next sibling.
                    node = node.parent.children[i]
                    break  # Found.
                # p.moveToParent()
                node = node.parent
                stack.pop()
            # not found.
            else:
                break  # pragma: no cover
        return self.last_node_index
    #@+node:ekr.20191227160547.1: *4* TOT.visit
    def visit(self, node):

        self.last_node_index += 1
        assert self.last_node_index == node.node_index, (
            self.last_node_index, node.node_index)
    #@-others
#@+node:ekr.20200107165250.1: *3* class Orange
class Orange:
    """
    A flexible and powerful beautifier for Python.
    Orange is the new black.

    *Important*: This is a predominantly a *token*-based beautifier.
    However, orange.colon and orange.possible_unary_op use the parse
    tree to provide context that would otherwise be difficult to
    deduce.
    """
    # This switch is really a comment. It will always be false.
    # It marks the code that simulates the operation of the black tool.
    black_mode = False

    # Patterns...
    nobeautify_pat = re.compile(r'\s*#\s*pragma:\s*no\s*beautify\b|#\s*@@nobeautify')

    # Patterns from FastAtRead class, specialized for python delims.
    node_pat = re.compile(r'^(\s*)#@\+node:([^:]+): \*(\d+)?(\*?) (.*)$')  # @node
    start_doc_pat = re.compile(r'^\s*#@\+(at|doc)?(\s.*?)?$')  # @doc or @
    at_others_pat = re.compile(r'^(\s*)#@(\+|-)others\b(.*)$')  # @others

    # Doc parts end with @c or a node sentinel. Specialized for python.
    end_doc_pat = re.compile(r"^\s*#@(@(c(ode)?)|([+]node\b.*))$")
    #@+others
    #@+node:ekr.20200107165250.2: *4* orange.ctor
    def __init__(self, settings=None):
        """Ctor for Orange class."""
        if settings is None:
            settings = {}
        valid_keys = (
            'allow_joined_strings',
            'max_join_line_length',
            'max_split_line_length',
            'orange',
            'tab_width',
        )
        # For mypy...
        self.kind: str = ''
        # Default settings...
        self.allow_joined_strings = False  # EKR's preference.
        self.max_join_line_length = 88
        self.max_split_line_length = 88
        self.tab_width = 4
        # Override from settings dict...
        for key in settings:  # pragma: no cover
            value = settings.get(key)
            if key in valid_keys and value is not None:
                setattr(self, key, value)
            else:
                g.trace(f"Unexpected setting: {key} = {value!r}")
    #@+node:ekr.20200107165250.51: *4* orange.push_state
    def push_state(self, kind, value=None):
        """Append a state to the state stack."""
        state = ParseState(kind, value)
        self.state_stack.append(state)
    #@+node:ekr.20200107165250.8: *4* orange: Entries
    #@+node:ekr.20200107173542.1: *5* orange.beautify (main token loop)
    def oops(self):
        g.trace(f"Unknown kind: {self.kind}")

    def beautify(self, contents, filename, tokens, tree, max_join_line_length=None, max_split_line_length=None):
        """
        The main line. Create output tokens and return the result as a string.
        """
        # Config overrides
        if max_join_line_length is not None:
            self.max_join_line_length = max_join_line_length
        if max_split_line_length is not None:
            self.max_split_line_length = max_split_line_length
        # State vars...
        self.curly_brackets_level = 0  # Number of unmatched '{' tokens.
        self.decorator_seen = False  # Set by do_name for do_op.
        self.in_arg_list = 0  # > 0 if in an arg list of a def.
        self.level = 0  # Set only by do_indent and do_dedent.
        self.lws = ''  # Leading whitespace.
        self.paren_level = 0  # Number of unmatched '(' tokens.
        self.square_brackets_stack: List[bool] = []  # A stack of bools, for self.word().
        self.state_stack: List["ParseState"] = []  # Stack of ParseState objects.
        self.val = None  # The input token's value (a string).
        self.verbatim = False  # True: don't beautify.
        #
        # Init output list and state...
        self.code_list: List[Token] = []  # The list of output tokens.
        self.code_list_index = 0  # The token's index.
        self.tokens = tokens  # The list of input tokens.
        self.tree = tree
        self.add_token('file-start', '')
        self.push_state('file-start')
        for i, token in enumerate(tokens):
            self.token = token
            self.kind, self.val, self.line = token.kind, token.value, token.line
            if self.verbatim:
                self.do_verbatim()
            else:
                func = getattr(self, f"do_{token.kind}", self.oops)
                func()
        # Any post pass would go here.
        return tokens_to_string(self.code_list)
    #@+node:ekr.20200107172450.1: *5* orange.beautify_file (entry)
    def beautify_file(self, filename):  # pragma: no cover
        """
        Orange: Beautify the the given external file.

        Return True if the file was changed.
        """
        tag = 'beautify-file'
        self.filename = filename
        tog = TokenOrderGenerator()
        contents, encoding, tokens, tree = tog.init_from_file(filename)
        if not contents or not tokens or not tree:
            print(f"{tag}: Can not beautify: {filename}")
            return False
        # Beautify.
        results = self.beautify(contents, filename, tokens, tree)
        # Something besides newlines must change.
        if regularize_nls(contents) == regularize_nls(results):
            print(f"{tag}: Unchanged: {filename}")
            return False
        if 0:  # This obscures more import error messages.
            # Show the diffs.
            show_diffs(contents, results, filename=filename)
        # Write the results
        print(f"{tag}: Wrote {filename}")
        write_file(filename, results, encoding=encoding)
        return True
    #@+node:ekr.20200107172512.1: *5* orange.beautify_file_diff (entry)
    def beautify_file_diff(self, filename):  # pragma: no cover
        """
        Orange: Print the diffs that would resulf from the orange-file command.

        Return True if the file would be changed.
        """
        tag = 'diff-beautify-file'
        self.filename = filename
        tog = TokenOrderGenerator()
        contents, encoding, tokens, tree = tog.init_from_file(filename)
        if not contents or not tokens or not tree:
            print(f"{tag}: Can not beautify: {filename}")
            return False
        # fstringify.
        results = self.beautify(contents, filename, tokens, tree)
        # Something besides newlines must change.
        if regularize_nls(contents) == regularize_nls(results):
            print(f"{tag}: Unchanged: {filename}")
            return False
        # Show the diffs.
        show_diffs(contents, results, filename=filename)
        return True
    #@+node:ekr.20200107165250.13: *4* orange: Input token handlers
    #@+node:ekr.20200107165250.14: *5* orange.do_comment
    in_doc_part = False

    def do_comment(self):
        """Handle a comment token."""
        val = self.val
        #
        # Leo-specific code...
        if self.node_pat.match(val):
            # Clear per-node state.
            self.in_doc_part = False
            self.verbatim = False
            self.decorator_seen = False
            # Do *not clear other state, which may persist across @others.
                # self.curly_brackets_level = 0
                # self.in_arg_list = 0
                # self.level = 0
                # self.lws = ''
                # self.paren_level = 0
                # self.square_brackets_stack = []
                # self.state_stack = []
        else:
            # Keep track of verbatim mode.
            if self.beautify_pat.match(val):
                self.verbatim = False
            elif self.nobeautify_pat.match(val):
                self.verbatim = True
            # Keep trace of @doc parts, to honor the convention for splitting lines.
            if self.start_doc_pat.match(val):
                self.in_doc_part = True
            if self.end_doc_pat.match(val):
                self.in_doc_part = False
        #
        # General code: Generate the comment.
        self.clean('blank')
        entire_line = self.line.lstrip().startswith('#')
        if entire_line:
            self.clean('hard-blank')
            self.clean('line-indent')
            # #1496: No further munging needed.
            val = self.line.rstrip()
        else:
            # Exactly two spaces before trailing comments.
            val = '  ' + self.val.rstrip()
        self.add_token('comment', val)
    #@+node:ekr.20200107165250.15: *5* orange.do_encoding
    def do_encoding(self):
        """
        Handle the encoding token.
        """
        pass
    #@+node:ekr.20200107165250.16: *5* orange.do_endmarker
    def do_endmarker(self):
        """Handle an endmarker token."""
        # Ensure exactly one blank at the end of the file.
        self.clean_blank_lines()
        self.add_token('line-end', '\n')
    #@+node:ekr.20200107165250.18: *5* orange.do_indent & do_dedent & helper
    def do_dedent(self):
        """Handle dedent token."""
        self.level -= 1
        self.lws = self.level * self.tab_width * ' '
        self.line_indent()
        if self.black_mode:  # pragma: no cover (black)
            state = self.state_stack[-1]
            if state.kind == 'indent' and state.value == self.level:
                self.state_stack.pop()
                state = self.state_stack[-1]
                if state.kind in ('class', 'def'):
                    self.state_stack.pop()
                    self.handle_dedent_after_class_or_def(state.kind)

    def do_indent(self):
        """Handle indent token."""
        new_indent = self.val
        old_indent = self.level * self.tab_width * ' '
        if new_indent > old_indent:
            self.level += 1
        elif new_indent < old_indent:  # pragma: no cover (defensive)
            g.trace('\n===== can not happen', repr(new_indent), repr(old_indent))
        self.lws = new_indent
        self.line_indent()
    #@+node:ekr.20200220054928.1: *6* orange.handle_dedent_after_class_or_def
    def handle_dedent_after_class_or_def(self, kind):  # pragma: no cover (black)
        """
        Insert blank lines after a class or def as the result of a 'dedent' token.

        Normal comment lines may precede the 'dedent'.
        Insert the blank lines *before* such comment lines.
        """
        #
        # Compute the tail.
        i = len(self.code_list) - 1
        tail: List[Token] = []
        while i > 0:
            t = self.code_list.pop()
            i -= 1
            if t.kind == 'line-indent':
                pass
            elif t.kind == 'line-end':
                tail.insert(0, t)
            elif t.kind == 'comment':
                # Only underindented single-line comments belong in the tail.
                # @+node comments must never be in the tail.
                single_line = self.code_list[i].kind in ('line-end', 'line-indent')
                lws = len(t.value) - len(t.value.lstrip())
                underindent = lws <= len(self.lws)
                if underindent and single_line and not self.node_pat.match(t.value):
                    # A single-line comment.
                    tail.insert(0, t)
                else:
                    self.code_list.append(t)
                    break
            else:
                self.code_list.append(t)
                break
        #
        # Remove leading 'line-end' tokens from the tail.
        while tail and tail[0].kind == 'line-end':
            tail = tail[1:]
        #
        # Put the newlines *before* the tail.
        # For Leo, always use 1 blank lines.
        n = 1  # n = 2 if kind == 'class' else 1
        # Retain the token (intention) for debugging.
        self.add_token('blank-lines', n)
        for i in range(0, n + 1):
            self.add_token('line-end', '\n')
        if tail:
            self.code_list.extend(tail)
        self.line_indent()
    #@+node:ekr.20200107165250.20: *5* orange.do_name
    def do_name(self):
        """Handle a name token."""
        name = self.val
        if self.black_mode and name in ('class', 'def'):  # pragma: no cover (black)
            # Handle newlines before and after 'class' or 'def'
            self.decorator_seen = False
            state = self.state_stack[-1]
            if state.kind == 'decorator':
                # Always do this, regardless of @bool clean-blank-lines.
                self.clean_blank_lines()
                # Suppress split/join.
                self.add_token('hard-newline', '\n')
                self.add_token('line-indent', self.lws)
                self.state_stack.pop()
            else:
                # Always do this, regardless of @bool clean-blank-lines.
                self.blank_lines(2 if name == 'class' else 1)
            self.push_state(name)
            self.push_state('indent', self.level)
                # For trailing lines after inner classes/defs.
            self.word(name)
            return
        #
        # Leo mode...
        if name in ('class', 'def'):
            self.word(name)
        elif name in (
            'and', 'elif', 'else', 'for', 'if', 'in', 'not', 'not in', 'or', 'while'
        ):
            self.word_op(name)
        else:
            self.word(name)
    #@+node:ekr.20200107165250.21: *5* orange.do_newline & do_nl
    def do_newline(self):
        """Handle a regular newline."""
        self.line_end()

    def do_nl(self):
        """Handle a continuation line."""
        self.line_end()
    #@+node:ekr.20200107165250.22: *5* orange.do_number
    def do_number(self):
        """Handle a number token."""
        self.blank()
        self.add_token('number', self.val)
    #@+node:ekr.20200107165250.23: *5* orange.do_op
    def do_op(self):
        """Handle an op token."""
        val = self.val
        if val == '.':
            self.clean('blank')
            self.add_token('op-no-blanks', val)
        elif val == '@':
            if self.black_mode:  # pragma: no cover (black)
                if not self.decorator_seen:
                    self.blank_lines(1)
                    self.decorator_seen = True
            self.clean('blank')
            self.add_token('op-no-blanks', val)
            self.push_state('decorator')
        elif val == ':':
            # Treat slices differently.
            self.colon(val)
        elif val in ',;':
            # Pep 8: Avoid extraneous whitespace immediately before
            # comma, semicolon, or colon.
            self.clean('blank')
            self.add_token('op', val)
            self.blank()
        elif val in '([{':
            # Pep 8: Avoid extraneous whitespace immediately inside
            # parentheses, brackets or braces.
            self.lt(val)
        elif val in ')]}':
            # Ditto.
            self.rt(val)
        elif val == '=':
            # Pep 8: Don't use spaces around the = sign when used to indicate
            # a keyword argument or a default parameter value.
            if self.paren_level:
                self.clean('blank')
                self.add_token('op-no-blanks', val)
            else:
                self.blank()
                self.add_token('op', val)
                self.blank()
        elif val in '~+-':
            self.possible_unary_op(val)
        elif val == '*':
            self.star_op()
        elif val == '**':
            self.star_star_op()
        else:
            # Pep 8: always surround binary operators with a single space.
            # '==','+=','-=','*=','**=','/=','//=','%=','!=','<=','>=','<','>',
            # '^','~','*','**','&','|','/','//',
            # Pep 8: If operators with different priorities are used,
            # consider adding whitespace around the operators with the lowest priority(ies).
            self.blank()
            self.add_token('op', val)
            self.blank()
    #@+node:ekr.20200107165250.24: *5* orange.do_string
    def do_string(self):
        """Handle a 'string' token."""
        # Careful: continued strings may contain '\r'
        val = regularize_nls(self.val)
        self.add_token('string', val)
        self.blank()
    #@+node:ekr.20200210175117.1: *5* orange.do_verbatim
    beautify_pat = re.compile(
        r'#\s*pragma:\s*beautify\b|#\s*@@beautify|#\s*@\+node|#\s*@[+-]others|#\s*@[+-]<<')

    def do_verbatim(self):
        """
        Handle one token in verbatim mode.
        End verbatim mode when the appropriate comment is seen.
        """
        kind = self.kind
        #
        # Careful: tokens may contain '\r'
        val = regularize_nls(self.val)
        if kind == 'comment':
            if self.beautify_pat.match(val):
                self.verbatim = False
            val = val.rstrip()
            self.add_token('comment', val)
            return
        if kind == 'indent':
            self.level += 1
            self.lws = self.level * self.tab_width * ' '
        if kind == 'dedent':
            self.level -= 1
            self.lws = self.level * self.tab_width * ' '
        self.add_token('verbatim', val)
    #@+node:ekr.20200107165250.25: *5* orange.do_ws
    def do_ws(self):
        """
        Handle the "ws" pseudo-token.

        Put the whitespace only if if ends with backslash-newline.
        """
        val = self.val
        # Handle backslash-newline.
        if '\\\n' in val:
            self.clean('blank')
            self.add_token('op-no-blanks', val)
            return
        # Handle start-of-line whitespace.
        prev = self.code_list[-1]
        inner = self.paren_level or self.square_brackets_stack or self.curly_brackets_level
        if prev.kind == 'line-indent' and inner:
            # Retain the indent that won't be cleaned away.
            self.clean('line-indent')
            self.add_token('hard-blank', val)
    #@+node:ekr.20200107165250.26: *4* orange: Output token generators
    #@+node:ekr.20200118145044.1: *5* orange.add_line_end
    def add_line_end(self):
        """Add a line-end request to the code list."""
        # This may be called from do_name as well as do_newline and do_nl.
        assert self.token.kind in ('newline', 'nl'), self.token.kind
        self.clean('blank')  # Important!
        self.clean('line-indent')
        t = self.add_token('line-end', '\n')
        # Distinguish between kinds of 'line-end' tokens.
        t.newline_kind = self.token.kind
        return t
    #@+node:ekr.20200107170523.1: *5* orange.add_token
    def add_token(self, kind, value):
        """Add an output token to the code list."""
        tok = Token(kind, value)
        tok.index = self.code_list_index  # For debugging only.
        self.code_list_index += 1
        self.code_list.append(tok)
        return tok
    #@+node:ekr.20200107165250.27: *5* orange.blank
    def blank(self):
        """Add a blank request to the code list."""
        prev = self.code_list[-1]
        if prev.kind not in (
            'blank',
            'blank-lines',
            'file-start',
            'hard-blank',  # Unique to orange.
            'line-end',
            'line-indent',
            'lt',
            'op-no-blanks',
            'unary-op',
        ):
            self.add_token('blank', ' ')
    #@+node:ekr.20200107165250.29: *5* orange.blank_lines (black only)
    def blank_lines(self, n):  # pragma: no cover (black)
        """
        Add a request for n blank lines to the code list.
        Multiple blank-lines request yield at least the maximum of all requests.
        """
        self.clean_blank_lines()
        prev = self.code_list[-1]
        if prev.kind == 'file-start':
            self.add_token('blank-lines', n)
            return
        for i in range(0, n + 1):
            self.add_token('line-end', '\n')
        # Retain the token (intention) for debugging.
        self.add_token('blank-lines', n)
        self.line_indent()
    #@+node:ekr.20200107165250.30: *5* orange.clean
    def clean(self, kind):
        """Remove the last item of token list if it has the given kind."""
        prev = self.code_list[-1]
        if prev.kind == kind:
            self.code_list.pop()
    #@+node:ekr.20200107165250.31: *5* orange.clean_blank_lines
    def clean_blank_lines(self):
        """
        Remove all vestiges of previous blank lines.

        Return True if any of the cleaned 'line-end' tokens represented "hard" newlines.
        """
        cleaned_newline = False
        table = ('blank-lines', 'line-end', 'line-indent')
        while self.code_list[-1].kind in table:
            t = self.code_list.pop()
            if t.kind == 'line-end' and getattr(t, 'newline_kind', None) != 'nl':
                cleaned_newline = True
        return cleaned_newline
    #@+node:ekr.20200107165250.32: *5* orange.colon
    def colon(self, val):
        """Handle a colon."""

        def is_expr(node):
            """True if node is any expression other than += number."""
            if isinstance(node, (ast.BinOp, ast.Call, ast.IfExp)):
                return True
            return isinstance(
                node, ast.UnaryOp) and not isinstance(node.operand, ast.Num)

        node = self.token.node
        self.clean('blank')
        if not isinstance(node, ast.Slice):
            self.add_token('op', val)
            self.blank()
            return
        # A slice.
        lower = getattr(node, 'lower', None)
        upper = getattr(node, 'upper', None)
        step = getattr(node, 'step', None)
        if any(is_expr(z) for z in (lower, upper, step)):
            prev = self.code_list[-1]
            if prev.value not in '[:':
                self.blank()
            self.add_token('op', val)
            self.blank()
        else:
            self.add_token('op-no-blanks', val)
    #@+node:ekr.20200107165250.33: *5* orange.line_end
    def line_end(self):
        """Add a line-end request to the code list."""
        # This should be called only be do_newline and do_nl.
        node, token = self.token.statement_node, self.token
        assert token.kind in ('newline', 'nl'), (token.kind, g.callers())
        # Create the 'line-end' output token.
        self.add_line_end()
        # Attempt to split the line.
        was_split = self.split_line(node, token)
        # Attempt to join the line only if it has not just been split.
        if not was_split and self.max_join_line_length > 0:
            self.join_lines(node, token)
        self.line_indent()
            # Add the indentation for all lines
            # until the next indent or unindent token.
    #@+node:ekr.20200107165250.40: *5* orange.line_indent
    def line_indent(self):
        """Add a line-indent token."""
        self.clean('line-indent')
            # Defensive. Should never happen.
        self.add_token('line-indent', self.lws)
    #@+node:ekr.20200107165250.41: *5* orange.lt & rt
    #@+node:ekr.20200107165250.42: *6* orange.lt
    def lt(self, val):
        """Generate code for a left paren or curly/square bracket."""
        assert val in '([{', repr(val)
        if val == '(':
            self.paren_level += 1
        elif val == '[':
            self.square_brackets_stack.append(False)
        else:
            self.curly_brackets_level += 1
        self.clean('blank')
        prev = self.code_list[-1]
        if prev.kind in ('op', 'word-op'):
            self.blank()
            self.add_token('lt', val)
        elif prev.kind == 'word':
            # Only suppress blanks before '(' or '[' for non-keyworks.
            if val == '{' or prev.value in ('if', 'else', 'return', 'for'):
                self.blank()
            elif val == '(':
                self.in_arg_list += 1
            self.add_token('lt', val)
        else:
            self.clean('blank')
            self.add_token('op-no-blanks', val)
    #@+node:ekr.20200107165250.43: *6* orange.rt
    def rt(self, val):
        """Generate code for a right paren or curly/square bracket."""
        assert val in ')]}', repr(val)
        if val == ')':
            self.paren_level -= 1
            self.in_arg_list = max(0, self.in_arg_list - 1)
        elif val == ']':
            self.square_brackets_stack.pop()
        else:
            self.curly_brackets_level -= 1
        self.clean('blank')
        self.add_token('rt', val)
    #@+node:ekr.20200107165250.45: *5* orange.possible_unary_op & unary_op
    def possible_unary_op(self, s):
        """Add a unary or binary op to the token list."""
        node = self.token.node
        self.clean('blank')
        if isinstance(node, ast.UnaryOp):
            self.unary_op(s)
        else:
            self.blank()
            self.add_token('op', s)
            self.blank()

    def unary_op(self, s):
        """Add an operator request to the code list."""
        assert s and isinstance(s, str), repr(s)
        self.clean('blank')
        prev = self.code_list[-1]
        if prev.kind == 'lt':
            self.add_token('unary-op', s)
        else:
            self.blank()
            self.add_token('unary-op', s)
    #@+node:ekr.20200107165250.46: *5* orange.star_op
    def star_op(self):
        """Put a '*' op, with special cases for *args."""
        val = '*'
        self.clean('blank')
        if self.paren_level > 0:
            prev = self.code_list[-1]
            if prev.kind == 'lt' or (prev.kind, prev.value) == ('op', ','):
                self.blank()
                self.add_token('op', val)
                return
        self.blank()
        self.add_token('op', val)
        self.blank()
    #@+node:ekr.20200107165250.47: *5* orange.star_star_op
    def star_star_op(self):
        """Put a ** operator, with a special case for **kwargs."""
        val = '**'
        self.clean('blank')
        if self.paren_level > 0:
            prev = self.code_list[-1]
            if prev.kind == 'lt' or (prev.kind, prev.value) == ('op', ','):
                self.blank()
                self.add_token('op', val)
                return
        self.blank()
        self.add_token('op', val)
        self.blank()
    #@+node:ekr.20200107165250.48: *5* orange.word & word_op
    def word(self, s):
        """Add a word request to the code list."""
        assert s and isinstance(s, str), repr(s)
        if self.square_brackets_stack:
            # A previous 'op-no-blanks' token may cancel this blank.
            self.blank()
            self.add_token('word', s)
        elif self.in_arg_list > 0:
            self.add_token('word', s)
            self.blank()
        else:
            self.blank()
            self.add_token('word', s)
            self.blank()

    def word_op(self, s):
        """Add a word-op request to the code list."""
        assert s and isinstance(s, str), repr(s)
        self.blank()
        self.add_token('word-op', s)
        self.blank()
    #@+node:ekr.20200118120049.1: *4* orange: Split/join
    #@+node:ekr.20200107165250.34: *5* orange.split_line & helpers
    def split_line(self, node, token):
        """
        Split token's line, if possible and enabled.

        Return True if the line was broken into two or more lines.
        """
        assert token.kind in ('newline', 'nl'), repr(token)
        # Return if splitting is disabled:
        if self.max_split_line_length <= 0:  # pragma: no cover (user option)
            return False
        # Return if the node can't be split.
        if not is_long_statement(node):
            return False
        # Find the *output* tokens of the previous lines.
        line_tokens = self.find_prev_line()
        line_s = ''.join([z.to_string() for z in line_tokens])
        # Do nothing for short lines.
        if len(line_s) < self.max_split_line_length:
            return False
        # Return if the previous line has no opening delim: (, [ or {.
        if not any(z.kind == 'lt' for z in line_tokens):  # pragma: no cover (defensive)
            return False
        prefix = self.find_line_prefix(line_tokens)
        # Calculate the tail before cleaning the prefix.
        tail = line_tokens[len(prefix) :]
        # Cut back the token list: subtract 1 for the trailing line-end.
        self.code_list = self.code_list[: len(self.code_list) - len(line_tokens) - 1]
        # Append the tail, splitting it further, as needed.
        self.append_tail(prefix, tail)
        # Add the line-end token deleted by find_line_prefix.
        self.add_token('line-end', '\n')
        return True
    #@+node:ekr.20200107165250.35: *6* orange.append_tail
    def append_tail(self, prefix, tail):
        """Append the tail tokens, splitting the line further as necessary."""
        tail_s = ''.join([z.to_string() for z in tail])
        if len(tail_s) < self.max_split_line_length:
            # Add the prefix.
            self.code_list.extend(prefix)
            # Start a new line and increase the indentation.
            self.add_token('line-end', '\n')
            self.add_token('line-indent', self.lws + ' ' * 4)
            self.code_list.extend(tail)
            return
        # Still too long.  Split the line at commas.
        self.code_list.extend(prefix)
        # Start a new line and increase the indentation.
        self.add_token('line-end', '\n')
        self.add_token('line-indent', self.lws + ' ' * 4)
        open_delim = Token(kind='lt', value=prefix[-1].value)
        value = open_delim.value.replace('(', ')').replace('[', ']').replace('{', '}')
        close_delim = Token(kind='rt', value=value)
        delim_count = 1
        lws = self.lws + ' ' * 4
        for i, t in enumerate(tail):
            if t.kind == 'op' and t.value == ',':
                if delim_count == 1:
                    # Start a new line.
                    self.add_token('op-no-blanks', ',')
                    self.add_token('line-end', '\n')
                    self.add_token('line-indent', lws)
                    # Kill a following blank.
                    if i + 1 < len(tail):
                        next_t = tail[i + 1]
                        if next_t.kind == 'blank':
                            next_t.kind = 'no-op'
                            next_t.value = ''
                else:
                    self.code_list.append(t)
            elif t.kind == close_delim.kind and t.value == close_delim.value:
                # Done if the delims match.
                delim_count -= 1
                if delim_count == 0:
                    # Start a new line
                    self.add_token('op-no-blanks', ',')
                    self.add_token('line-end', '\n')
                    self.add_token('line-indent', self.lws)
                    self.code_list.extend(tail[i:])
                    return
                lws = lws[:-4]
                self.code_list.append(t)
            elif t.kind == open_delim.kind and t.value == open_delim.value:
                delim_count += 1
                lws = lws + ' ' * 4
                self.code_list.append(t)
            else:
                self.code_list.append(t)
        g.trace('BAD DELIMS', delim_count)
    #@+node:ekr.20200107165250.36: *6* orange.find_prev_line
    def find_prev_line(self):
        """Return the previous line, as a list of tokens."""
        line = []
        for t in reversed(self.code_list[:-1]):
            if t.kind in ('hard-newline', 'line-end'):
                break
            line.append(t)
        return list(reversed(line))
    #@+node:ekr.20200107165250.37: *6* orange.find_line_prefix
    def find_line_prefix(self, token_list):
        """
        Return all tokens up to and including the first lt token.
        Also add all lt tokens directly following the first lt token.
        """
        result = []
        for i, t in enumerate(token_list):
            result.append(t)
            if t.kind == 'lt':
                break
        return result
    #@+node:ekr.20200107165250.39: *5* orange.join_lines
    def join_lines(self, node, token):
        """
        Join preceding lines, if possible and enabled.
        token is a line_end token. node is the corresponding ast node.
        """
        if self.max_join_line_length <= 0:  # pragma: no cover (user option)
            return
        assert token.kind in ('newline', 'nl'), repr(token)
        if token.kind == 'nl':
            return
        # Scan backward in the *code* list,
        # looking for 'line-end' tokens with tok.newline_kind == 'nl'
        nls = 0
        i = len(self.code_list) - 1
        t = self.code_list[i]
        assert t.kind == 'line-end', repr(t)
        # Not all tokens have a newline_kind ivar.
        assert t.newline_kind == 'newline'  # type:ignore
        i -= 1
        while i >= 0:
            t = self.code_list[i]
            if t.kind == 'comment':
                # Can't join.
                return
            if t.kind == 'string' and not self.allow_joined_strings:
                # An EKR preference: don't join strings, no matter what black does.
                # This allows "short" f-strings to be aligned.
                return
            if t.kind == 'line-end':
                if getattr(t, 'newline_kind', None) == 'nl':
                    nls += 1
                else:
                    break  # pragma: no cover
            i -= 1
        # Retain at the file-start token.
        if i <= 0:
            i = 1
        if nls <= 0:  # pragma: no cover (rare)
            return
        # Retain line-end and and any following line-indent.
        # Required, so that the regex below won't eat too much.
        while True:
            t = self.code_list[i]
            if t.kind == 'line-end':
                if getattr(t, 'newline_kind', None) == 'nl':  # pragma: no cover (rare)
                    nls -= 1
                i += 1
            elif self.code_list[i].kind == 'line-indent':
                i += 1
            else:
                break  # pragma: no cover (defensive)
        if nls <= 0:  # pragma: no cover (defensive)
            return
        # Calculate the joined line.
        tail = self.code_list[i:]
        tail_s = tokens_to_string(tail)
        tail_s = re.sub(r'\n\s*', ' ', tail_s)
        tail_s = tail_s.replace('( ', '(').replace(' )', ')')
        tail_s = tail_s.rstrip()
        # Don't join the lines if they would be too long.
        if len(tail_s) > self.max_join_line_length:  # pragma: no cover (defensive)
            return
        # Cut back the code list.
        self.code_list = self.code_list[:i]
        # Add the new output tokens.
        self.add_token('string', tail_s)
        self.add_token('line-end', '\n')
    #@-others
#@+node:ekr.20200107170847.1: *3* class OrangeSettings
class OrangeSettings:

    pass
#@+node:ekr.20200107170126.1: *3* class ParseState
class ParseState:
    """
    A class representing items in the parse state stack.

    The present states:

    'file-start': Ensures the stack stack is never empty.

    'decorator': The last '@' was a decorator.

        do_op():    push_state('decorator')
        do_name():  pops the stack if state.kind == 'decorator'.

    'indent': The indentation level for 'class' and 'def' names.

        do_name():      push_state('indent', self.level)
        do_dendent():   pops the stack once or twice if state.value == self.level.

    """

    def __init__(self, kind, value):
        self.kind = kind
        self.value = value

    def __repr__(self):
        return f"State: {self.kind} {self.value!r}"

    __str__ = __repr__
#@+node:ekr.20200122033203.1: ** TOT classes...
#@+node:ekr.20191222083453.1: *3* class Fstringify (TOT)
class Fstringify(TokenOrderTraverser):
    """A class to fstringify files."""

    silent = True  # for pytest. Defined in all entries.
    line_number = 0
    line = ''

    #@+others
    #@+node:ekr.20191222083947.1: *4* fs.fstringify
    def fstringify(self, contents, filename, tokens, tree):
        """
        Fstringify.fstringify:

        f-stringify the sources given by (tokens, tree).

        Return the resulting string.
        """
        self.filename = filename
        self.tokens = tokens
        self.tree = tree
        # Prepass: reassign tokens.
        ReassignTokens().reassign(filename, tokens, tree)
        # Main pass.
        self.traverse(self.tree)
        results = tokens_to_string(self.tokens)
        return results
    #@+node:ekr.20200103054101.1: *4* fs.fstringify_file (entry)
    def fstringify_file(self, filename):  # pragma: no cover
        """
        Fstringify.fstringify_file.

        The entry point for the fstringify-file command.

        f-stringify the given external file with the Fstrinfify class.

        Return True if the file was changed.
        """
        tag = 'fstringify-file'
        self.filename = filename
        self.silent = False
        tog = TokenOrderGenerator()
        try:
            contents, encoding, tokens, tree = tog.init_from_file(filename)
            if not contents or not tokens or not tree:
                print(f"{tag}: Can not fstringify: {filename}")
                return False
            results = self.fstringify(contents, filename, tokens, tree)
        except Exception as e:
            print(e)
            return False
        # Something besides newlines must change.
        changed = regularize_nls(contents) != regularize_nls(results)
        status = 'Wrote' if changed else 'Unchanged'
        print(f"{tag}: {status:>9}: {filename}")
        if changed:
            write_file(filename, results, encoding=encoding)
        return changed
    #@+node:ekr.20200103065728.1: *4* fs.fstringify_file_diff (entry)
    def fstringify_file_diff(self, filename):  # pragma: no cover
        """
        Fstringify.fstringify_file_diff.

        The entry point for the diff-fstringify-file command.

        Print the diffs that would resulf from the fstringify-file command.

        Return True if the file would be changed.
        """
        tag = 'diff-fstringify-file'
        self.filename = filename
        self.silent = False
        tog = TokenOrderGenerator()
        try:
            contents, encoding, tokens, tree = tog.init_from_file(filename)
            if not contents or not tokens or not tree:
                return False
            results = self.fstringify(contents, filename, tokens, tree)
        except Exception as e:
            print(e)
            return False
        # Something besides newlines must change.
        changed = regularize_nls(contents) != regularize_nls(results)
        if changed:
            show_diffs(contents, results, filename=filename)
        else:
            print(f"{tag}: Unchanged: {filename}")
        return changed
    #@+node:ekr.20200112060218.1: *4* fs.fstringify_file_silent (entry)
    def fstringify_file_silent(self, filename):  # pragma: no cover
        """
        Fstringify.fstringify_file_silent.

        The entry point for the silent-fstringify-file command.

        fstringify the given file, suppressing all but serious error messages.

        Return True if the file would be changed.
        """
        self.filename = filename
        self.silent = True
        tog = TokenOrderGenerator()
        try:
            contents, encoding, tokens, tree = tog.init_from_file(filename)
            if not contents or not tokens or not tree:
                return False
            results = self.fstringify(contents, filename, tokens, tree)
        except Exception as e:
            print(e)
            return False
        # Something besides newlines must change.
        changed = regularize_nls(contents) != regularize_nls(results)
        status = 'Wrote' if changed else 'Unchanged'
        # Write the results.
        print(f"{status:>9}: {filename}")
        if changed:
            write_file(filename, results, encoding=encoding)
        return changed
    #@+node:ekr.20191222095754.1: *4* fs.make_fstring & helpers
    def make_fstring(self, node):
        """
        node is BinOp node representing an '%' operator.
        node.left is an ast.Str node.
        node.right reprsents the RHS of the '%' operator.

        Convert this tree to an f-string, if possible.
        Replace the node's entire tree with a new ast.Str node.
        Replace all the relevant tokens with a single new 'string' token.
        """
        trace = False
        assert isinstance(node.left, ast.Str), (repr(node.left), g.callers())
        # Careful: use the tokens, not Str.s.  This preserves spelling.
        lt_token_list = get_node_token_list(node.left, self.tokens)
        if not lt_token_list:  # pragma: no cover
            print('')
            g.trace('Error: no token list in Str')
            dump_tree(self.tokens, node)
            print('')
            return
        lt_s = tokens_to_string(lt_token_list)
        if trace:
            g.trace('lt_s:', lt_s)
        # Get the RHS values, a list of token lists.
        values = self.scan_rhs(node.right)
        if trace:
            for i, z in enumerate(values):
                dump_tokens(z, tag=f"RHS value {i}")
        # Compute rt_s, self.line and self.line_number for later messages.
        token0 = lt_token_list[0]
        self.line_number = token0.line_number
        self.line = token0.line.strip()
        rt_s = ''.join(tokens_to_string(z) for z in values)
        # Get the % specs in the LHS string.
        specs = self.scan_format_string(lt_s)
        if len(values) != len(specs):  # pragma: no cover
            self.message(
                f"can't create f-fstring: {lt_s!r}\n"
                f":f-string mismatch: "
                f"{len(values)} value{g.plural(len(values))}, "
                f"{len(specs)} spec{g.plural(len(specs))}")
            return
        # Replace specs with values.
        results = self.substitute_values(lt_s, specs, values)
        result = self.compute_result(lt_s, results)
        if not result:
            return
        # Remove whitespace before ! and :.
        result = self.clean_ws(result)
        # Show the results
        if trace:  # pragma: no cover
            before = (lt_s + ' % ' + rt_s).replace('\n', '<NL>')
            after = result.replace('\n', '<NL>')
            self.message(
                f"trace:\n"
                f":from: {before!s}\n"
                f":  to: {after!s}")
        # Adjust the tree and the token list.
        self.replace(node, result, values)
    #@+node:ekr.20191222102831.3: *5* fs.clean_ws
    ws_pat = re.compile(r'(\s+)([:!][0-9]\})')

    def clean_ws(self, s):
        """Carefully remove whitespace before ! and : specifiers."""
        s = re.sub(self.ws_pat, r'\2', s)
        return s
    #@+node:ekr.20191222102831.4: *5* fs.compute_result & helpers
    def compute_result(self, lt_s, tokens):
        """
        Create the final result, with various kinds of munges.

        Return the result string, or None if there are errors.
        """
        # Fail if there is a backslash within { and }.
        if not self.check_back_slashes(lt_s, tokens):
            return None  # pragma: no cover
        # Ensure consistent quotes.
        if not self.change_quotes(lt_s, tokens):
            return None  # pragma: no cover
        return tokens_to_string(tokens)
    #@+node:ekr.20200215074309.1: *6* fs.check_back_slashes
    def check_back_slashes(self, lt_s, tokens):
        """
        Return False if any backslash appears with an {} expression.

        Tokens is a list of lokens on the RHS.
        """
        count = 0
        for z in tokens:
            if z.kind == 'op':
                if z.value == '{':
                    count += 1
                elif z.value == '}':
                    count -= 1
            if (count % 2) == 1 and '\\' in z.value:
                if not self.silent:
                    self.message(  # pragma: no cover (silent during unit tests)
                        f"can't create f-fstring: {lt_s!r}\n"
                        f":backslash in {{expr}}:")
                return False
        return True
    #@+node:ekr.20191222102831.7: *6* fs.change_quotes
    def change_quotes(self, lt_s, aList):
        """
        Carefully check quotes in all "inner" tokens as necessary.

        Return False if the f-string would contain backslashes.

        We expect the following "outer" tokens.

        aList[0]:  ('string', 'f')
        aList[1]:  ('string',  a single or double quote.
        aList[-1]: ('string', a single or double quote matching aList[1])
        """
        # Sanity checks.
        if len(aList) < 4:
            return True  # pragma: no cover (defensive)
        if not lt_s:  # pragma: no cover (defensive)
            self.message("can't create f-fstring: no lt_s!")
            return False
        delim = lt_s[0]
        # Check tokens 0, 1 and -1.
        token0 = aList[0]
        token1 = aList[1]
        token_last = aList[-1]
        for token in token0, token1, token_last:
            # These are the only kinds of tokens we expect to generate.
            ok = (
                token.kind == 'string' or
                token.kind == 'op' and token.value in '{}')
            if not ok:  # pragma: no cover (defensive)
                self.message(
                    f"unexpected token: {token.kind} {token.value}\n"
                    f":           lt_s: {lt_s!r}")
                return False
        # These checks are important...
        if token0.value != 'f':
            return False  # pragma: no cover (defensive)
        val1 = token1.value
        if delim != val1:
            return False  # pragma: no cover (defensive)
        val_last = token_last.value
        if delim != val_last:
            return False  # pragma: no cover (defensive)
        #
        # Check for conflicting delims, preferring f"..." to f'...'.
        for delim in ('"', "'"):
            aList[1] = aList[-1] = Token('string', delim)
            for z in aList[2:-1]:
                if delim in z.value:
                    break
            else:
                return True
        if not self.silent:  # pragma: no cover (silent unit test)
            self.message(
                f"can't create f-fstring: {lt_s!r}\n"
                f":   conflicting delims:")
        return False
    #@+node:ekr.20191222102831.6: *5* fs.munge_spec
    def munge_spec(self, spec):
        """
        Return (head, tail).

        The format is spec !head:tail or :tail

        Example specs: s2, r3
        """
        # To do: handle more specs.
        head, tail = [], []
        if spec.startswith('+'):
            pass  # Leave it alone!
        elif spec.startswith('-'):
            tail.append('>')
            spec = spec[1:]
        if spec.endswith('s'):
            spec = spec[:-1]
        if spec.endswith('r'):
            head.append('r')
            spec = spec[:-1]
        tail_s = ''.join(tail) + spec
        head_s = ''.join(head)
        return head_s, tail_s
    #@+node:ekr.20191222102831.9: *5* fs.scan_format_string
    # format_spec ::=  [[fill]align][sign][#][0][width][,][.precision][type]
    # fill        ::=  <any character>
    # align       ::=  "<" | ">" | "=" | "^"
    # sign        ::=  "+" | "-" | " "
    # width       ::=  integer
    # precision   ::=  integer
    # type        ::=  "b" | "c" | "d" | "e" | "E" | "f" | "F" | "g" | "G" | "n" | "o" | "s" | "x" | "X" | "%"

    format_pat = re.compile(r'%(([+-]?[0-9]*(\.)?[0.9]*)*[bcdeEfFgGnoxrsX]?)')

    def scan_format_string(self, s):
        """Scan the format string s, returning a list match objects."""
        result = list(re.finditer(self.format_pat, s))
        return result
    #@+node:ekr.20191222104224.1: *5* fs.scan_rhs
    def scan_rhs(self, node):
        """
        Scan the right-hand side of a potential f-string.

        Return a list of the token lists for each element.
        """
        trace = False
        # First, Try the most common cases.
        if isinstance(node, ast.Str):
            token_list = get_node_token_list(node, self.tokens)
            return [token_list]
        if isinstance(node, (list, tuple, ast.Tuple)):
            result = []
            elts = node.elts if isinstance(node, ast.Tuple) else node
            for i, elt in enumerate(elts):
                tokens = tokens_for_node(self.filename, elt, self.tokens)
                result.append(tokens)
                if trace:
                    g.trace(f"item: {i}: {elt.__class__.__name__}")
                    g.printObj(tokens, tag=f"Tokens for item {i}")
            return result
        # Now we expect only one result.
        tokens = tokens_for_node(self.filename, node, self.tokens)
        return [tokens]
    #@+node:ekr.20191226155316.1: *5* fs.substitute_values
    def substitute_values(self, lt_s, specs, values):
        """
        Replace specifiers with values in lt_s string.

        Double { and } as needed.
        """
        i, results = 0, [Token('string', 'f')]
        for spec_i, m in enumerate(specs):
            value = tokens_to_string(values[spec_i])
            start, end, spec = m.start(0), m.end(0), m.group(1)
            if start > i:
                val = lt_s[i:start].replace('{', '{{').replace('}', '}}')
                results.append(Token('string', val[0]))
                results.append(Token('string', val[1:]))
            head, tail = self.munge_spec(spec)
            results.append(Token('op', '{'))
            results.append(Token('string', value))
            if head:
                results.append(Token('string', '!'))
                results.append(Token('string', head))
            if tail:
                results.append(Token('string', ':'))
                results.append(Token('string', tail))
            results.append(Token('op', '}'))
            i = end
        # Add the tail.
        tail = lt_s[i:]
        if tail:
            tail = tail.replace('{', '{{').replace('}', '}}')
            results.append(Token('string', tail[:-1]))
            results.append(Token('string', tail[-1]))
        return results
    #@+node:ekr.20200214142019.1: *4* fs.message
    def message(self, message):  # pragma: no cover.
        """
        Print one or more message lines aligned on the first colon of the message.
        """
        # Print a leading blank line.
        print('')
        # Calculate the padding.
        lines = g.splitLines(message)
        pad = max(lines[0].find(':'), 30)
        # Print the first line.
        z = lines[0]
        i = z.find(':')
        if i == -1:
            print(z.rstrip())
        else:
            print(f"{z[:i+2].strip():>{pad+1}} {z[i+2:].strip()}")
        # Print the remaining message lines.
        for z in lines[1:]:
            if z.startswith('<'):
                # Print left aligned.
                print(z[1:].strip())
            elif z.startswith(':') and -1 < z[1:].find(':') <= pad:
                # Align with the first line.
                i = z[1:].find(':')
                print(f"{z[1:i+2].strip():>{pad+1}} {z[i+2:].strip()}")
            elif z.startswith('>'):
                # Align after the aligning colon.
                print(f"{' ':>{pad+2}}{z[1:].strip()}")
            else:
                # Default: Put the entire line after the aligning colon.
                print(f"{' ':>{pad+2}}{z.strip()}")
        # Print the standard message lines.
        file_s = f"{'file':>{pad}}"
        ln_n_s = f"{'line number':>{pad}}"
        line_s = f"{'line':>{pad}}"
        print(
            f"{file_s}: {self.filename}\n"
            f"{ln_n_s}: {self.line_number}\n"
            f"{line_s}: {self.line!r}")
    #@+node:ekr.20191225054848.1: *4* fs.replace
    def replace(self, node, s, values):
        """
        Replace node with an ast.Str node for s.
        Replace all tokens in the range of values with a single 'string' node.
        """
        # Replace the tokens...
        tokens = tokens_for_node(self.filename, node, self.tokens)
        i1 = i = tokens[0].index
        replace_token(self.tokens[i], 'string', s)
        j = 1
        while j < len(tokens):
            replace_token(self.tokens[i1 + j], 'killed', '')
            j += 1
        # Replace the node.
        new_node = ast.Str()
        new_node.s = s
        replace_node(new_node, node)
        # Update the token.
        token = self.tokens[i1]
        token.node = new_node  # type:ignore
        # Update the token list.
        add_token_to_token_list(token, new_node)
    #@+node:ekr.20191231055008.1: *4* fs.visit
    def visit(self, node):
        """
        FStringify.visit. (Overrides TOT visit).

        Call fs.makes_fstring if node is a BinOp that might be converted to an
        f-string.
        """
        if (
            isinstance(node, ast.BinOp)
            and op_name(node.op) == '%'
            and isinstance(node.left, ast.Str)
        ):
            self.make_fstring(node)
    #@-others
#@+node:ekr.20191231084514.1: *3* class ReassignTokens (TOT)
class ReassignTokens(TokenOrderTraverser):
    """A class that reassigns tokens to more appropriate ast nodes."""
    #@+others
    #@+node:ekr.20191231084640.1: *4* reassign.reassign
    def reassign(self, filename, tokens, tree):
        """The main entry point."""
        self.filename = filename
        self.tokens = tokens
        self.tree = tree
        self.traverse(tree)
    #@+node:ekr.20191231084853.1: *4* reassign.visit
    def visit(self, node):
        """ReassignTokens.visit"""
        # For now, just handle call nodes.
        if not isinstance(node, ast.Call):
            return
        tokens = tokens_for_node(self.filename, node, self.tokens)
        node0, node9 = tokens[0].node, tokens[-1].node
        nca = nearest_common_ancestor(node0, node9)
        if not nca:
            return
        # g.trace(f"{self.filename:20} nca: {nca.__class__.__name__}")
        # Associate () with the call node.
        i = tokens[-1].index
        j = find_paren_token(i + 1, self.tokens)
        if j is None:
            return  # pragma: no cover
        k = find_paren_token(j + 1, self.tokens)
        if k is None:
            return  # pragma: no cover
        self.tokens[j].node = nca  # type:ignore
        self.tokens[k].node = nca  # type:ignore
        add_token_to_token_list(self.tokens[j], nca)
        add_token_to_token_list(self.tokens[k], nca)
    #@-others
#@+node:ekr.20191227170803.1: ** Token classes
#@+node:ekr.20191110080535.1: *3* class Token
class Token:
    """
    A class representing a 5-tuple, plus additional data.

    The TokenOrderTraverser class creates a list of such tokens.
    """

    def __init__(self, kind, value):

        self.kind = kind
        self.value = value
        #
        # Injected by Tokenizer.add_token.
        self.five_tuple = None
        self.index = 0
        self.line = ''
            # The entire line containing the token.
            # Same as five_tuple.line.
        self.line_number = 0
            # The line number, for errors and dumps.
            # Same as five_tuple.start[0]
        #
        # Injected by Tokenizer.add_token.
        self.level = 0
        self.node = None

    def __repr__(self):
        nl_kind = getattr(self, 'newline_kind', '')
        s = f"{self.kind:}.{self.index:<3}"
        return f"{s:>18}:{nl_kind:7} {self.show_val(80)}"

    def __str__(self):
        nl_kind = getattr(self, 'newline_kind', '')
        return f"{self.kind}.{self.index:<3}{nl_kind:8} {self.show_val(80)}"

    def to_string(self):
        """Return the contribution of the token to the source file."""
        return self.value if isinstance(self.value, str) else ''
    #@+others
    #@+node:ekr.20191231114927.1: *4* token.brief_dump
    def brief_dump(self):  # pragma: no cover
        """Dump a token."""
        return (
            f"{self.index:>3} line: {self.line_number:<2} "
            f"{self.kind:>11} {self.show_val(100)}")
    #@+node:ekr.20200223022950.11: *4* token.dump
    def dump(self):  # pragma: no cover
        """Dump a token and related links."""
        # Let block.
        node_id = self.node.node_index if self.node else ''
        node_cn = self.node.__class__.__name__ if self.node else ''
        return (
            f"{self.line_number:4} "
            f"{node_id:5} {node_cn:16} "
            f"{self.index:>5} {self.kind:>11} "
            f"{self.show_val(100)}")
    #@+node:ekr.20200121081151.1: *4* token.dump_header
    def dump_header(self):  # pragma: no cover
        """Print the header for token.dump"""
        print(
            f"\n"
            f"         node    {'':10} token          token\n"
            f"line index class {'':10} index        kind value\n"
            f"==== ===== ===== {'':10} =====        ==== =====\n")
    #@+node:ekr.20191116154328.1: *4* token.error_dump
    def error_dump(self):  # pragma: no cover
        """Dump a token or result node for error message."""
        if self.node:
            node_id = obj_id(self.node)
            node_s = f"{node_id} {self.node.__class__.__name__}"
        else:
            node_s = "None"
        return (
            f"index: {self.index:<3} {self.kind:>12} {self.show_val(20):<20} "
            f"{node_s}")
    #@+node:ekr.20191113095507.1: *4* token.show_val
    def show_val(self, truncate_n):  # pragma: no cover
        """Return the token.value field."""
        if self.kind in ('ws', 'indent'):
            val = len(self.value)
        elif self.kind == 'string':
            # Important: don't add a repr for 'string' tokens.
            # repr just adds another layer of confusion.
            val = g.truncate(self.value, truncate_n)  # type:ignore
        else:
            val = g.truncate(repr(self.value), truncate_n)  # type:ignore
        return val
    #@-others
#@+node:ekr.20191110165235.1: *3* class Tokenizer
class Tokenizer:

    """Create a list of Tokens from contents."""

    results: List[Token] = []

    #@+others
    #@+node:ekr.20191110165235.2: *4* tokenizer.add_token
    token_index = 0
    prev_line_token = None

    def add_token(self, kind, five_tuple, line, s_row, value):
        """
        Add a token to the results list.

        Subclasses could override this method to filter out specific tokens.
        """
        tok = Token(kind, value)
        tok.five_tuple = five_tuple
        tok.index = self.token_index
        # Bump the token index.
        self.token_index += 1
        tok.line = line
        tok.line_number = s_row
        self.results.append(tok)
    #@+node:ekr.20191110170551.1: *4* tokenizer.check_results
    def check_results(self, contents):

        # Split the results into lines.
        result = ''.join([z.to_string() for z in self.results])
        result_lines = g.splitLines(result)
        # Check.
        ok = result == contents and result_lines == self.lines
        assert ok, (
            f"\n"
            f"      result: {result!r}\n"
            f"    contents: {contents!r}\n"
            f"result_lines: {result_lines}\n"
            f"       lines: {self.lines}"
        )
    #@+node:ekr.20191110165235.3: *4* tokenizer.create_input_tokens
    def create_input_tokens(self, contents, tokens):
        """
        Generate a list of Token's from tokens, a list of 5-tuples.
        """
        # Create the physical lines.
        self.lines = contents.splitlines(True)
        # Create the list of character offsets of the start of each physical line.
        last_offset, self.offsets = 0, [0]
        for line in self.lines:
            last_offset += len(line)
            self.offsets.append(last_offset)
        # Handle each token, appending tokens and between-token whitespace to results.
        self.prev_offset, self.results = -1, []
        for token in tokens:
            self.do_token(contents, token)
        # Print results when tracing.
        self.check_results(contents)
        # Return results, as a list.
        return self.results
    #@+node:ekr.20191110165235.4: *4* tokenizer.do_token (the gem)
    header_has_been_shown = False

    def do_token(self, contents, five_tuple):
        """
        Handle the given token, optionally including between-token whitespace.

        This is part of the "gem".

        Links:

        - 11/13/19: ENB: A much better untokenizer
          https://groups.google.com/forum/#!msg/leo-editor/DpZ2cMS03WE/VPqtB9lTEAAJ

        - Untokenize does not round-trip ws before bs-nl
          https://bugs.python.org/issue38663
        """
        import token as token_module
        # Unpack..
        tok_type, val, start, end, line = five_tuple
        s_row, s_col = start  # row/col offsets of start of token.
        e_row, e_col = end  # row/col offsets of end of token.
        kind = token_module.tok_name[tok_type].lower()
        # Calculate the token's start/end offsets: character offsets into contents.
        s_offset = self.offsets[max(0, s_row - 1)] + s_col
        e_offset = self.offsets[max(0, e_row - 1)] + e_col
        # tok_s is corresponding string in the line.
        tok_s = contents[s_offset:e_offset]
        # Add any preceding between-token whitespace.
        ws = contents[self.prev_offset:s_offset]
        if ws:
            # No need for a hook.
            self.add_token('ws', five_tuple, line, s_row, ws)
        # Always add token, even if it contributes no text!
        self.add_token(kind, five_tuple, line, s_row, tok_s)
        # Update the ending offset.
        self.prev_offset = e_offset
    #@-others
#@-others
g = LeoGlobals()
if __name__ == '__main__':
    main()
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
