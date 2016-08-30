import sys
import re
import xml.etree.ElementTree as ET

#test1: no 'prosody', no 'mtu'

m_test1 = """<?xml version="1.0" encoding="UTF-8"?><maryxml xmlns="http://mary.dfki.de/2002/MaryXML" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="0.5" xml:lang="sv">
<p>
<s>
<phrase>
<t accent="L+H*" g2p_method="lexicon" ph="' h E j" pos="content">
hej
<syllable accent="L+H*" ph="h E j" stress="1">
<ph p="h"/>
<ph p="E"/>
<ph p="j"/>
</syllable>
</t>
<t accent="!H*" g2p_method="lexicon" ph="' h E j" pos="content">
hej
<syllable accent="!H*" ph="h E j" stress="1">
<ph p="h"/>
<ph p="E"/>
<ph p="j"/>
</syllable>
</t>
<boundary breakindex="5" tone="L-L%"/>
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
                        "token_orth": "hej",
                        "words": [
                        {
                            "orth": "hej",
                            "accent": "L+H*",
                            "g2p_method": "lexicon",
                            "pos": "content",
                            "ph": "' h E j",
                            "syllables": [
                            {
                                "accent": "L+H*",
                                "ph": "h E j",
                                "stress": "1",
                                "phonemes": [
                                    {"symbol": "h"},
                                    {"symbol": "E"},
                                    {"symbol": "j"}
                                ]
                            }
                            ]
                        }
                        ]
                    },
                    {
                        "token_orth": "hej",
                        "words": [
                        {
                            "orth": "hej",
                            "accent": "!H*",
                            "g2p_method": "lexicon",
                            "pos": "content",
                            "ph": "' h E j",
                            "syllables": [
                            {
                                "accent": "!H*",
                                "ph": "h E j",
                                "stress": "1",
                                "phonemes": [
                                    {"symbol": "h"},
                                    {"symbol": "E"},
                                    {"symbol": "j"}
                                ]
                            }
                            ]
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
m_test2 = """<?xml version="1.0" encoding="UTF-8"?><maryxml xmlns="http://mary.dfki.de/2002/MaryXML" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="0.5" xml:lang="sv">
<p>
<s>
<prosody pitch="+5%" range="+20%">
<phrase>
<t accent="L+H*" g2p_method="lexicon" ph="' h E j" pos="content">
hej
<syllable accent="L+H*" ph="h E j" stress="1">
<ph p="h"/>
<ph p="E"/>
<ph p="j"/>
</syllable>
</t>
<t pos="$PUNCT">
,
</t>
<boundary breakindex="4" tone="H-L%"/>
</phrase>
</prosody>
<prosody pitch="-5%" range="-20%">
<phrase>
<t accent="!H*" g2p_method="lexicon" ph="' h E j" pos="content">
hej
<syllable accent="!H*" ph="h E j" stress="1">
<ph p="h"/>
<ph p="E"/>
<ph p="j"/>
</syllable>
</t>
<boundary breakindex="5" tone="L-L%"/>
</phrase>
</prosody>
</s>
</p>
</maryxml>
"""


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
                            "token_orth": "hej",
                            "words": [
                                {
                                    "orth": "hej",
                                    "accent": "L+H*",
                                    "g2p_method": "lexicon",
                                    "pos": "content",
                                    "ph": "' h E j",
                                    "syllables": [
                                        {
                                            "accent": "L+H*",
                                            "ph": "h E j",
                                            "stress": "1",
                                            "phonemes": [
                                                {"symbol": "h"},
                                                {"symbol": "E"},
                                                {"symbol": "j"}
                                            ]
                                        }
                                    ]
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
                            "token_orth": "hej",
                            "words": [
                                {
                                    "orth": "hej",
                                    "accent": "!H*",
                                    "g2p_method": "lexicon",
                                    "pos": "content",
                                    "ph": "' h E j",
                                    "syllables": [
                                        {
                                            "accent": "!H*",
                                            "ph": "h E j",
                                            "stress": "1",
                                            "phonemes": [
                                                {"symbol": "h"},
                                                {"symbol": "E"},
                                                {"symbol": "j"}
                                            ]
                                        }
                                    ]
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
m_test3 = """<?xml version="1.0" encoding="UTF-8"?><maryxml xmlns="http://mary.dfki.de/2002/MaryXML" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="0.5" xml:lang="sv">
<p>
<s>
<phrase>
<t accent="L+H*" g2p_method="lexicon" ph="' h E j" pos="content">
hej
<syllable accent="L+H*" ph="h E j" stress="1">
<ph p="h"/>
<ph p="E"/>
<ph p="j"/>
</syllable>
</t>
<mtu orig="12">
<t accent="!H*" g2p_method="lexicon" ph="' t O l v" pos="content">
tolv
<syllable accent="!H*" ph="t O l v" stress="1">
<ph p="t"/>
<ph p="O"/>
<ph p="l"/>
<ph p="v"/>
</syllable>
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
                        "token_orth": "hej",
                        "words": [
                        {
                            "orth": "hej",
                            "accent": "L+H*",
                            "g2p_method": "lexicon",
                            "pos": "content",
                            "ph": "' h E j",
                            "syllables": [
                            {
                                "accent": "L+H*",
                                "ph": "h E j",
                                "stress": "1",
                                "phonemes": [
                                    {"symbol": "h"},
                                    {"symbol": "E"},
                                    {"symbol": "j"}
                                ]
                            }
                            ]
                        }
                        ]
                    },
                    {
                        "token_orth": "12",
                        "words": [
                        {
                            "orth": "tolv",
                            "accent": "!H*",
                            "g2p_method": "lexicon",
                            "pos": "content",
                            "ph": "' t O l v",
                            "syllables": [
                            {
                                "accent": "!H*",
                                "ph": "t O l v",
                                "stress": "1",
                                "phonemes": [
                                    {"symbol": "t"},
                                    {"symbol": "O"},
                                    {"symbol": "l"},
                                    {"symbol": "v"}
                                ]
                            }
                            ]
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
m_test4 = """<?xml version="1.0" encoding="UTF-8"?><maryxml xmlns="http://mary.dfki.de/2002/MaryXML" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="0.5" xml:lang="sv">
<p>
<s>
<prosody pitch="+5%" range="+20%">
<phrase>
<t accent="L+H*" g2p_method="lexicon" ph="' h E j" pos="content">
hej
<syllable accent="L+H*" ph="h E j" stress="1">
<ph p="h"/>
<ph p="E"/>
<ph p="j"/>
</syllable>
</t>
<t pos="$PUNCT">
,
</t>
<boundary breakindex="4" tone="H-L%"/>
</phrase>
</prosody>
<prosody pitch="-5%" range="-20%">
<phrase>
<mtu orig="12">
<t accent="!H*" g2p_method="lexicon" ph="' t O l v" pos="content">
tolv
<syllable accent="!H*" ph="t O l v" stress="1">
<ph p="t"/>
<ph p="O"/>
<ph p="l"/>
<ph p="v"/>
</syllable>
</t>
</mtu>
<t pos="$PUNCT">
.
</t>
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
                            "token_orth": "hej",
                            "words": [
                                {
                                    "orth": "hej",
                                    "accent": "L+H*",
                                    "g2p_method": "lexicon",
                                    "pos": "content",
                                    "ph": "' h E j",
                                    "syllables": [
                                        {
                                            "accent": "L+H*",
                                            "ph": "h E j",
                                            "stress": "1",
                                            "phonemes": [
                                                {"symbol": "h"},
                                                {"symbol": "E"},
                                                {"symbol": "j"}
                                            ]
                                        }
                                    ]
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
                            "token_orth": "12",
                            "words": [
                                {
                                    "orth": "tolv",
                                    "accent": "!H*",
                                    "g2p_method": "lexicon",
                                    "pos": "content",
                                    "ph": "' t O l v",
                                    "syllables": [
                                        {
                                            "accent": "!H*",
                                            "ph": "t O l v",
                                            "stress": "1",
                                            "phonemes": [
                                                {"symbol": "t"},
                                                {"symbol": "O"},
                                                {"symbol": "l"},
                                                {"symbol": "v"}
                                            ]
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "token_orth": ".",
                            "words": [
                                {
                                    "orth": ".",
                                    "pos": "$PUNCT"
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


#mary2ws: 'prosody' and 'phrase' are combined into 'phrase'. ws2mary: 'phrase' is split into 'prosody' and 'phrase'
#mary2ws: 'mtu' and 'token' are combined into 'token', and 'token' is also copied to 'word'
def mary2ws(maryxml):
    (lang, maryxml) = dropHeader(maryxml)
    #lang = "sv"

    #print(maryxml)

    root = ET.fromstring(maryxml.encode('utf-8'))
    #root = ET.fromstring(maryxml)

    paragraphs = []
    utterance = {
        "lang": lang,
        "paragraphs": paragraphs
    }

    paragraph_elements = root.findall(".//p")
    for paragraph_element in paragraph_elements:

        sentences = []
        paragraphs.append({"sentences": sentences})
        
        sentence_elements = paragraph_element.findall("s")
        for sentence_element in sentence_elements:

            phrases = []
            sentence = {"phrases": phrases}
            sentences.append(sentence)

            for sentence_child in sentence_element:

                if sentence_child.tag == "phrase":
                    phrase_element = sentence_child
                    phrase = buildPhrase(phrase_element)
                    phrases.append(phrase)
                elif sentence_child.tag == "prosody":
                    prosody_element = sentence_child
                    #can 'prosody' only contain exactly one 'phrase'? 
                    phrase_element = prosody_element[0]
                    phrase = buildPhrase(phrase_element)

                    phrase = addIfExists(phrase, prosody_element, "pitch", prefix="prosody_")
                    phrase = addIfExists(phrase, prosody_element, "range", prefix="prosody_")

                    phrases.append(phrase)
                else:
                    print("ERROR: sentence child should not have tag %s" % sentence_child.tag)
                    

    return utterance


def buildPhrase(phrase_element):
    if phrase_element.tag != "phrase":
        print("ERROR: wrong type of element: %s\n%s" % (phrase_element.tag, phrase_element))
        sys.exit(1)
    tokens = []
    phrase = {"tokens": tokens}
    for phrase_child in phrase_element:
        #print("phrase_child: %s" % phrase_child.tag)
                        
        #no 'mtu'
        if phrase_child.tag == "t":                
            token_element = phrase_child
            words = []
            token = {
                "words": words
            }
            tokens.append(token)
            
            orth = token_element.text
            token["token_orth"] = orth
            
            word = buildWord(token_element)
            words.append(word)
            
            #END no 'mtu'
            #'mtu'
        elif phrase_child.tag == "mtu":                
            mtu_element = phrase_child
            words = []
            token = {
                "words": words
            }
            tokens.append(token)
            
            token_orth = mtu_element.attrib["orig"]
            token["token_orth"] = token_orth
            
            token_elements = mtu_element.findall("t")
            for token_element in token_elements:
                word = buildWord(token_element)
                words.append(word)
                #END  'mtu'
        elif phrase_child.tag == "boundary":
            boundary = {}
            boundary = addIfExists(boundary, phrase_child, "breakindex")
            boundary = addIfExists(boundary, phrase_child, "tone")
            phrase["boundary"] = boundary
                            
        else:
            print("ERROR: phrase child should not have tag %s" % phrase_child.tag)
    return phrase




def buildWord(token_element):
    if token_element.tag != "t":
        print("ERROR: wrong type of element: %s\n%s" % (token_element.tag, token_element))
        sys.exit(1)

    orth = token_element.text
    word = {
        "orth": orth
    }
    word = addIfExists(word, token_element, "accent")
    word = addIfExists(word, token_element, "g2p_method")
    word = addIfExists(word, token_element, "pos")
    word = addIfExists(word, token_element, "ph")
    
    syllable_elements = token_element.findall("syllable")

    if len(syllable_elements) > 0:
        syllables = []
        word["syllables"] = syllables

    
    for syllable_element in syllable_elements:
        phonemes = []
        syllable = {
            "phonemes": phonemes
        }
        syllable = addIfExists(syllable, syllable_element, "accent")
        syllable = addIfExists(syllable, syllable_element, "ph")
        syllable = addIfExists(syllable, syllable_element, "stress")

        
        syllables.append(syllable)
        
        phoneme_elements = syllable_element.findall("ph")
        for phoneme_element in phoneme_elements:
            symbol = phoneme_element.attrib["p"]
            phonemes.append({"symbol": symbol})

    return word

def addIfExists(addTo, element, attribute, prefix=""):
    if attribute in element.attrib:
        addTo[prefix+attribute] = element.attrib.get(attribute)
    return addTo



def dropHeader(maryxml):
    lang = None
    maryxml = maryxml.replace("\n","")
    m = re.match("<\?xml .+ xml:lang=\"([^\"]*)\">\n*(.*)$", maryxml)
    if m:
        lang = m.group(1)
        maryxml = m.group(2)
        if not maryxml.startswith("<maryxml"):
            maryxml = "<maryxml>"+maryxml

    return (lang,maryxml)

def ws2mary(utterance):

    lang = utterance["lang"]

    header = '<?xml version="1.0" encoding="UTF-8"?>'

    #<maryxml xmlns="http://mary.dfki.de/2002/MaryXML" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="0.5" xml:lang="%s">' % lang

    maryxml = ET.Element("maryxml")

    maryxml.attrib["xmlns"] = "http://mary.dfki.de/2002/MaryXML"
    maryxml.attrib["xmlns:xsi"] = "http://www.w3.org/2001/XMLSchema-instance"
    maryxml.attrib["version"] = "0.5"
    maryxml.attrib["xml:lang"] = lang

    paragraphs = utterance["paragraphs"]
    for paragraph in paragraphs:
        paragraph_element = ET.Element("p")
        maryxml.append(paragraph_element)
        sentences = paragraph["sentences"]
        for sentence in sentences:
            sentence_element = ET.Element("s")
            paragraph_element.append(sentence_element)
            phrases = sentence["phrases"]
            for phrase in phrases:
                phrase_element = ET.Element("phrase")

                sentence_element.append(phrase_element)
                tokens = phrase["tokens"]
                for token in tokens:
                    token_element = ET.Element("t")
                    token_element.text = token["token_orth"]


                    phrase_element.append(token_element)
                    words = token["words"]
                    for word in words:
                        
                        token_element = addToElementIfExists(token_element, word, "accent")
                        token_element = addToElementIfExists(token_element, word, "g2p_method")
                        token_element = addToElementIfExists(token_element, word, "pos")
                        token_element = addToElementIfExists(token_element, word, "ph")
                        

                        syllables = word["syllables"]
                        for syllable in syllables:
                            syllable_element = ET.Element("syllable")

                            syllable_element = addToElementIfExists(syllable_element, syllable, "accent")
                            syllable_element = addToElementIfExists(syllable_element, syllable, "ph")
                            syllable_element = addToElementIfExists(syllable_element, syllable, "stress")

                            token_element.append(syllable_element)
                            phonemes = syllable["phonemes"]
                            for phoneme in phonemes:
                                phoneme_element = ET.Element("ph")
                                phoneme_element.attrib["p"] = phoneme["symbol"]
                                syllable_element.append(phoneme_element)


                if "boundary" in phrase:
                    boundary_element = ET.Element("boundary")
                    boundary_element = addToElementIfExists(boundary_element, phrase["boundary"], "breakindex")
                    boundary_element = addToElementIfExists(boundary_element, phrase["boundary"], "tone")
                    phrase_element.append(boundary_element)
                


    if sys.version_info.major == 2:
        #This works in python2.7
        maryxmlstring = ET.tostring(maryxml, encoding="utf-8")
    else:
        #This works in python3
        maryxmlstring = ET.tostring(maryxml, encoding="unicode")

    #print("utt2maryxml maryxml:\n%s%s" % (header,maryxmlstring))


    return "%s%s" % (header,maryxmlstring)


def addToElementIfExists(element, item, attribute, drop_prefix=""):
    if attribute in item:
        new_attribute = re.sub("^"+drop_prefix, "", attribute)
        element.attrib[new_attribute] = item[attribute]
    return element



import unittest

class TestM2Ws(unittest.TestCase):

    def test1(self):
        u = mary2ws(m_test1)
        #print(u)
        #print(w_test1)
        self.assertEqual(u, w_test1)

    def test2(self):
        u = mary2ws(m_test2)
        #print(u)
        #print(w_test2)
        self.assertEqual(u, w_test2)

    def test3(self):
        u = mary2ws(m_test3)
        #print(u)
        #print(w_test3)
        self.assertEqual(u, w_test3)
        
    def test4(self):
        u = mary2ws(m_test4)
        #print(u)
        #print(w_test4)
        self.assertEqual(u, w_test4)

class TestWs2M(unittest.TestCase):

    def test1(self):
        m = ws2mary(w_test1)

        m1 = re.sub("\n", "", m_test1)
        print()
        print(m1)
        m = re.sub("\" \/", "\"/", m)
        print(m)

        d1 = ET.fromstring(m1)
        d2 = ET.fromstring(m)
        self.assertEqual(d1, d2)





if __name__ == '__main__':
    unittest.main()
