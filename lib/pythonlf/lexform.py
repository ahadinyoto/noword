# 
# Copyright (c) 2011 Andrew Hadinyoto - https://github.com/ahadinyoto
#
# Licensed under GNU General Public License version 2.0 and above
# 

from common import add_lineno

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter


# The decision to have line number or not can be refactored to a config file or switch (todo)
def convert(text, attrib=None, withlineno=True):
    converted_text = highlight(text, PythonLexer(), HtmlFormatter())
    if withlineno:
        converted_text = add_lineno(converted_text)

    wrapped_text = """<div class="codeblock">\n%s\n</div>""" % converted_text 

    return wrapped_text
