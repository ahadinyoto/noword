h1. Code

bc.. {- python -}
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
            element = html.fromstring(html_code)
            codes_pre_parent = codes[0].getparent()
            codes_pre_grandparent = codes_pre_parent.getparent()
            codes_pre_grandparent.replace(codes_pre_parent, element)

        data = { "content": model.doc_tostring(), "theme": theme }
        data.update(vartorender)
        return view.render(data)
            
class Tedi:
    """A wrapper class to manage files and outputs"""

    def get_result(self):
        return self.result

    def write(self, stream=sys.stdout):
        stream.write(self.result)

    def convert(self, filename, data={}, theme="default", output=sys.stdout):
        try:
            con = Controller()
            self.result = con.process(filename, vartorender=data)
            output.write(self.result)
        except Exception, ex:
            logging.error(ex)

    # Todo: broken. Needs publishing mechanism (can't handle recursive dir yet)
    def publish(self, indir, outdir, data={}, theme="default"):

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

        # update data with converted files (in lexical order of given by txl files)
        # navlist[0] => htmlfile name
        # navlist[1] => docname (html file without .html extension)
        data.update({"navlist": [ (i[1],i[2]) for i in txlfiles]})

        for f in txlfiles:
            # f[0] => txl file, f[1] => html file, f[2] => docname
            outf = open("%s/%s" % (outdir, f[1]), "wb")
            data.update({"current" : f[2]})
            self.convert("%s/%s" % (indir, f[0]), data, theme, outf)

        # sanity check not to delete the current directories that contain the to be processed TXL files
        curdir = os.getcwd()
        if outdir.startswith(curdir):
            logging.error("Target is the current directory. Aborted!")
            return False

        # calling "rmtree", so you know it's dangerous
        codepath = os.path.dirname(sys.argv[0])
        if len(codepath) == 0:
            codepath = "."
        srctheme = "%s/themes/%s" % (codepath, theme)
        outtheme = "%s/themes/%s" % (outdir, theme)
        if (os.path.exists(outtheme)):
            shutil.rmtree(outtheme)

        print srctheme, "=", outtheme
        shutil.copytree(srctheme, outtheme)


if __name__ == '__main__':
    t = Tedi()
    data = {    "course_title": "C105 Introduction to Programming",
                "lesson_title": "Intro to Python",
                "lesson_part" : "Week 1",
                "footer_col1_title": "About Python",
                "footer_col1" : [("Official Python Website", "http://python.org"),
                                 ("Python Documentation", "http://docs.python.org")
                                ],
                "footer_col2_title": "Learning Python",
                "footer_col2" : [("Python Tutorial", "http://docs.python.org/tutorial/"),
                                 ("Think Python", "http://www.openbookproject.net/thinkcs/python/english2e/"),                                ("Dive Into Python", "http://diveintopython.org/")
                                ],
                "footer_col3_title": "Fun with Python",
                "footer_col3" : [("PySchools", "http://www.pyschools.com/"),
                                 ("SingPath", "http://www.singpath.com/")
                                ]
           }

    t.publish("test/publish", "/tmp/txlout", data = data)
    # t.convert("file:///./test/samples/1_nocode.txl")
    # t.convert("file:///./test/samples/2_withcode.txl")
    # t.convert("file:///./test/samples/3_multicode.txl")
    # t.convert("file:///./test/samples/4_prenocode.txl")

p. Ok

bc.. {- python -}
print "hello"
a = 5

print a
