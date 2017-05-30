if __name__ == "__main__":
    import sys
    sys.path.append(sys.path[0]+"/..")

import unittest
try:
    from wikispeech_server.textprocessor import *
except:
    from textprocessor import *

import wikispeech_server.log as log


    
class TestTextprocessor(unittest.TestCase):

    def testNewTextprocessor(self):
        tp_config = {
            "name":"wikitextproc_sv",
            "lang":"sv",
            "components":[
                {
                    "module":"adapters.marytts_adapter",
                    "call":"marytts_preproc",
                    "mapper": {
                        "from":"sv-se_ws-sampa",
                        "to":"sv-se_sampa_mary"
                    },
                },
                {
                    "module":"adapters.lexicon_client",
                    "call":"lexLookup",
                    "lexicon":"sv-se.nst"
                }
            ]
        }
        tp = Textprocessor(tp_config)
        self.assertEqual(tp.name, tp_config["name"])
        self.assertEqual(tp.components[0].call, tp_config["components"][0]["call"])
        self.assertEqual(str(type(tp.components[1])), "<class 'wikispeech_server.adapters.lexicon_client.Lexicon'>")

    def testBrokenTextprocessor(self):
        default_log_level = log.log_level
        log.log_level = "fatal"
        tp_config = {
            "name":"wikitextproc_sv",
            "lang":"sv",
            "components":[
                {
                    "module":"adapters.marytts_adapter",
                    "call":"marytts_preproc",
                    "mapper": {
                        "from":"sv-se_ws-sampaXX",
                        "to":"sv-se_sampa_mary"
                    },
                },
                {
                    "module":"adapters.lexicon_client",
                    "call":"lexLookup",
                    "lexicon":"sv-se.nst"
                }
            ]
        }
        with self.assertRaises(TextprocessorException):
            tp = Textprocessor(tp_config)
        log.log_level = default_log_level



def run_tests():
    unittest.main(exit=False, failfast=True)
    
        
    
if __name__ == "__main__":
    log.log_level = "error" #debug, info, warning, error
    run_tests()
