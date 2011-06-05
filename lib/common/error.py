import re

def multi_attrib_error(module, text) :
    output = """<div class="%s">%s</div>"""
    text = re.sub(r"\r\n|\n", "", text[0:20])
    print "* Error: '%s' with text: %s...\n" % (module, text[0:20])
    return output % ("general-error", "Error! Multiple attributes for '%s' with text => %s ..." % (module,text[0:20]))       

def no_attrib_error(module, text):
    output = """<div class="%s">%s</div>"""
    text = re.gsub(r"\r\n|\n", "", text[0:20])
    print "* Error: '%s' with text: %s...\n" % (module, text[0:20])
    return output % ("general-error", "Error! No attribue is found for '%s' with text => %s ..." % (module,text[0:20]))       
