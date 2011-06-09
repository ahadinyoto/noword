import unittest
import sys
import shutil
import re

sys.path.insert(0,"..")
import noword

from lxml import etree, html

class TestTextileOutput(unittest.TestCase):
    def setUp(self):
        pass

    def test_simple(self):
        m = noword.Model("test_indir/1_nocode.txl")
        htmlstr = m.doc_tostring()
        htmlstr = re.sub("\s+", "", htmlstr) 

        self.assertEqual(htmlstr, "<h1>hello</h1><p>test1</p>")

    def test_get_single_code_block(self):
        m = noword.Model("test_indir/2_withcode.txl")
        pres = m.get_all_codes()
        
        self.assertEqual(1, len(pres))

        cleaned_codes = m.remove_code_tags_in_pre(pres[0])
        output = """{- python -}
print 1

print "BLAH"

print 2

"""
        self.assertEqual(output, cleaned_codes)

    def test_get_multi_code_blocks(self):
        m = noword.Model("test_indir/3_multicode.txl")
        pres = m.get_all_codes()
        self.assertEqual(2, len(pres))
        cleaned_codes = m.remove_code_tags_in_pre(pres[0])

        output = """{- python -}
print 1
def p:
    print "abc"

print 2

"""
        self.assertEqual(output, cleaned_codes)

        cleaned_codes = m.remove_code_tags_in_pre(pres[1])
        output = """{- xml -}
<xml>

<bbb>
</bbb>

</xml>

"""
        self.assertEqual(output, cleaned_codes)

    def tearDown(self):
        try:
            shutil.rmtree("test_outdir")
        except:
            pass


if __name__ == '__main__':
    unittest.main()
