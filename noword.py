#!/usr/bin/env python
#
# noword.py: a simple textile to HTML generator
# 
# Copyright (c) 2011 Andrew Hadinyoto - https://github.com/ahadinyoto
#
# Licensed under GNU General Public License version 2.0 and above
# 

LIB_PATH = "lib"

import sys
sys.path.insert(0, LIB_PATH)

import os
import os.path
import textile
import re
import logging
import shutil
import traceback
import time
import types
import argparse
import pprint
import zipfile

from lxml import etree, html
from StringIO import StringIO
from jinja2 import Template, FileSystemLoader, Environment

# Manifest name for HTML5 manifest
MANIFEST_NAME = "noword.manifest"
WEBSERVER_CONFIG = "%s/apache/.htaccess" % LIB_PATH

def get_exec_path():
    dirname = os.path.dirname(sys.argv[0])
    _path = "."
    if len(dirname) > 0:
        _path = dirname 
    return _path

class Model:
    """The class that handles textile and its conversion to DOM"""
    
    def __init__(self, filename):
        self.textile_string = open(filename, "rb").read()
        self.html = textile.textile(self.textile_string)
        self.doc = html.fromstring(self.html)

    def get_all_codes(self):
        """Get all <pre><code>... """
        pres = self.doc.xpath("//pre")
        prelist = []
        for pre in pres:
            code = pre.xpath("./code")
            if len(code):
               prelist.append(code)

        # returns codes in all pres (grouped)
        # [ [<elem code>, <elem code>], [<elem code] ]
        return prelist

    def remove_code_tags_in_pre(self, pre):
        """Cleanup muliple "<code>" per "<pre>"
        So, "<pre><code>" becomes "<pre>"
        """
        codetext = ""
        for child in pre:
            codetext += child.text + "\n"

        return codetext

    def doc_tostring(self):
        """Return the entire HTML file converted from textile."""
        htmlstr = ""

        # lxml attach <div> as parent by default which is not needed. Below is to extract the children."
        for child in self.doc:
            htmlstr += html.tostring(child)

        return htmlstr


class View:
    """The class that handles processed DOM into its HTML view"""

    def __init__(self, theme="default"):
        self._path = get_exec_path()
        loader = FileSystemLoader("%s/themes/%s" % (self._path, theme))
        self.env = Environment(loader=loader)

    def add_wrapper(self, str):
        """Wrap both code and line numbers in a div block."""
        return "<div class=\"codeblock\">\n" + str + "</div>"

    def code_view(self, codetext, withlineno):
        """Syntax highlight the code. Either pygmentize or using custom lexer and formatter."""
        match = re.search(r"{-\s+(\w+)(@.*)?\s+-}", codetext)
        converted_text = ""
        if match:
            lf = match.group(1)
            attrib = match.group(2)
            sys.path.insert(0, "%s/lib" % self._path)
            module_ = __import__("%slf" % lf)
            codetext = re.sub(r"{-\s+\w+(@.*)?\s+-}", "", codetext)
            converted_text += module_.lexform.convert(codetext, attrib, withlineno)

        return converted_text

    def render(self, data, **params):
        template = self.env.get_template("_content.html")
        return template.render(data)
        

class Controller:
    """The logic that does the rest"""
    def __init__(self):
        pass

    def process(self, filename, vartorender={}, withlineno=True, theme="default"):
        model = Model(filename)
        view  = View(theme)
        pre_codes = model.get_all_codes()
        for codes in pre_codes:
            pre_no_codes = model.remove_code_tags_in_pre(codes)
            html_code = view.code_view(pre_no_codes, withlineno)

            # convert html_code to DOM elements to be reinserted back into the tree
            try:
                element = html.fromstring(html_code)
                codes_pre_parent = codes[0].getparent()
                codes_pre_grandparent = codes_pre_parent.getparent()
                codes_pre_grandparent.replace(codes_pre_parent, element)
            except Exception, ex:
                print "Error:", ex
                print "On text:", pre_no_codes

        data = { "content": model.doc_tostring(), "theme": theme }
        data.update(vartorender)
        return view.render(data)
            
class NoWord:
    """A wrapper class to manage files and outputs"""

    def get_result(self):
        return self.result

    def write(self, stream=sys.stdout):
        stream.write(self.result)

    def convert(self, filename, data={}, withlineno=True, theme="default", output=sys.stdout):
        try:
            con = Controller()
            self.result = con.process(filename, withlineno=withlineno, vartorender=data)
            output.write(self.result)
        except Exception, ex:
            traceback.print_exc(file=sys.stdout)    
            logging.error(ex)

    def find_dir(self, directory):
        """Behaves like Unix find -type f /dir, except it'll strip out the directory"""
        files = ""
        for d in os.walk(directory):
            for f in d[2]:
                if f.startswith(".") or f.endswith(".manifest"):
                    continue
                    
                s = "%s/%s" % (d[0], f)
                if os.path.isdir(s):
                    continue

                files += re.sub(directory + "/", "", s) + "\n"
        return files 


    def create_manifest(self, outdir, mfname=MANIFEST_NAME):
        timestamp = "%s - %s" % (time.asctime(), time.time())  
        mf = "CACHE MANIFEST\n"
        mf += "# %s\n" % timestamp
        files = self.find_dir(outdir)
        f = open("%s/%s" % (outdir, mfname), "wb")
        f.write(mf)
        f.write(files)

    def config_webserver(self, outdir, config=WEBSERVER_CONFIG):
        _path = get_exec_path()
        shutil.copy("%s/%s" % (_path, WEBSERVER_CONFIG), outdir)

    def __read_conf(self, confname='conf'):
        data = {}
        sys.path.insert(0, self.indir)
        try:
            conf = __import__('conf')
            for i in dir(conf):
                if i.startswith("__") and i.endswith("__"):
                    continue
                attr = getattr(conf, i)
                if type(attr) == types.StringType:
                    data[i] = attr
                elif type(attr) in [types.TupleType, types.ListType]:
                    data[i] = attr
        except ImportError, ex:
            print "Config not found - %s" % ex.message
            pass

        try:
            os.remove("%s/%s.pyc" % (self.indir, confname))    
        except:
            pass

        sys.path.pop(0) 
        return data

    # Todo: broken. Needs publishing mechanism (can't handle recursive dir yet)
    def publish(self, indir, outdir): 
        self.indir = indir
        self.outdir = outdir

        if (not os.path.exists(outdir)):
            os.mkdir(outdir)

        txlfiles = []
        for f in os.listdir(indir):
            if os.path.isfile(indir + "/" + f) and f.endswith(".txl"):
                m = re.search(r"^(\d+_)?(\w+).txl$", f)
                docname = m.group(2)
                htmlfile = docname + ".html"
                txlfiles.append( (f, htmlfile, docname) )
            elif os.path.isdir(indir + "/" + f):
                if os.path.exists("%s/%s" % (outdir, f)):
                    shutil.rmtree("%s/%s" % (outdir, f))
                shutil.copytree("%s/%s" % (indir, f), "%s/%s" % (outdir, f) )

        data = self.__read_conf()
        # update data with converted files (in lexical order of txl file names)
        # navlist[0] => htmlfile name
        # navlist[1] => docname (html file without .html extension)
        data.update({"navlist": [ (i[1],i[2]) for i in txlfiles]})
        theme = "default"
        if data.has_key("theme") and len(data['theme']) > 0:
            theme = data['theme']
        print "Using theme: %s" % theme

        for f in txlfiles:
            # f[0] => txl file, f[1] => html file, f[2] => docname
            print "Processing: %s\n .. Output: %s" % (f[0], f[1])
            outf = open("%s/%s" % (outdir, f[1]), "wb")
            data.update({"current" : f[2]})
            self.convert("%s/%s" % (indir, f[0]), data, theme=theme, output=outf)

        # sanity check not to delete the current directories that contain the to be processed TXL files
        curdir = os.getcwd()
        if outdir.startswith(curdir):
            logging.error("Target is the current directory. Aborted!")
            return False

        # calling "rmtree", so you know it's dangerous
        _path = get_exec_path()
        srctheme = "%s/themes/%s" % (_path, theme)
        outtheme = "%s/themes/%s" % (outdir, theme)
        if (os.path.exists(outtheme)):
            shutil.rmtree(outtheme)

        shutil.copytree(srctheme, outtheme)

        srclib = "%s/%s/js" % (_path, LIB_PATH) # , _path)
        outlib = "%s/%s/js" % (outdir, LIB_PATH)

        if (os.path.exists(outlib)):
            shutil.rmtree(outlib)

        shutil.copytree(srclib, outlib)

        self.create_manifest(outdir)
        self.config_webserver(outdir)

# -- Functions ---

def zipper(outdir, filename):
    """Zip the outdir by removing everything except for basename for dirname"""
    filelist = []
    dirname = os.path.dirname(outdir)

    if not filename.endswith(".zip"):
        filename += ".zip"

    try:
        for node in os.walk(outdir):
            if len(node[2]) > 0:
                for f in node[2]:
                    filelist.append(os.path.join(node[0],f))
            else:
                filelist.append(node[0])

        with zipfile.ZipFile(filename, "w") as z:
            for node in filelist:
                arcname = re.sub(r"%s/(.*)" % dirname, r"\1", node)
                z.write(node, arcname)

    except Exception, ex:
        print "ERROR! zipping file %s failed because %s" % (filename, ex)
    

if __name__ == '__main__':
    usage = """
    %prog -i inputdir -o outputdir [-z filename.zip]
    %prog --indir inputdir --outdir outputdir [--zip filename.zip]
    %prog -h 
    """
    op = argparse.ArgumentParser(description="Convert 'textile' to 'html' with some goodies.")
    op.add_argument("-i", "--indir", dest="indir", 
            help="Input directory containing .txl files, and it'll be processed recursively.")
    op.add_argument("-o", "--outdir", dest="outdir", 
            help="Output directory where the generated .html files will be stored")
    op.add_argument("-z", "--zip", dest="zipfile", 
            help="Compress the output as zip file.")

    has_opts = False
    if len(sys.argv) > 1:
        ns = op.parse_args()
        if ns.indir != None and ns.outdir != None:
            has_opts = True

    if not has_opts:
        print "\n* Errorr: missing argument. See the usage below.\n"
        op.print_help() 
        sys.exit(1)

    nw = NoWord()
    nw.publish(ns.indir, ns.outdir)

    zfile = None
    if ns.zipfile != None:
        zipper(ns.outdir, ns.zipfile)
        print "Zipping:", ns.zipfile

