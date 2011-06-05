# 
# Copyright (c) 2011 Andrew Hadinyoto - https://github.com/ahadinyoto
#
# Licensed under GNU General Public License version 2.0 and above
# 

import re
import common

def convert(text, attrib=None, withlineno=False):
    output = """<div class="%s">%s</div>"""

    class_attrib = attrib
    if attrib:
        attribs = attrib.split(",")
        if len(attribs) > 1:
            return common.multi_attrib_error("info", text)
        # attribs = [ i.strip() for i in attribs ]
        class_attrib = re.sub(r"@(\w+)", r"info-\1", attribs[0])
    else:
        class_attrib = "info"

    return output % (class_attrib, text.strip())
