# 
# Copyright (c) 2011 Andrew Hadinyoto - https://github.com/ahadinyoto
#
# Licensed under GNU General Public License version 2.0 and above
# 

import re
import common

def convert(text, attrib=None, withlineno=False):
    output = """<div class="%s">%s</div>"""
    return output % ('powershell', text.strip())
