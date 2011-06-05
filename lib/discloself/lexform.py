# 
# Copyright (c) 2011 Andrew Hadinyoto - https://github.com/ahadinyoto
#
# Licensed under GNU General Public License version 2.0 and above
# 

import random
import re
import string
import base64

# imported from "lib" folder
import slowaes as aes
import common

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

_EncryptedList = []

def _encrypt(key, plaintext):
    padsize = 16 - (len(key) % 16)
    padded_key = key + ("." * padsize)
    cipher = aes.encryptData(padded_key, plaintext) 
    cipher_text = base64.encodestring(cipher)
    return cipher_text

def _register(title, key, text):
    _EncryptedList.append((title, key, text)) 

def _print_encrypted_list():
    if len(_EncryptedList) > 0:
        print "Following 'disclose' texts are encrypted:\n"
        print "URL Title".center(20), "Key".center(11), "Sample text".center(30)
        print ("-"*20).ljust(20), ("-"*10).ljust(11), ("-"*30).ljust(30)
        for e in _EncryptedList:
            text = re.sub(r"\r\n|\n", " ", e[2])[0:30]
            title = e[0][0:19]
            print "%s %s  %s" % (str(e[0]).ljust(20), e[1].ljust(10), text)

        print "\n"

def convert(text, attrib=None, withlineno=False):

    # Generate random number for "div" id.
    # The same id is used to determine if decryption was successful.
    # This may collide for long time use. TODO: use hash.
    genid = random.randint(1, 1000000000)
    atext = "Hint"
    password  = None

    if attrib:
        attrib = re.sub(r"^@", "", attrib)
        attlist = attrib.split(",")

        if len(attlist) > 2:
            return common.multi_attrib_error("info", text) 

        attlist = map(string.strip, attlist)
        if len(attlist) == 1:
            attlist.append(None)

        (attrib_text, key) = attlist

        # Prepend the id. This id string will be compared after decryption to check if it's successful
        js_decrypt = "false"
        if key:
            text_with_id = ("{{%s}}" % genid) + text
            cipher_text = _encrypt(key, text_with_id)
            _register(attrib_text, key, text)
            text = cipher_text
            js_decrypt = "true"

    link = """<div class="disclose"><a class="disclose-link" href="javascript:void(0)" onclick="noword.handleDisclose('%s', %s);">%s</a>\n""" % (genid, js_decrypt, attrib_text)
    html = """
                <div class="disclose-key" id="%s-key">
                <input type="text" class="disclose-key-text" id="%s-key-text">
                <input type="button" value="decrypt" onclick="noword.decrypt('%s');">
                &nbsp;&nbsp;<span class="disclose-error" id="%s-error"></span>
                </div>\n
            """ % (genid, genid, genid, genid)
    html += """<div class="disclose-text" id="%s-text">\n%s\n</div>\n
               </div>\n
            """ % (genid, text)

    _print_encrypted_list()

    return link + html
