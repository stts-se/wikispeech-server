import requests
import tokeniser, maryxml_converter
import xml.etree.ElementTree as ET

url = 'https://demo.morf.se/marytts/process'

def marytts_preproc(lang, text):
    if lang == "en":
        locale = "en_US"
    else:
        locale = lang

    payload = {
        "INPUT_TYPE":"TEXT",
        #"OUTPUT_TYPE":"WORDS",
        "OUTPUT_TYPE":"PHONEMES",
        "LOCALE":locale,
        "INPUT_TEXT":text
    }
    #Using output_type PHONEMES means that marytts will phonetise the words first, and lexLookup will change the transcription if a word is found
    r = requests.get(url, params=payload)
    #print "CALLING MARYTTS: ", r.url
    
    xml = r.text
    #print "REPLY:", xml
    #(utt,marylang) = maryxml2utt(xml)
    (marylang, utt) = maryxml_converter.maryxml2utt(xml)

    return utt



def marytts_preproc_tokenised(lang, utt):
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
    r = requests.get(url, params=payload)
    print("CALLING MARYTTS: %s" % r.url)
    
    xml = r.text
    print("REPLY: %s" % xml)
    import maryxml_converter
    (marylang, utt) = maryxml_converter.maryxml2utt(xml)
    #(utt,marylang) = maryxml2utt(xml)
    print("marytts_preproc_tokenised returns %s" % utt)
    return utt



def marytts_postproc(lang, utt):
    if lang == "en":
        locale = "en_US"
    else:
        locale = lang

    #xml = utt2maryxml(utt, lang)
    xml = maryxml_converter.utt2maryxml(lang, utt)

    payload = {
        "INPUT_TYPE":"PHONEMES",
        "OUTPUT_TYPE":"ALLOPHONES",
        "LOCALE":locale,
        "INPUT_TEXT":xml
    }
    r = requests.post(url, params=payload)
    #print "CALLING MARYTTS: ", r.url

    #Should raise an error if status is not OK (In particular if the url-too-long issue appears)
    r.raise_for_status()


    
    xml = r.text
    print("REPLY: %s" % xml)
    #(utt,marylang) = maryxml2utt(xml)
    (marylang, utt) = maryxml_converter.maryxml2utt(xml)
    print("marytts_postproc returning: %s" % utt)
    return utt













def synthesise(lang,voice,input):

    if "marytts_locale" in voice:
        locale = voice["marytts_locale"]
    else:
        locale = lang

    #maryxml = utt2maryxml(input, lang)
    maryxml = maryxml_converter.utt2maryxml(lang, input)
    print("MARYXML: %s" % maryxml)
        
    #url = 'https://demo.morf.se/marytts/process'
    url = "%s/%s" % (voice["server"]["url"], "process")

    params = {"INPUT_TYPE":"ALLOPHONES",
              "OUTPUT_TYPE":"REALISED_ACOUSTPARAMS",
              "LOCALE":locale,
              "VOICE":voice["name"],
              "INPUT_TEXT":maryxml}
    r = requests.post(url,params=params)

    print("runMarytts PARAMS URL (length %d): %s" % (len(r.url), r.url))

    xml = r.text.encode("utf-8")

    print("REPLY: %s" % xml)

    #Should raise an error if status is not OK (In particular if the url-too-long issue appears)
    r.raise_for_status()



    output_tokens = maryxml2tokensET(xml)



    params = {"INPUT_TYPE":"ALLOPHONES",
              "OUTPUT_TYPE":"AUDIO",
              "AUDIO":"WAVE_FILE",
              "LOCALE":lang,
              "VOICE":voice["name"],
              "INPUT_TEXT":maryxml}
    #actually synthesising it here so should be no problem saving the audio and returning link to that rather than the marytts synthesising url
    #As it is it will be synthesised again when the audio tag is put on page
    audio_r = requests.get(url,params=params)
    audio_url = audio_r.url

    #print("runMarytts AUDIO_URL: %s" % audio_url)

    return (audio_url, output_tokens)















def dropMaryHeader(utt):
    utt = utt["maryxml"]["p"]
    return utt

def addMaryHeader(utt,lang):
    newutt = {"maryxml": {
        "@xmlns": "http://mary.dfki.de/2002/MaryXML", 
        "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance", 
        "@version": "0.5", 
        "@xml:lang": lang, 
        "p": utt
    }}
    return newutt

def maryxml2utt(maryxmlstring):
    utt = xmltodict.parse(maryxmlstring)
    lang = utt["maryxml"]["@xml:lang"]
    utt = dropMaryHeader(utt)
    return (utt, lang)

def utt2maryxml(utt, lang):
    utt = addMaryHeader(utt,lang)
    maryxmlstring = xmltodict.unparse(utt)
    return maryxmlstring

def json2utt(jsonstring):
    return json.loads(jsonstring)

def utt2json(utt):
    return json.dumps(utt)

def maryxml2tokensET(maryxmlstring):
    try:
        root = ET.fromstring(maryxmlstring)
    except:
        print("ERROR IN PARSING XML:\n%s" % maryxmlstring)
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
            #print "S:",s
            phrases = s.findall(".//{http://mary.dfki.de/2002/MaryXML}phrase")
            for phrase in phrases:
                #print "PHRASE:", phrase
                for child in phrase:
                    #print "CHILD:", child.tag
                    if child.tag == "{http://mary.dfki.de/2002/MaryXML}t":
                        #orth = child.text.strip()
                        orth = "".join(child.itertext()).strip()
                        #print "ORTH:", orth
                        tokendur = 0
                        for ph in child.findall(".//{http://mary.dfki.de/2002/MaryXML}ph"):
                            #print ph.attrib
                            #tokendur += ph.attrib['{http://mary.dfki.de/2002/MaryXML}d']
                            tokendur += int(ph.attrib['d'])

                        endtime += tokendur
                        endtime_seconds = endtime/1000.0
                        token = (orth,endtime_seconds)
                    elif child.tag == "{http://mary.dfki.de/2002/MaryXML}mtu":
                        #orth = child.text.strip()
                        orth = "".join(child.itertext()).strip()
                        #print "ORTH:", orth
                        tokendur = 0
                        for ph in child.findall(".//{http://mary.dfki.de/2002/MaryXML}ph"):
                            #print ph.attrib
                            #tokendur += ph.attrib['{http://mary.dfki.de/2002/MaryXML}d']
                            tokendur += int(ph.attrib['d'])

                        endtime += tokendur
                        endtime_seconds = endtime/1000.0
                        token = (orth,endtime_seconds)
                    elif child.tag == "{http://mary.dfki.de/2002/MaryXML}boundary":
                        orth = "PAUSE"
                        orth = ""
                        #print "ORTH:", orth
                        #print child.attrib
                        #endtime += child.attrib['{http://mary.dfki.de/2002/MaryXML}duration']
                        endtime += int(child.attrib['duration'])
                        endtime_seconds = endtime/1000.0
                        token = (orth,endtime_seconds)
                    sentence.append(token)
                    output_tokens.append(token)
    #print utt
    #return (output_tokens, lang)
    return output_tokens

def maryxml2uttET(maryxmlstring):
    print("MARYXMLSTRING: %s" % maryxmlstring)
    root = ET.fromstring(maryxmlstring)
    #root = doc.getroot()
    lang = root.attrib['{http://www.w3.org/XML/1998/namespace}lang']
    #lang = utt2["maryxml"]["@xml:lang"]
    print("ROOT: %s" % root)
    ps = root.findall(".//{http://mary.dfki.de/2002/MaryXML}p")
    utt = []
    for p in ps:
        print("P: %s" % p)
        #ss = p.findall(".//{http://mary.dfki.de/2002/MaryXML}s")
        ss = p.findall(".//{http://mary.dfki.de/2002/MaryXML}s")
        print("SS: %s" % ss)
        paragraph = []
        utt.append(paragraph)
        for s in ss:
            sentence = []
            paragraph.append(sentence)
            print("S: %s" % s)
            phrases = s.findall(".//{http://mary.dfki.de/2002/MaryXML}phrase")

            if len(phrases) == 0:
                phrases = [s]


            for phrase in phrases:
                print("PHRASE: %s" % phrase)
                for child in phrase:
                    print("CHILD: %s" % child.tag)
                    if child.tag == "{http://mary.dfki.de/2002/MaryXML}t":
                        #orth = child.text.strip()
                        orth = "".join(child.itertext()).strip()
                        #print "ORTH:", orth
                        for ph in child.findall(".//{http://mary.dfki.de/2002/MaryXML}ph"):
                            pass
                        token = orth
                    elif child.tag == "{http://mary.dfki.de/2002/MaryXML}mtu":
                        #orth = child.text.strip()
                        print("MTU attrib: %s" % child.attrib)
                        #orth = child.attrib['{http://mary.dfki.de/2002/MaryXML}orig']
                        orth = child.attrib['orig']
                        #print "ORTH:", orth
                        for ph in child.findall(".//{http://mary.dfki.de/2002/MaryXML}ph"):
                            pass
                        token = orth
                    elif child.tag == "{http://mary.dfki.de/2002/MaryXML}boundary":
                        orth = "PAUSE"
                        orth = ""
                        #print "ORTH:", orth
                        #print child.attrib
                        #endtime += child.attrib['{http://mary.dfki.de/2002/MaryXML}duration']
                        token = orth
                    sentence.append(token)
            print("SENTENCE: %s" % sentence)
    print("UTT: %s" % utt)
    return (utt, lang)
