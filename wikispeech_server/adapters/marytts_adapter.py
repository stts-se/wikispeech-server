import sys, requests, json, re
import xml.etree.ElementTree as ET

import wikispeech_server.config as config
import wikispeech_server.log as log
import wikispeech_server.wikispeech as ws


try:
    #Python 3
    from urllib.parse import quote_plus
except:
    #Python 2
    from urllib import quote_plus




marytts_url = config.config.get("Services", "marytts")
mapper_url = config.config.get("Services", "lexicon")



def marytts_preproc(text, lang, tp_config, input_type="text"):

    if lang == "en":
        locale = "en_US"
    elif lang == "nb":
        locale = "no"
    else:
        locale = lang

    if input_type == "ssml":
        mary_input_type = "SSML"
    else:
        mary_input_type = "TEXT"

    if input_type == "ssml":
        text = mapSsmlTranscriptionsToMary(text, lang, tp_config)

    #FIX FOR ISSUE T164917: 600-talet loses number
    #Marytts uses ICU to expand numerals, but only numerals that are a full token.
    #In cases like this the number is just dropped.
    #The very simple fix is to insert space before the hyphen
    text = re.sub(r"([0-9]+)-tal",r"\1 -tal", text)
        
    payload = {
        "INPUT_TYPE": mary_input_type,
        #"OUTPUT_TYPE": "WORDS",
        "OUTPUT_TYPE": "INTONATION",
        #"OUTPUT_TYPE": "ALLOPHONES",
        "LOCALE": locale,
        "INPUT_TEXT": text
    }
    #Using output_type PHONEMES/INTONATION/ALLOPHONES means that marytts will phonetise the words first, and lexLookup will change the transcription if a word is found
    r = requests.get(marytts_url, params=payload)
    log.debug("CALLING MARYTTS: %s" % r.url)
    
    xml = r.text
    #log.debug "REPLY:", xml
    (marylang, utt) = maryxml2utt(xml, tp_config)

    return utt



def marytts_preproc_tokenised_TOREMOVE(lang, utt):
    if lang == "en":
        locale = "en_US"
    else:
        locale = lang

    maryxml = tokeniser.utt2maryxml_TOKENS(lang,utt)

    payload = {
        "INPUT_TYPE":"TOKENS",
        #"OUTPUT_TYPE":"WORDS",
        "OUTPUT_TYPE":"PHONEMES",
        "LOCALE":locale,
        "INPUT_TEXT":maryxml
    }
    #Using output_type PHONEMES means that marytts will phonetise the words first, and lexLookup will change the transcription if a word is found
    r = requests.get(marytts_url, params=payload)
    log.debug("CALLING MARYTTS: %s" % r.url)
    
    xml = r.text
    log.debug("REPLY: %s" % xml)
    (marylang, utt) = maryxml2utt(xml)
    log.debug("marytts_preproc_tokenised returns %s" % utt)
    return utt



def marytts_postproc(lang, utt):
    if lang == "en":
        locale = "en_US"
        xmllang = "en"
    elif lang == "nb":
        locale = "no"
        xmllang = "no"
    else:
        locale = lang
        xmllang = lang

    #xmllang, not lang, here. Marytts needs the xml:lang to match first part of LOCALE..
    xml = utt2maryxml(xmllang, utt)

    payload = {
        #"INPUT_TYPE":"PHONEMES",
        "INPUT_TYPE":"INTONATION",
        "OUTPUT_TYPE":"ALLOPHONES",
        "LOCALE":locale,
        "INPUT_TEXT":xml
    }
    r = requests.post(marytts_url, params=payload)
    log.debug("CALLING MARYTTS: %s" % r.url)

    #Should raise an error if status is not OK (In particular if the url-too-long issue appears)
    r.raise_for_status()


    
    xml = r.text
    log.debug("REPLY: %s" % xml)
    (marylang, utt) = maryxml2utt(xml)
    log.debug("marytts_postproc returning: %s" % utt)
    return utt










def synthesise(lang,voice,input, presynth=False):
    if presynth:
        return synthesise_json(lang,voice,input)
    else:
        return synthesise_default(lang,voice,input)



def synthesise_default(lang,voice,input):

    if lang == "nb":
        xmllang = "no"
    else:
        xmllang = lang

    if "marytts_locale" in voice:
        locale = voice["marytts_locale"]
    else:
        locale = lang

    #xmllang, not lang, here. Marytts needs the xml:lang to match first part of LOCALE..
    maryxml = utt2maryxml(xmllang, input, voice)
    log.debug("MARYXML: %s" % maryxml)
     

    params = {
        "INPUT_TYPE":"INTONATION",
        #"INPUT_TYPE":"ALLOPHONES",
        "OUTPUT_TYPE":"REALISED_ACOUSTPARAMS",
        "LOCALE":locale,
        "VOICE":voice["name"],
        "INPUT_TEXT":maryxml
    }
    r = requests.post(marytts_url,params=params)

    log.debug("runMarytts PARAMS URL (length %d): %s" % (len(r.url), r.url))

    xml = r.text.encode("utf-8")

    log.debug("REPLY: %s" % xml)

    #Should raise an error if status is not OK (In particular if the url-too-long issue appears)
    r.raise_for_status()



    output_tokens = maryxml2tokensET(xml)



    params = {
        "INPUT_TYPE":"INTONATION",
        #"INPUT_TYPE":"ALLOPHONES",
        "OUTPUT_TYPE":"AUDIO",
        "AUDIO":"WAVE_FILE",
        "LOCALE":lang,
        "VOICE":voice["name"],
        "INPUT_TEXT":maryxml
    }
    #actually synthesising it here so should be no problem saving the audio and returning link to that rather than the marytts synthesising url
    #As it is it will be synthesised again when the audio tag is put on page
    audio_r = requests.get(marytts_url,params=params)
    audio_url = audio_r.url

    #log.debug("runMarytts AUDIO_URL: %s" % audio_url)

    return (audio_url, output_tokens)


def synthesise_json(lang,voice,input):

    if lang == "nb":
        xmllang = "no"
    else:
        xmllang = lang

    if "marytts_locale" in voice:
        locale = voice["marytts_locale"]
    else:
        locale = lang

    #xmllang, not lang, here. Marytts needs the xml:lang to match first part of LOCALE..
    maryxml = utt2maryxml(xmllang, input)
    log.debug("MARYXML: %s" % maryxml)
     
    #BUGFIX TODO
    #url = 'https://demo.morf.se/marytts/process'
    #url = "%s/%s" % (voice["server"]["url"], "process")

    #url = "http://morf.se:59125/process"
    #url = "http://localhost:59125/process"
    

    params = {"INPUT_TYPE":"ALLOPHONES",
              "OUTPUT_TYPE":"WIKISPEECH_JSON",
              "LOCALE":locale,
              "VOICE":voice["name"],
              "INPUT_TEXT":maryxml}
    r = requests.post(marytts_url,params=params)

    log.debug("runMarytts PARAMS URL (length %d): %s" % (len(r.url), r.url))

    json = r.json()

    log.debug("REPLY: %s" % json)

    #Should raise an error if status is not OK (In particular if the url-too-long issue appears)
    r.raise_for_status()

    audio_url = json["audio"]
    output_tokens = json["tokens"]

    #log.debug("runMarytts AUDIO_URL: %s" % audio_url)

    return (audio_url, output_tokens)



#Called from marytts_preproc
def mapSsmlTranscriptionsToMary(ssml, lang, tp_config):
    phoneme_elements = re.findall("(<phoneme [^>]+>)", ssml)
    for element in phoneme_elements:
        #log.debug(element)
        trans = re.findall("ph=\"(.+)\">", element)[0]
        log.debug("ws_trans: %s" % trans)
        mary_trans = mapperMapToMary(trans.replace("&quot;","\""), lang, tp_config)
        log.debug("mary_trans: %s" % mary_trans)
        ssml = re.sub(trans, mary_trans.replace("\"", "&quot;"), ssml)
    #log.debug("MAPPED SSML: %s" % ssml)
    return ssml

        


def dropMaryHeader_TOREMOVE(utt):
    utt = utt["maryxml"]["p"]
    return utt

def addMaryHeader_TOREMOVE(utt,lang):
    newutt = {"maryxml": {
        "@xmlns": "http://mary.dfki.de/2002/MaryXML", 
        "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance", 
        "@version": "0.5", 
        "@xml:lang": lang, 
        "p": utt
    }}
    return newutt


def json2utt_TOREMOVE(jsonstring):
    return json.loads(jsonstring)

def utt2json_TOREMOVE(utt):
    return json.dumps(utt)


#Called from synthesise_default
def maryxml2tokensET(maryxmlstring):
    try:
        root = ET.fromstring(maryxmlstring)
    except:
        log.error("ERROR IN PARSING XML:\n%s" % maryxmlstring)
        #raise with no argument re-raises the last exception
        raise
    #root = doc.getroot()
    lang = root.attrib['{http://www.w3.org/XML/1998/namespace}lang']
    #lang = utt2["maryxml"]["@xml:lang"]
    ps = root.findall(".//{http://mary.dfki.de/2002/MaryXML}p")
    utt = []
    output_tokens = []
    endtime = 0
    for p in ps:
        ss = p.findall(".//{http://mary.dfki.de/2002/MaryXML}s")
        paragraph = []
        utt.append(paragraph)
        for s in ss:
            sentence = []
            paragraph.append(sentence)
            #log.debug "S:",s
            phrases = s.findall(".//{http://mary.dfki.de/2002/MaryXML}phrase")
            for phrase in phrases:
                #log.debug "PHRASE:", phrase
                for child in phrase:
                    #log.debug "CHILD:", child.tag
                    expanded = None
                    if child.tag == "{http://mary.dfki.de/2002/MaryXML}t":
                        #orth = child.text.strip()
                        orth = "".join(child.itertext()).strip()                        
                        #log.debug "ORTH:", orth
                        tokendur = 0
                        for ph in child.findall(".//{http://mary.dfki.de/2002/MaryXML}ph"):
                            #log.debug ph.attrib
                            #tokendur += ph.attrib['{http://mary.dfki.de/2002/MaryXML}d']
                            tokendur += int(ph.attrib['d'])

                        endtime += tokendur
                        #endtime_seconds = endtime/1000.0
                        #token = (orth,endtime_seconds)
                    elif child.tag == "{http://mary.dfki.de/2002/MaryXML}mtu":
                        log.debug(child.attrib)
                        #The expanded words of the mtu
                        expanded = "".join(child.itertext()).strip()
                        #The original orthography
                        #TODO return both
                        orth = child.attrib["orig"]
                        log.debug("ORTH: %s" % orth)
                        tokendur = 0
                        for ph in child.findall(".//{http://mary.dfki.de/2002/MaryXML}ph"):
                            #log.debug ph.attrib
                            #tokendur += ph.attrib['{http://mary.dfki.de/2002/MaryXML}d']
                            tokendur += int(ph.attrib['d'])

                        endtime += tokendur
                        #endtime_seconds = endtime/1000.0
                        #token = (orth,endtime_seconds)
                    elif child.tag == "{http://mary.dfki.de/2002/MaryXML}boundary":
                        orth = "PAUSE"
                        orth = ""
                        #log.debug "ORTH:", orth
                        #log.debug child.attrib
                        #endtime += child.attrib['{http://mary.dfki.de/2002/MaryXML}duration']
                        if "duration" in child.attrib:
                            endtime += int(child.attrib['duration'])
                        #endtime_seconds = endtime/1000.0
                        #token = (orth,endtime_seconds)

                    orth = re.sub("\s+", " ", orth)
                    endtime_seconds = endtime/1000.0
                    token = {"orth":orth,"endtime":endtime_seconds}
                    if expanded:
                        expanded = re.sub("\s+", " ", expanded)
                        token["expanded"] = expanded
                    
                    sentence.append(token)
                    output_tokens.append(token)
    #log.debug utt
    #return (output_tokens, lang)
    return output_tokens

def maryxml2uttET_TOREMOVE(maryxmlstring):
    log.debug("MARYXMLSTRING: %s" % maryxmlstring)
    root = ET.fromstring(maryxmlstring)
    #root = doc.getroot()
    lang = root.attrib['{http://www.w3.org/XML/1998/namespace}lang']
    #lang = utt2["maryxml"]["@xml:lang"]
    log.debug("ROOT: %s" % root)
    ps = root.findall(".//{http://mary.dfki.de/2002/MaryXML}p")
    utt = []
    for p in ps:
        log.debug("P: %s" % p)
        #ss = p.findall(".//{http://mary.dfki.de/2002/MaryXML}s")
        ss = p.findall(".//{http://mary.dfki.de/2002/MaryXML}s")
        log.debug("SS: %s" % ss)
        paragraph = []
        utt.append(paragraph)
        for s in ss:
            sentence = []
            paragraph.append(sentence)
            log.debug("S: %s" % s)
            phrases = s.findall(".//{http://mary.dfki.de/2002/MaryXML}phrase")

            if len(phrases) == 0:
                phrases = [s]


            for phrase in phrases:
                log.debug("PHRASE: %s" % phrase)
                for child in phrase:
                    log.debug("CHILD: %s" % child.tag)
                    if child.tag == "{http://mary.dfki.de/2002/MaryXML}t":
                        #orth = child.text.strip()
                        orth = "".join(child.itertext()).strip()
                        #log.debug "ORTH:", orth
                        for ph in child.findall(".//{http://mary.dfki.de/2002/MaryXML}ph"):
                            pass
                        token = orth
                    elif child.tag == "{http://mary.dfki.de/2002/MaryXML}mtu":
                        #orth = child.text.strip()
                        log.debug("MTU attrib: %s" % child.attrib)
                        #orth = child.attrib['{http://mary.dfki.de/2002/MaryXML}orig']
                        orth = child.attrib['orig']
                        #log.debug "ORTH:", orth
                        for ph in child.findall(".//{http://mary.dfki.de/2002/MaryXML}ph"):
                            pass
                        token = orth
                    elif child.tag == "{http://mary.dfki.de/2002/MaryXML}boundary":
                        orth = "PAUSE"
                        orth = ""
                        #log.debug "ORTH:", orth
                        #log.debug child.attrib
                        #endtime += child.attrib['{http://mary.dfki.de/2002/MaryXML}duration']
                        token = orth
                    sentence.append(token)
            log.debug("SENTENCE: %s" % sentence)
    log.debug("UTT: %s" % utt)
    return (utt, lang)


##############
# moved from new_maryxml_converter_with_mapper.py

#Called from marytts_preproc, marytts_postproc
def maryxml2utt(xml, voice):    
    utt =  mary2ws(xml, voice)
    lang = utt["lang"]
    return (lang, utt)

#Called from marytts_postproc, synthesise_default, synthesise_json
def utt2maryxml(lang, utt, voice):
    xml = ws2mary(utt, voice)
    return xml

#mary2ws: 'prosody' and 'phrase' are combined into 'phrase'. ws2mary: 'phrase' is split into 'prosody' and 'phrase'
#mary2ws: 'mtu' and 'token' are combined into 'token', and 'token' is also copied to 'word'
#Called from maryxml2utt
def mary2ws(maryxml, voice):
    (lang, maryxml) = dropHeader(maryxml)
    #lang = "sv"

    #log.debug(maryxml)

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
                    phrase = buildPhrase(phrase_element, lang, voice)
                    phrases.append(phrase)
                elif sentence_child.tag == "prosody":
                    prosody_element = sentence_child
                    #can 'prosody' only contain exactly one 'phrase'? 
                    phrase_element = prosody_element[0]
                    phrase = buildPhrase(phrase_element, lang, voice)

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
                    phrase = buildPhrase(phrase_element, lang, voice)

                    phrases.append(phrase)

                else:
                    log.error("sentence child should not have tag %s" % sentence_child.tag)
                    

    return utterance

#Called from mary2ws
def buildPhrase(phrase_element, lang, voice):
    if phrase_element.tag != "phrase":
        log.error("wrong type of element: %s\n%s" % (phrase_element.tag, phrase_element))
        sys.exit(1)
    tokens = []
    phrase = {"tokens": tokens}
    for phrase_child in phrase_element:
        #log.debug("phrase_child: %s" % phrase_child.tag)
                        
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
            
            word = buildWord(token_element, lang, voice)
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
                word = buildWord(token_element, lang, voice)
                words.append(word)
                #END  'mtu'
        elif phrase_child.tag == "boundary":
            boundary = {}
            boundary = addIfExists(boundary, phrase_child, "breakindex")
            boundary = addIfExists(boundary, phrase_child, "tone")
            phrase["boundary"] = boundary
                            
        else:
            log.warn("phrase child should not have tag %s" % phrase_child.tag)
    return phrase



#Called from buildPhrase
def buildWord(token_element, lang, voice):
    if token_element.tag != "t":
        log.error("wrong type of element: %s\n%s" % (token_element.tag, token_element))
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
        ws_trans = mapperMapFromMary(mary_trans, lang, voice)
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

#Called from buildWord
def addIfExists(addTo, element, attribute, prefix=""):
    if attribute in element.attrib:
        addTo[prefix+attribute] = element.attrib.get(attribute)
    return addTo


#Called from mary2ws
def dropHeader(maryxml):
    lang = None
    maryxml = maryxml.replace("\n","")
    m = re.match("<\?xml .+xml:lang=\"([^\"]*)\"[^>]*>(.*)$", maryxml)
    if m:
        lang = m.group(1)
        maryxml = m.group(2)
        if not maryxml.startswith("<maryxml"):
            maryxml = "<maryxml>"+maryxml
    #log.debug(lang)
    #log.debug(maryxml)
    #sys.exit()
    return (lang,maryxml)

#Called from utt2maryxml
def ws2mary(utterance, voice):

    #log.debug(utterance)
    
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
                            mary_trans = mapperMapToMary(ws_trans, lang, voice)
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

    #log.debug("utt2maryxml maryxml:\n%s%s" % (header,maryxmlstring))


    return "%s%s" % (header,maryxmlstring)


#Called from ws2mary
def addToElementIfExists(element, item, attribute, drop_prefix=""):
    if attribute in item:
        new_attribute = re.sub("^"+drop_prefix, "", attribute)
        element.attrib[new_attribute] = item[attribute]
    return element



#Called from buildWord
def mapperMapFromMary(trans, lang, voice):

    log.info("mapperMapFromMary( %s , %s , %s )" % (trans, lang, voice))

    if "mapper" in voice:
        #Bad names.. It should be perhaps "external" and "internal" instead of "from" and "to"
        to_symbol_set = voice["mapper"]["from"]
        from_symbol_set = voice["mapper"]["to"]
    
    else:
        log.info("No marytts mapper defined for language %s" % lang)
        return trans

    url = mapper_url+"/mapper/map?to=%s&from=%s&trans=%s" % (to_symbol_set, from_symbol_set, quote_plus(trans))


    r = requests.get(url)
    log.debug("MAPPER URL: "+r.url)
    response = r.text
    #log.debug("RESPONSE: %s" % response)
    try:
        response_json = json.loads(response)
        #log.debug("RESPONSE_JSON: %s" % response_json)
        new_trans = response_json["Result"]
    except:
        log.error("unable to map %s, from %s to %s. response was %s" % (trans, from_symbol_set, to_symbol_set, response))
        raise
    #log.debug("NEW TRANS: %s" % new_trans)
    return new_trans


#Called from mapSsmlTranscriptionsToMary, ws2mary
def mapperMapToMary(trans, lang, voice):

    log.debug("mapperMapToMary( %s, %s, %s)" % (trans, lang, voice))
    if "mapper" in voice:
        to_symbol_set = voice["mapper"]["to"]
        from_symbol_set = voice["mapper"]["from"]

        log.info("marytts mapper defined for language %s\nFrom: %s\nTo: %s" % (lang, from_symbol_set, to_symbol_set))
    
    else:        
        log.info("No marytts mapper defined for language %s" % lang)
        return trans

    
    url = mapper_url+"/mapper/map?to=%s&from=%s&trans=%s" % (to_symbol_set, from_symbol_set, quote_plus(trans))
    
    r = requests.get(url)
    log.debug("MAPPER URL: %s" % r.url)
    response = r.text
    log.debug("MAPPER RESPONSE: %s" % response)
    try:
        response_json = json.loads(response)
    except json.JSONDecodeError:
        log.error("JSONDecodeError:")
        log.error("RESPONSE: %s" % response)
        raise
        
    new_trans = response_json["Result"]

    #Special cases for Swedish pre-r allophones that are not handled by the mapper (because mary uses an old version of the phoneme set that desn't distinguish between normal and r-coloured E/{ (always E) and 2/9 (always 9). This should change in mary later on.
    if lang == "sv":
        new_trans = re.sub("{ - ",r"E - ", new_trans)
        new_trans = re.sub("{ ",r"E ", new_trans)
        new_trans = re.sub("2(:? -) r? ",r"9\1 r", new_trans)


    log.debug("NEW TRANS: %s" % new_trans)

    
    return new_trans
 






