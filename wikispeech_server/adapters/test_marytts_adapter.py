from wikispeech_server.adapters.marytts_adapter import *

#test1: no 'prosody', no 'mtu'
#hel häl här

m_test1 = """<?xml version="1.0" encoding="UTF-8"?>
<maryxml version="0.5" xml:lang="sv" xmlns="http://mary.dfki.de/2002/MaryXML" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<p>
<s>
<phrase>
<t accent="L+H*" g2p_method="lexicon" ph="' h e: l" pos="content">
hel
</t>
<t accent="L+H*" g2p_method="lexicon" ph="' h E: l" pos="content">
häl
</t>
<t accent="!H*" g2p_method="lexicon" ph="' h {: r" pos="content">
här
</t>
<boundary breakindex="5" tone="L-L%" />
</phrase>
</s>
</p>
</maryxml>
"""

w_test1 = {
    "lang": "sv",
    "paragraphs": [
        {"sentences": [
            {"phrases": [
                {"tokens": [
                    {
                        "token_orth": "hel",
                        "words": [
                            {
                                "orth": "hel",
                                "accent": "L+H*",
                                "g2p_method": "lexicon",
                                "pos": "content",
                                "trans": "\" h e: l"
                            }
                        ]
                    },
                    {
                        "token_orth": "häl",
                        "words": [
                            {
                                "orth": "häl",
                                "accent": "L+H*",
                                "g2p_method": "lexicon",
                                "pos": "content",
                                "trans": "\" h E: l"
                            }
                        ]
                    },
                    {
                        "token_orth": "här",
                        "words": [
                            {
                                "orth": "här",
                                "accent": "!H*",
                                "g2p_method": "lexicon",
                                "pos": "content",
                                "trans": "\" h {: r"
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
                                


#test2: 'prosody', no 'mtu'
#hel, häl här
m_test2 = """<?xml version="1.0" encoding="UTF-8"?>
<maryxml version="0.5" xml:lang="sv" xmlns="http://mary.dfki.de/2002/MaryXML" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<p>
<s>
<prosody pitch="+5%" range="+20%">
<phrase>
<t accent="L+H*" g2p_method="lexicon" ph="' h e: l" pos="content">
hel
</t>
<t pos="$PUNCT">
,
</t>
<boundary breakindex="4" tone="H-L%" />
</phrase>
</prosody>
<prosody pitch="-5%" range="-20%">
<phrase>
<t accent="L+H*" g2p_method="lexicon" ph="' h E: l" pos="content">
häl
</t>
<t accent="!H*" g2p_method="lexicon" ph="' h {: r" pos="content">
här
</t>
<boundary breakindex="5" tone="L-L%" />
</phrase>
</prosody>
</s>
</p>
</maryxml>"""


w_test2 = {
    "lang": "sv",
    "paragraphs": [
        {"sentences": [
            {"phrases": [
                {
                    "prosody_pitch": "+5%",
                    "prosody_range": "+20%",
                    "tokens": [
                        {
                            "token_orth": "hel",
                            "words": [
                                {
                                    "orth": "hel",
                                    "accent": "L+H*",
                                    "g2p_method": "lexicon",
                                    "pos": "content",
                                    "trans": "\" h e: l"
                                }
                            ]
                        },
                        {
                            "token_orth": ",",
                            "words": [
                                {
                                    "orth": ",",
                                    "pos": "$PUNCT"
                                }
                            ]
                        }
                    ],
                    "boundary": {"breakindex": "4", "tone": "H-L%"}
                },
                {
                    "prosody_pitch": "-5%",
                    "prosody_range": "-20%",
                    "tokens": [                        
                        {
                            "token_orth": "häl",
                            "words": [
                                {
                                    "orth": "häl",
                                    "accent": "L+H*",
                                    "g2p_method": "lexicon",
                                    "pos": "content",
                                    "trans": "\" h E: l"
                                }
                            ]
                        },
                        {
                            "token_orth": "här",
                            "words": [
                                {
                                    "orth": "här",
                                    "accent": "!H*",
                                    "g2p_method": "lexicon",
                                    "pos": "content",
                                    "trans": "\" h {: r"
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




#test3: no 'prosody', but 'mtu'
#öga öra 12

m_test3 = """<?xml version="1.0" encoding="UTF-8"?>
<maryxml version="0.5" xml:lang="sv" xmlns="http://mary.dfki.de/2002/MaryXML" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<p>
<s>
<phrase>
<t accent="L+H*" g2p_method="lexicon" ph="&quot; 2: - g a" pos="content">
öga
</t>
<t accent="L+H*" g2p_method="lexicon" ph="&quot; 9: - r a" pos="content">
öra
</t>
<mtu orig="12">
<t accent="!H*" g2p_method="lexicon" ph="' t O l v" pos="content">
tolv
</t>
</mtu>
<boundary breakindex="5" tone="L-L%"/>
</phrase>
</s>
</p>
</maryxml>"""

w_test3 = {
    "lang": "sv",
    "paragraphs": [
        {"sentences": [
            {"phrases": [
                {"tokens": [
                    {
                        "token_orth": "öga",
                        "words": [
                            {
                                "orth": "öga",
                                "accent": "L+H*",
                                "g2p_method": "lexicon",
                                "pos": "content",
                                "trans": "\"\" 2: . g a"
                            }
                        ]
                    },
                    {
                        "token_orth": "öra",
                        "words": [
                            {
                                "orth": "öra",
                                "accent": "L+H*",
                                "g2p_method": "lexicon",
                                "pos": "content",
                                "trans": "\"\" 9: . r a"
                            }
                        ]
                    },
                    {
                        "token_orth": "12",
                        "mtu": True,
                        "words": [
                            {
                                "orth": "tolv",
                                "accent": "!H*",
                                "g2p_method": "lexicon",
                                "pos": "content",
                                "trans": "\" t O l v"
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
                                

#test4: 'prosody' and 'mtu'
#öga, öra 12

m_test4 = """<?xml version="1.0" encoding="UTF-8"?>
<maryxml version="0.5" xml:lang="sv" xmlns="http://mary.dfki.de/2002/MaryXML" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<p>
<s>
<prosody pitch="+5%" range="+20%">
<phrase>
<t accent="L+H*" g2p_method="lexicon" ph="&quot; 2: - g a" pos="content">
öga
</t>
<t pos="$PUNCT">
,
</t>
<boundary breakindex="4" tone="H-L%"/>
</phrase>
</prosody>
<prosody pitch="-5%" range="-20%">
<phrase>
<t accent="L+H*" g2p_method="lexicon" ph="&quot; 9: - r a" pos="content">
öra
</t>
<mtu orig="12">
<t accent="!H*" g2p_method="lexicon" ph="' t O l v" pos="content">
tolv
</t>
</mtu>
<boundary breakindex="5" tone="L-L%"/>
</phrase>
</prosody>
</s>
</p>
</maryxml>
"""

w_test4 = {
    "lang": "sv",
    "paragraphs": [
        {"sentences": [
            {"phrases": [
                {
                    "prosody_pitch": "+5%",
                    "prosody_range": "+20%",
                    "tokens": [
                        {
                            "token_orth": "öga",
                            "words": [
                                {
                                    "orth": "öga",
                                    "accent": "L+H*",
                                    "g2p_method": "lexicon",
                                    "pos": "content",
                                    "trans": "\"\" 2: . g a"
                                }
                            ]
                        },
                        {
                            "token_orth": ",",
                            "words": [
                                {
                                    "orth": ",",
                                    "pos": "$PUNCT"
                                }
                            ]
                        }
                    ],
                    "boundary": {"breakindex": "4", "tone": "H-L%"}
                },
                {
                    "prosody_pitch": "-5%",
                    "prosody_range": "-20%",
                    "tokens": [                        
                        {
                            "token_orth": "öra",
                            "words": [
                                {
                                    "orth": "öra",
                                    "accent": "L+H*",
                                    "g2p_method": "lexicon",
                                    "pos": "content",
                                    "trans": "\"\" 9: . r a"
                                }
                            ]
                        },
                        {
                            "token_orth": "12",
                            "mtu": True,
                            "words": [
                                {
                                    "orth": "tolv",
                                    "accent": "!H*",
                                    "g2p_method": "lexicon",
                                    "pos": "content",
                                    "trans": "\" t O l v"
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

#test5: English. no 'prosody' but long 'mtu'

m_test5 = """<?xml version="1.0" encoding="UTF-8"?>
<maryxml version="0.5" xml:lang="en" xmlns="http://mary.dfki.de/2002/MaryXML" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<p>
<s>
<phrase>
<t accent="!H*" g2p_method="lexicon" ph="h @ - ' l @U" pos="UH">
Hello
</t>
<t pos=".">
,
</t>
<mtu orig="112">
<t g2p_method="lexicon" ph="' w V n" pos=",">
one
</t>
<t g2p_method="lexicon" ph="' h V n - d r @ d" pos="CD">
hundred
</t>
<t g2p_method="lexicon" ph="' t w E l v" pos="CD">
twelve
</t>
</mtu>
<t pos=".">
.
</t>
<boundary breakindex="5" tone="L-L%"/>
</phrase>
</s>
</p>
</maryxml>
"""



w_test5 = {
    "lang": "en",
    "paragraphs": [
        {
            "sentences": [
            {
                "phrases": [
                    {
                        "tokens": [
                            {
                                "token_orth": "Hello",
                                "words": [
                                    {
                                        "orth": "Hello",
                                        "accent": "!H*",
                                        "g2p_method": "lexicon",
                                        "pos": "UH",
                                        "trans": "h @ - ' l @U",
                                    }
                                ]
                            },
                            {
                                "token_orth": ",",
                                "words": [
                                    {
                                        "orth": ",",
                                        "pos": "."
                                    }
                                ]
                            },
                            {
                                "token_orth": "112",
                                "mtu": True,
                                "words": [
                                    {
                                        "orth": "one",
                                        "g2p_method": "lexicon",
                                        "pos": ",",
                                        "trans": "' w V n",
                                    },
                                    {
                                        "orth": "hundred",
                                        "g2p_method": "lexicon",
                                        "pos": "CD",
                                        "trans": "' h V n - d r @ d",
                                    },
                                    {
                                        "orth": "twelve",
                                        "g2p_method": "lexicon",
                                        "pos": "CD",
                                        "trans": "' t w E l v",
                                    }
                                ]
                            },
                            {
                                "token_orth": ".",
                                "words": [
                                    {
                                        "orth": ".",
                                        "pos": "."
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

w_test5_OLD_BROKEN = {
    "lang": "en",
    "paragraphs": [
        {
            "sentences": [
            {
                "phrases": [
                    {
                        "tokens": [
                            {
                                "token_orth": "Hello",
                                "words": [
                                    {
                                        "orth": "Hello",
                                        "accent": "!H*",
                                        "g2p_method": "lexicon",
                                        "pos": "UH",
                                        "trans": "HH AX $ L OW1",
                                    }
                                ]
                            },
                            {
                                "token_orth": ",",
                                "words": [
                                    {
                                        "orth": ",",
                                        "pos": "."
                                    }
                                ]
                            },
                            {
                                "token_orth": "112",
                                "mtu": True,
                                "words": [
                                    {
                                        "orth": "one",
                                        "g2p_method": "lexicon",
                                        "pos": ",",
                                        "trans": "W AH1 N",
                                    },
                                    {
                                        "orth": "hundred",
                                        "g2p_method": "lexicon",
                                        "pos": "CD",
                                        "trans": "HH AH1 N $ D R AX D",
                                    },
                                    {
                                        "orth": "twelve",
                                        "g2p_method": "lexicon",
                                        "pos": "CD",
                                        "trans": "T W EH1 L V",
                                    }
                                ]
                            },
                            {
                                "token_orth": ".",
                                "words": [
                                    {
                                        "orth": ".",
                                        "pos": "."
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


m_test6 = """
<?xml version="1.0" encoding="UTF-8"?>
<maryxml version="0.5" xml:lang="sv" xmlns="http://mary.dfki.de/2002/MaryXML" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<p>
<s>
<phrase>
<t accent="!H*" g2p_method="lexicon" ph="j 9 - t @ - ' b O r g" pos="content">
göteborg
</t>
<boundary breakindex="5" tone="L-L%"/>
</phrase>
</s>
</p>
</maryxml>
"""


w_test6 = {
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
                                "trans": "j 9 . t @ . \" b O r g"
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
 


import unittest

class TestM2Ws(unittest.TestCase):

    def test1(self):
        tp_config = ws.get_tp_config_by_name("wikitextproc_sv")
        #log.debug("tp_config: %s" % tp_config)
        component_config = tp_config["components"][0]
        u = mary2ws(m_test1, component_config)
        #log.debug(u)
        #log.debug(w_test1)
        self.assertEqual(u, w_test1)

    def test2(self):
        tp_config = ws.get_tp_config_by_name("wikitextproc_sv")
        #log.debug("tp_config: %s" % tp_config)
        component_config = tp_config["components"][0]
        u = mary2ws(m_test2, component_config)
        #log.debug(u)
        #log.debug(w_test2)
        self.assertEqual(u, w_test2)

    def test3(self):
        tp_config = ws.get_tp_config_by_name("wikitextproc_sv")
        #log.debug("tp_config: %s" % tp_config)
        component_config = tp_config["components"][0]

        u = mary2ws(m_test3, component_config)
        #log.debug(u)
        #log.debug(w_test3)
        self.assertEqual(u, w_test3)
        
    def test4(self):
        tp_config = ws.get_tp_config_by_name("wikitextproc_sv")
        #log.debug("tp_config: %s" % tp_config)
        component_config = tp_config["components"][0]

        u = mary2ws(m_test4, component_config)
        #log.debug("")
        #log.debug(u)
        #log.debug(w_test4)
        self.assertEqual(u, w_test4)

    def test5(self):
        tp_config = ws.get_tp_config_by_name("wikitextproc_en")
        #log.debug("tp_config: %s" % tp_config)
        component_config = tp_config["components"][0]

        u = mary2ws(m_test5, component_config)
        #log.debug("")
        #log.debug(u)
        #log.debug(w_test5)
        self.assertEqual(u, w_test5)

    def test6(self):
        tp_config = ws.get_tp_config_by_name("wikitextproc_sv")
        #log.debug("tp_config: %s" % tp_config)
        component_config = tp_config["components"][0]

        u = mary2ws(m_test6, component_config)
        #log.debug("")
        #log.debug(u)
        #log.debug(w_test6)
        self.assertEqual(u, w_test6)

class TestWs2M(unittest.TestCase):

    def test1(self):
        tp_config = ws.get_tp_config_by_name("wikitextproc_sv")
        #log.debug("tp_config: %s" % tp_config)
        component_config = tp_config["components"][0]

        m1 = ws2mary(w_test1, component_config)
        #m1 = re.sub('" />', '"/>', m1)

        m2 = re.sub("\n","",m_test1)

        #log.debug()
        #log.debug(m1)
        #log.debug(m2)
        self.assertEqual(m1, m2)
        
    def test2(self):
        tp_config = ws.get_tp_config_by_name("wikitextproc_sv")
        #log.debug("tp_config: %s" % tp_config)
        component_config = tp_config["components"][0]

        m1 = ws2mary(w_test2, component_config)
        #m1 = re.sub('" />', '"/>', m1)

        m2 = re.sub("\n","",m_test2)

        #log.debug("")
        #log.debug(m1)
        #log.debug(m2)
        self.assertEqual(m1, m2)
        
    def test3(self):
        tp_config = ws.get_tp_config_by_name("wikitextproc_sv")
        #log.debug("tp_config: %s" % tp_config)
        component_config = tp_config["components"][0]
        
        m1 = ws2mary(w_test3, component_config)
        m1 = re.sub('" />', '"/>', m1)

        m2 = re.sub("\n","",m_test3)

        #log.debug("")
        #log.debug(m1)
        #log.debug(m2)
        self.assertEqual(m1, m2)
        
    def test4(self):
        tp_config = ws.get_tp_config_by_name("wikitextproc_sv")
        #log.debug("tp_config: %s" % tp_config)
        component_config = tp_config["components"][0]

        m1 = ws2mary(w_test4, component_config)
        m1 = re.sub('" />', '"/>', m1)

        m2 = re.sub("\n","",m_test4)

        #log.debug("")
        #log.debug(m1)
        #log.debug(m2)
        self.assertEqual(m1, m2)
        
    def test5(self):
        tp_config = ws.get_tp_config_by_name("wikitextproc_en")
        #log.debug("tp_config: %s" % tp_config)
        component_config = tp_config["components"][0]
    
        m1 = ws2mary(w_test5, component_config)
        m1 = re.sub('" />', '"/>', m1)

        m2 = re.sub("\n","",m_test5)

        #log.debug("")
        #log.debug(m1)
        #log.debug(m2)
        self.assertEqual(m1, m2)
        
    def test6(self):
        tp_config = ws.get_tp_config_by_name("wikitextproc_sv")
        #log.debug("tp_config: %s" % tp_config)
        component_config = tp_config["components"][0]

        m1 = ws2mary(w_test6, component_config)
        m1 = re.sub('" />', '"/>', m1)

        m2 = re.sub("\n","",m_test6)

        #log.debug("")
        #log.debug(m1)
        #log.debug(m2)
        self.assertEqual(m1, m2)
        




import unittest

class TestMapSsml(unittest.TestCase):

    def test1(self):
        ws_ssml = """
<p>
    <s>
    Fartyget byggdes <br>
    <sub alias="nittonhundra-femtionio">1959</sub> 
    i 
    <phoneme alphabet="x-sampa" ph="\" p O . rt u0 . g a l">Portugal</phoneme> 
    på 
    <phoneme alphabet="x-sampa" ph="E s . t a . \" l E j . r O s">Estaleiros</phoneme> 
    <phoneme alphabet="x-sampa" ph="n a . \" v a j s">Navais</phoneme> 
    <phoneme alphabet="x-sampa" ph="\" d E">de</phoneme> 
    <phoneme alphabet="x-sampa" ph="v I . \" a . n a">Viana</phoneme> 
    <phoneme alphabet="x-sampa" ph="\" d O">do</phoneme> 
    <phoneme alphabet="x-sampa" ph="k a s . \" t E . l O">Castelo</phoneme>
    , och levererades till Färöarna under namnet 
    <phoneme alphabet="x-sampa" ph="\" v A: k . b I N . k u0 r">Vágbingur</phoneme>
    .
    </s>
</p>
"""
        mary_ssml = """
<p>
    <s>
    Fartyget byggdes <br>
    <sub alias="nittonhundra-femtionio">1959</sub> 
    i 
    <phoneme alphabet="x-sampa" ph="' p O - rt u0 - g a l">Portugal</phoneme> 
    på 
    <phoneme alphabet="x-sampa" ph="E s - t a - ' l E j - r O s">Estaleiros</phoneme> 
    <phoneme alphabet="x-sampa" ph="n a - ' v a j s">Navais</phoneme> 
    <phoneme alphabet="x-sampa" ph="' d E">de</phoneme> 
    <phoneme alphabet="x-sampa" ph="v I - ' a - n a">Viana</phoneme> 
    <phoneme alphabet="x-sampa" ph="' d O">do</phoneme> 
    <phoneme alphabet="x-sampa" ph="k a s - ' t E - l O">Castelo</phoneme>
    , och levererades till Färöarna under namnet 
    <phoneme alphabet="x-sampa" ph="' v A: k - b I N - k u0 r">Vágbingur</phoneme>
    .
    </s>
</p>
"""

        tp_config = ws.get_tp_config_by_name("wikitextproc_sv")
        log.debug("tp_config: %s" % tp_config)
        component_config = tp_config["components"][0]
        mapped = mapSsmlTranscriptionsToMary(ws_ssml, "sv", component_config)
        self.assertEqual(mapped, mary_ssml)


class TestPreproc(unittest.TestCase):

    def test1(self):
        input_text = "Ett öra."
        #expected = {'paragraphs': [{'sentences': [{'phrases': [{'boundary': {'tone': 'L-L%', 'breakindex': '5'}, 'tokens': [{'words': [{'pos': 'content', 'trans': '" E t', 'orth': 'Ett', 'accent': 'L+H*', 'g2p_method': 'lexicon'}], 'token_orth': 'Ett'}, {'words': [{'pos': 'content', 'trans': '"" 2: . r a', 'orth': 'öra', 'accent': '!H*', 'g2p_method': 'lexicon'}], 'token_orth': 'öra'}, {'words': [{'pos': '$PUNCT', 'orth': '.'}], 'token_orth': '.'}]}]}]}], 'lang': 'sv'}
        expected = {'lang': 'sv', 'paragraphs': [{'sentences': [{'phrases': [{'tokens': [{'token_orth': 'Ett', 'words': [{'g2p_method': 'lexicon', 'trans': '" E t', 'orth': 'Ett', 'accent': 'L+H*', 'pos': 'content'}]}, {'token_orth': 'öra', 'words': [{'g2p_method': 'lexicon', 'trans': '"" 9: . r a', 'orth': 'öra', 'accent': '!H*', 'pos': 'content'}]}, {'token_orth': '.', 'words': [{'orth': '.', 'pos': '$PUNCT'}]}], 'boundary': {'tone': 'L-L%', 'breakindex': '5'}}]}]}]}

        tp_config = ws.get_tp_config_by_name("wikitextproc_sv")
        log.debug("tp_config: %s" % tp_config)
        component_config = tp_config["components"][0]
        result = marytts_preproc(input_text, "sv", component_config)
        #print(result)
        self.assertEqual(expected, result)

        

if __name__ == "__main__":
    ws.log.log_level = "error" #debug, info, warning, error
    unittest.main()
