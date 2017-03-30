# *-* coding: utf-8 *-*

import sys, re, requests, json
import xml.etree.ElementTree as ET
try:
    #Python 3
    from urllib.parse import quote_plus
except:
    #Python 2
    from urllib import quote_plus


import wikispeech_mockup.config as config
host = config.config.get("Services", "lexicon")


    

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
                    phrase = buildPhrase(phrase_element, lang)
                    phrases.append(phrase)
                elif sentence_child.tag == "prosody":
                    prosody_element = sentence_child
                    #can 'prosody' only contain exactly one 'phrase'? 
                    phrase_element = prosody_element[0]
                    phrase = buildPhrase(phrase_element, lang)

                    phrase = addIfExists(phrase, prosody_element, "pitch", prefix="prosody_")
                    phrase = addIfExists(phrase, prosody_element, "range", prefix="prosody_")

                    phrases.append(phrase)
                elif sentence_child.tag == "t":
                    #This is a special case that happens (sometimes..) with single-word sentences
                    #doesn't work, produces error in synthesis
                    #TODO look at this again
                    #It only happens with the word "Hon." ...
                    phrase_element = ET.Element("phrase")
                    phrase_element.append(sentence_child)
                    phrase = buildPhrase(phrase_element, lang)

                    phrases.append(phrase)

                else:
                    print("ERROR: sentence child should not have tag %s" % sentence_child.tag)
                    

    return utterance


def buildPhrase(phrase_element, lang):
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
            
            word = buildWord(token_element, lang)
            words.append(word)
            
            #END no 'mtu'
            #'mtu'
        elif phrase_child.tag == "mtu":                
            mtu_element = phrase_child
            words = []
            token = {
                "mtu": True,
                "words": words
            }
            tokens.append(token)
            
            token_orth = mtu_element.attrib["orig"]
            token["token_orth"] = token_orth
            
            token_elements = mtu_element.findall("t")
            for token_element in token_elements:
                word = buildWord(token_element, lang)
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




def buildWord(token_element, lang):
    if token_element.tag != "t":
        print("ERROR: wrong type of element: %s\n%s" % (token_element.tag, token_element))
        sys.exit(1)

    orth = token_element.text
    word = {
        "orth": orth
    }
    word = addIfExists(word, token_element, "accent")
    #g2p_method can be rules, lexicon, or not there if there is sampa in input
    word = addIfExists(word, token_element, "g2p_method")
    word = addIfExists(word, token_element, "pos")
    #word = addIfExists(word, token_element, "ph")
    if "ph" in token_element.attrib:
        mary_trans = token_element.attrib.get("ph")
        ws_trans = mapperMapFromMary(mary_trans, lang)
        word["trans"] = ws_trans

    #In the new version with output_type INTONATION from marytts the following is no longer used
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
    m = re.match("<\?xml .+xml:lang=\"([^\"]*)\"[^>]*>(.*)$", maryxml)
    if m:
        lang = m.group(1)
        maryxml = m.group(2)
        if not maryxml.startswith("<maryxml"):
            maryxml = "<maryxml>"+maryxml
    #print(lang)
    #print(maryxml)
    #sys.exit()
    return (lang,maryxml)

def ws2mary(utterance):

    #print(utterance)
    
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

                #add prosody element if necessary
                if "prosody_range" in phrase or "prosody_pitch" in phrase:
                    prosody_element = ET.Element("prosody")
                    prosody_element = addToElementIfExists(prosody_element, phrase, "prosody_range", drop_prefix="prosody_")
                    prosody_element = addToElementIfExists(prosody_element, phrase, "prosody_pitch", drop_prefix="prosody_")
                    sentence_element.append(prosody_element)
                    prosody_element.append(phrase_element)
                else:                    
                    sentence_element.append(phrase_element)

                tokens = phrase["tokens"]
                for token in tokens:

                    words = token["words"]

                    #add mtu element if necessary
                    if "mtu" in token and token["mtu"] == True:
                        mtu_element = ET.Element("mtu")
                        phrase_element.append(mtu_element)
                        mtu_element.attrib["orig"] = token["token_orth"]
                        token_parent = mtu_element
                    else:
                        token_parent = phrase_element
                        

                    for word in words:
                        #each word creates one token_element
                        token_element = ET.Element("t")

                        token_element.text = word["orth"]
                        
                        token_element = addToElementIfExists(token_element, word, "accent")
                        token_element = addToElementIfExists(token_element, word, "g2p_method")
                        token_element = addToElementIfExists(token_element, word, "pos")
                        #token_element = addToElementIfExists(token_element, word, "ph")
                        if "trans" in word:
                            ws_trans = word["trans"]
                            mary_trans = mapperMapToMary(ws_trans, lang)
                            token_element.attrib["ph"] = mary_trans

                        #In the new version with output_type INTONATION from marytts the following is no longer used
                        if "syllables" in word:
                            #normal word
                            syllables = word["syllables"]
                        else:
                            #punctuation
                            syllables = []
                            
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

                        #each word creates one token_element
                        token_parent.append(token_element)

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

def mapperMapFromMary(trans, lang):
    #TODO
    #Configure elsewhere
    #get symbol set names

    if lang == "sv":
        from_symbol_set = "sv-se_sampa_mary"
        to_symbol_set = "sv-se_ws-sampa"
    elif lang == "en":
        from_symbol_set = "en-us_sampa_mary"
        to_symbol_set = "en-us_cmu"
    #elif lang == "en-US":
    #    from_symbol_set = "en-us_sampa_mary"
    #    to_symbol_set = "en-us_cmu"
    else:
        print("No marytts mapper defined for language %s" % lang)
        return trans

    url = host+"/mapper/map?to=%s&from=%s&trans=%s" % (to_symbol_set, from_symbol_set, quote_plus(trans))


    r = requests.get(url)
    print("MAPPER URL: "+r.url)
    response = r.text
    #print("RESPONSE: %s" % response)
    try:
        response_json = json.loads(response)
        #print("RESPONSE_JSON: %s" % response_json)
        new_trans = response_json["Result"]
    except:
        print("ERROR: unable to map %s, from %s to %s. response was %s" % (trans, from_symbol_set, to_symbol_set, response))
        raise
    #print("NEW TRANS: %s" % new_trans)
    return new_trans

def mapperMapToMary(trans, lang):
    #TODO
    #Configure elsewhere
    #get symbol set names
    if lang == "sv":
        to_symbol_set = "sv-se_sampa_mary"
        from_symbol_set = "sv-se_ws-sampa"
    elif lang == "en":
        to_symbol_set = "en-us_sampa_mary"
        from_symbol_set = "en-us_cmu"
    #elif lang == "en-US":
    #    to_symbol_set = "en-us_sampa_mary"
    #    from_symbol_set = "en-us_cmu"
    else:
        print("No marytts mapper defined for language %s" % lang)
        return trans

    

    #url = "https://morf.se/ws_service/mapper/map?to=%s&from=%s&trans=%s" % (to_symbol_set, from_symbol_set, quote_plus(trans))
    url = host+"/mapper/map?to=%s&from=%s&trans=%s" % (to_symbol_set, from_symbol_set, quote_plus(trans))
    
    r = requests.get(url)
    print("MAPPER URL: %s" % r.url)
    response = r.text
    print("MAPPER RESPONSE: %s" % response)
    try:
        response_json = json.loads(response)
    except json.JSONDecodeError:
        print("JSONDecodeError:")
        print("RESPONSE: %s" % response)
        raise
        
    new_trans = response_json["Result"]

    #Special cases for Swedish pre-r allophones that are not handled by the mapper (because mary uses an old version of the phoneme set that desn't distinguish between normal and r-coloured E/{ (always E) and 2/9 (always 9). This should change in mary later on.
    if lang == "sv":
        new_trans = re.sub("{( -)? ",r"E\1 ", new_trans)
        new_trans = re.sub("2(:? -) r? ",r"9\1 r", new_trans)


    print("NEW TRANS: %s" % new_trans)

    
    return new_trans
 



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
        #print("")
        #print(u)
        #print(w_test4)
        self.assertEqual(u, w_test4)

    def test5(self):
        u = mary2ws(m_test5)
        #print("")
        #print(u)
        #print(w_test5)
        self.assertEqual(u, w_test5)

    def test6(self):
        u = mary2ws(m_test6)
        #print("")
        #print(u)
        #print(w_test6)
        self.assertEqual(u, w_test6)

class TestWs2M(unittest.TestCase):

    def test1(self):
        m1 = ws2mary(w_test1)
        #m1 = re.sub('" />', '"/>', m1)

        m2 = re.sub("\n","",m_test1)

        #print()
        #print(m1)
        #print(m2)
        self.assertEqual(m1, m2)
        
    def test2(self):
        m1 = ws2mary(w_test2)
        #m1 = re.sub('" />', '"/>', m1)

        m2 = re.sub("\n","",m_test2)

        #print("")
        #print(m1)
        #print(m2)
        self.assertEqual(m1, m2)
        
    def test3(self):
        m1 = ws2mary(w_test3)
        m1 = re.sub('" />', '"/>', m1)

        m2 = re.sub("\n","",m_test3)

        #print("")
        #print(m1)
        #print(m2)
        self.assertEqual(m1, m2)
        
    def test4(self):
        m1 = ws2mary(w_test4)
        m1 = re.sub('" />', '"/>', m1)

        m2 = re.sub("\n","",m_test4)

        #print("")
        #print(m1)
        #print(m2)
        self.assertEqual(m1, m2)
        
    def test5(self):
        m1 = ws2mary(w_test5)
        m1 = re.sub('" />', '"/>', m1)

        m2 = re.sub("\n","",m_test5)

        #print("")
        #print(m1)
        #print(m2)
        self.assertEqual(m1, m2)
        
    def test6(self):
        m1 = ws2mary(w_test6)
        m1 = re.sub('" />', '"/>', m1)

        m2 = re.sub("\n","",m_test6)

        #print("")
        #print(m1)
        #print(m2)
        self.assertEqual(m1, m2)
        


def maryxml2utt(xml):    
    utt =  mary2ws(xml)
    lang = utt["lang"]
    return (lang, utt)

def utt2maryxml(lang, utt):
    xml = ws2mary(utt)
    return xml

if __name__ == '__main__':
    unittest.main()
