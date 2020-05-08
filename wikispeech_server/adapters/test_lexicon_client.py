if __name__ == "__main__":
    import sys
    sys.path.append(sys.path[0]+"/../..")
    #print(sys.path)
    
import unittest
try:
    from wikispeech_server.adapters.lexicon_client import *
except:
    from lexicon_client import *

import wikispeech_server.log as log


    
class TestLexicon(unittest.TestCase):

    def testNewLexicon(self):
        lexicon_name = "wikispeech_lexserver_demo:sv"
        lexicon = Lexicon(lexicon_name)
        self.assertEqual(str(type(lexicon)), "<class 'wikispeech_server.adapters.lexicon_client.Lexicon'>")

    def testLookup(self):
        lexicon_name = "wikispeech_lexserver_demo:sv"
        lexicon = Lexicon(lexicon_name)

        orth = "apa"

        #expected = [{'entryValidations': [], 'preferred': False, 'lexiconId': 2, 'partOfSpeech': 'NN', 'wordParts': 'apa', 'id': 74078, 'transcriptions': [{'language': 'sv-se', 'id': 79414, 'strn': '"" A: . p a', 'sources': [], 'entryId': 74078}], 'lemma': {'paradigm': 's1a-flicka', 'id': 8764, 'strn': 'apa', 'reading': ''}, 'status': {'id': 74078, 'source': 'nst', 'timestamp': '2017-04-06T09:40:10Z', 'current': True, 'name': 'imported'}, 'language': 'sv-se', 'strn': 'apa', 'morphology': 'SIN|IND|NOM|UTR'}, {'entryValidations': [], 'preferred': False, 'lexiconId': 2, 'partOfSpeech': 'VB', 'wordParts': 'apa', 'id': 74079, 'transcriptions': [{'language': 'sv-se', 'id': 79415, 'strn': '"" A: . p a', 'sources': [], 'entryId': 74079}], 'lemma': {'paradigm': 's1a-flicka', 'id': 8764, 'strn': 'apa', 'reading': ''}, 'status': {'id': 74079, 'source': 'nst', 'timestamp': '2017-04-06T09:40:10Z', 'current': True, 'name': 'imported'}, 'language': 'sv-se', 'strn': 'apa', 'morphology': ''}, {'entryValidations': [], 'preferred': False, 'lexiconId': 2, 'partOfSpeech': 'VB', 'wordParts': 'apa', 'id': 74080, 'transcriptions': [{'language': 'sv-se', 'id': 79416, 'strn': '"" A: . p a', 'sources': [], 'entryId': 74080}], 'lemma': {'paradigm': 's1a-flicka', 'id': 8764, 'strn': 'apa', 'reading': ''}, 'status': {'id': 74080, 'source': 'nst', 'timestamp': '2017-04-06T09:40:10Z', 'current': True, 'name': 'imported'}, 'language': 'sv-se', 'strn': 'apa', 'morphology': 'AKT|INF-IMP'}]

        #expected = [{'entryValidations': [], 'partOfSpeech': 'NN', 'language': 'sv-se', 'transcriptions': [{'id': 79410, 'entryId': 74074, 'sources': [], 'language': 'sv-se', 'strn': '"" A: . p a'}], 'id': 74074, 'preferred': False, 'morphology': 'SIN|IND|NOM|UTR', 'lemma': {'id': 8764, 'paradigm': 's1a-flicka', 'reading': '', 'strn': 'apa'}, 'wordParts': 'apa', 'strn': 'apa', 'lexiconId': 1, 'status': {'name': 'imported', 'id': 74074, 'current': True, 'source': 'nst', 'timestamp': '2017-05-12T10:55:49Z'}}, {'entryValidations': [], 'partOfSpeech': 'VB', 'language': 'sv-se', 'transcriptions': [{'id': 79411, 'entryId': 74075, 'sources': [], 'language': 'sv-se', 'strn': '"" A: . p a'}], 'id': 74075, 'preferred': False, 'morphology': '', 'lemma': {'id': 8764, 'paradigm': 's1a-flicka', 'reading': '', 'strn': 'apa'}, 'wordParts': 'apa', 'strn': 'apa', 'lexiconId': 1, 'status': {'name': 'imported', 'id': 74075, 'current': True, 'source': 'nst', 'timestamp': '2017-05-12T10:55:49Z'}}, {'entryValidations': [], 'partOfSpeech': 'VB', 'language': 'sv-se', 'transcriptions': [{'id': 79412, 'entryId': 74076, 'sources': [], 'language': 'sv-se', 'strn': '"" A: . p a'}], 'id': 74076, 'preferred': False, 'morphology': 'AKT|INF-IMP', 'lemma': {'id': 8764, 'paradigm': 's1a-flicka', 'reading': '', 'strn': 'apa'}, 'wordParts': 'apa', 'strn': 'apa', 'lexiconId': 1, 'status': {'name': 'imported', 'id': 74076, 'current': True, 'source': 'nst', 'timestamp': '2017-05-12T10:55:49Z'}}]

        #expected = [{'lexRef': {'DBRef': 'wikispeech_lexserver_demo', 'LexName': 'sv'}, 'lemma': {'strn': 'apa', 'paradigm': 's1a-flicka', 'reading': '', 'id': 8764}, 'strn': 'apa', 'transcriptions': [{'entryId': 74074, 'strn': '"" A: . p a', 'id': 79410, 'language': 'sv-se', 'sources': []}], 'preferred': False, 'partOfSpeech': 'NN', 'wordParts': 'apa', 'id': 74074, 'morphology': 'SIN|IND|NOM|UTR', 'status': {'source': 'nst', 'id': 74074, 'timestamp': '2017-08-17T11:57:08Z', 'name': 'imported', 'current': True}, 'language': 'sv-se', 'entryValidations': []}, {'lexRef': {'DBRef': 'wikispeech_lexserver_demo', 'LexName': 'sv'}, 'lemma': {'strn': 'apa', 'paradigm': 's1a-flicka', 'reading': '', 'id': 8764}, 'strn': 'apa', 'transcriptions': [{'entryId': 74075, 'strn': '"" A: . p a', 'id': 79411, 'language': 'sv-se', 'sources': []}], 'preferred': False, 'partOfSpeech': 'VB', 'wordParts': 'apa', 'id': 74075, 'morphology': '', 'status': {'source': 'nst', 'id': 74075, 'timestamp': '2017-08-17T11:57:08Z', 'name': 'imported', 'current': True}, 'language': 'sv-se', 'entryValidations': []}, {'lexRef': {'DBRef': 'wikispeech_lexserver_demo', 'LexName': 'sv'}, 'lemma': {'strn': 'apa', 'paradigm': 's1a-flicka', 'reading': '', 'id': 8764}, 'strn': 'apa', 'transcriptions': [{'entryId': 74076, 'strn': '"" A: . p a', 'id': 79412, 'language': 'sv-se', 'sources': []}], 'preferred': False, 'partOfSpeech': 'VB', 'wordParts': 'apa', 'id': 74076, 'morphology': 'AKT|INF-IMP', 'status': {'source': 'nst', 'id': 74076, 'timestamp': '2017-08-17T11:57:08Z', 'name': 'imported', 'current': True}, 'language': 'sv-se', 'entryValidations': []}]

        expected = [{'wordParts': 'apa', 'entryValidations': [], 'id': 74074, 'lexRef': {'LexName': 'sv', 'DBRef': 'wikispeech_lexserver_demo'}, 'status': {'timestamp': '2017-08-25T08:43:56Z', 'current': True, 'name': 'imported', 'source': 'nst', 'id': 74074}, 'morphology': 'SIN|IND|NOM|UTR', 'strn': 'apa', 'language': 'sv-se', 'partOfSpeech': 'NN', 'lemma': {'strn': 'apa', 'paradigm': 's1a-flicka', 'id': 8764, 'reading': ''}, 'transcriptions': [{'strn': '"" A: . p a', 'entryId': 74074, 'sources': [], 'language': 'sv-se', 'id': 79410}], 'preferred': False}, {'wordParts': 'apa', 'entryValidations': [], 'id': 74075, 'lexRef': {'LexName': 'sv', 'DBRef': 'wikispeech_lexserver_demo'}, 'status': {'timestamp': '2017-08-25T08:43:56Z', 'current': True, 'name': 'imported', 'source': 'nst', 'id': 74075}, 'morphology': '', 'strn': 'apa', 'language': 'sv-se', 'partOfSpeech': 'VB', 'lemma': {'strn': 'apa', 'paradigm': 's1a-flicka', 'id': 8764, 'reading': ''}, 'transcriptions': [{'strn': '"" A: . p a', 'entryId': 74075, 'sources': [], 'language': 'sv-se', 'id': 79411}], 'preferred': False}, {'wordParts': 'apa', 'entryValidations': [], 'id': 74076, 'lexRef': {'LexName': 'sv', 'DBRef': 'wikispeech_lexserver_demo'}, 'status': {'timestamp': '2017-08-25T08:43:56Z', 'current': True, 'name': 'imported', 'source': 'nst', 'id': 74076}, 'morphology': 'AKT|INF-IMP', 'strn': 'apa', 'language': 'sv-se', 'partOfSpeech': 'VB', 'lemma': {'strn': 'apa', 'paradigm': 's1a-flicka', 'id': 8764, 'reading': ''}, 'transcriptions': [{'strn': '"" A: . p a', 'entryId': 74076, 'sources': [], 'language': 'sv-se', 'id': 79412}], 'preferred': False}]


        
        result = lexicon.lookup(orth)
        log.debug("RESULT: %s" % result)

        expected_first_trans = expected[0]['transcriptions'][0]['strn']
        result_first_trans = result[0]['transcriptions'][0]['strn']
        
        self.assertEqual(expected_first_trans,result_first_trans)

    def testLexiconException1(self):
        default_log_level = log.log_level
        log.log_level = "fatal"
        lexicon_name = "wikispeech_lexserver_demo:sv_THIS_LEXICON_SHOULD_NOT_EXIST"
        with self.assertRaises(LexiconException):
            lexicon = Lexicon(lexicon_name)
        log.log_level = default_log_level
            
    def testLexiconException2(self):
        default_log_level = log.log_level
        log.log_level = "fatal"
        lexicon_name = "wikispeech_lexserver_demo:sv_THIS_LEXICON_SHOULD_NOT_EXIST"
        with self.assertRaises(LexiconException):
            lexicon = Lexicon("wikispeech_lexserver_demo:sv")
            lexicon.lexicon_name = lexicon_name
            lexicon.lookup("apa")
        log.log_level = default_log_level


    def test_lexLookup(self):
        lex_config = {
            "module":"adapters.lexicon_client",
            "call":"lexLookup",
            "lexicon":"wikispeech_lexserver_demo:sv"
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
            "module":"adapters.lexicon_client",
            "call":"lexLookup",
            "lexicon":"wikispeech_lexserver_demo:sv_DOES_NOT_EXIST"
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
    log.log_level = "debug" #debug, info, warning, error
    unittest.main()
