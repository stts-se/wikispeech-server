import unittest
try:
    from wikispeech_server.adapters.lexicon_client import *
except:
    from lexicon_client import *

import wikispeech_server.log as log


    
class TestLexicon(unittest.TestCase):

    def testNewLexicon(self):
        lexicon_name = "sv-se.nst"
        lexicon = Lexicon(lexicon_name)
        self.assertEqual(str(type(lexicon)), "<class 'wikispeech_server.adapters.lexicon_client.Lexicon'>")

    def testLookup(self):
        lexicon_name = "sv-se.nst"
        lexicon = Lexicon(lexicon_name)

        orth = "apa"

        expected = [{'entryValidations': [], 'preferred': False, 'lexiconId': 2, 'partOfSpeech': 'NN', 'wordParts': 'apa', 'id': 74078, 'transcriptions': [{'language': 'sv-se', 'id': 79414, 'strn': '"" A: . p a', 'sources': [], 'entryId': 74078}], 'lemma': {'paradigm': 's1a-flicka', 'id': 8764, 'strn': 'apa', 'reading': ''}, 'status': {'id': 74078, 'source': 'nst', 'timestamp': '2017-04-06T09:40:10Z', 'current': True, 'name': 'imported'}, 'language': 'sv-se', 'strn': 'apa', 'morphology': 'SIN|IND|NOM|UTR'}, {'entryValidations': [], 'preferred': False, 'lexiconId': 2, 'partOfSpeech': 'VB', 'wordParts': 'apa', 'id': 74079, 'transcriptions': [{'language': 'sv-se', 'id': 79415, 'strn': '"" A: . p a', 'sources': [], 'entryId': 74079}], 'lemma': {'paradigm': 's1a-flicka', 'id': 8764, 'strn': 'apa', 'reading': ''}, 'status': {'id': 74079, 'source': 'nst', 'timestamp': '2017-04-06T09:40:10Z', 'current': True, 'name': 'imported'}, 'language': 'sv-se', 'strn': 'apa', 'morphology': ''}, {'entryValidations': [], 'preferred': False, 'lexiconId': 2, 'partOfSpeech': 'VB', 'wordParts': 'apa', 'id': 74080, 'transcriptions': [{'language': 'sv-se', 'id': 79416, 'strn': '"" A: . p a', 'sources': [], 'entryId': 74080}], 'lemma': {'paradigm': 's1a-flicka', 'id': 8764, 'strn': 'apa', 'reading': ''}, 'status': {'id': 74080, 'source': 'nst', 'timestamp': '2017-04-06T09:40:10Z', 'current': True, 'name': 'imported'}, 'language': 'sv-se', 'strn': 'apa', 'morphology': 'AKT|INF-IMP'}]
        
        result = lexicon.lookup(orth)
        self.assertEqual(expected,result)

    def testLexiconException1(self):
        default_log_level = log.log_level
        log.log_level = "fatal"
        lexicon_name = "sv-se.nst_THIS_LEXICON_SHOULD_NOT_EXIST"
        with self.assertRaises(LexiconException):
            lexicon = Lexicon(lexicon_name)
        log.log_level = default_log_level
            
    def testLexiconException2(self):
        default_log_level = log.log_level
        log.log_level = "fatal"
        lexicon_name = "sv-se.nst_THIS_LEXICON_SHOULD_NOT_EXIST"
        with self.assertRaises(LexiconException):
            lexicon = Lexicon("sv-se.nst")
            lexicon.lexicon_name = lexicon_name
            lexicon.lookup("apa")
        log.log_level = default_log_level


    def test_lexLookup(self):
        lex_config = {
            "module":"wikilex",
            "call":"lexLookup",
            "lexicon":"sv-se.nst"
        }
        utt = {
            "lang": "sv",
            "paragraphs": [
                {"sentences": [
                    {"phrases": [
                        {"tokens": [
                            {
                                "token_orth": "göteborg",
                                "words": [
                                    {
                                        "orth": "göteborg",
                                        "accent": "!H*",
                                        "g2p_method": "lexicon",
                                        "pos": "content",
                                        "trans": "j 2 . t e . \" b O r j"
                                    }
                                ]
                            }
                        ],
                         "boundary": {"breakindex": "5", "tone": "L-L%"}
                        }
                    ]
                    }
                ]
                }
            ]
        }
        newutt = lexLookup(utt, utt["lang"], lex_config)
        self.assertEqual( utt, newutt )

    def test_lexLookup_Exception(self):
        default_log_level = log.log_level
        log.log_level = "fatal"
        lex_config = {
            "module":"wikilex",
            "call":"lexLookup",
            "lexicon":"sv-se.nst_DOES_NOT_EXIST"
        }
        utt = {
            "lang": "sv",
            "paragraphs": [
                {"sentences": [
                    {"phrases": [
                        {"tokens": [
                            {
                                "token_orth": "göteborg",
                                "words": [
                                    {
                                        "orth": "göteborg",
                                        "accent": "!H*",
                                        "g2p_method": "lexicon",
                                        "pos": "content",
                                        "trans": "j 2 . t e . \" b O r j"
                                    }
                                ]
                            }
                        ],
                         "boundary": {"breakindex": "5", "tone": "L-L%"}
                        }
                    ]
                    }
                ]
                }
            ]
        }
        with self.assertRaises(LexiconException):
            newutt = lexLookup(utt, utt["lang"], lex_config)
            self.assertEqual( utt, newutt )
        log.log_level = default_log_level
            
        
if __name__ == "__main__":
    log.log_level = "error" #debug, info, warning, error
    unittest.main()
