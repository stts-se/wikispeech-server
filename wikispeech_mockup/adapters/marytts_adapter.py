import requests, json
#import tokeniser
#from adapters.maryxml_converter import *
try:
    from adapters.new_maryxml_converter_with_mapper import *
except:
    #If running as __main__
    from new_maryxml_converter_with_mapper import *
    
import xml.etree.ElementTree as ET

try:
    #Python 3
    from urllib.parse import quote_plus
except:
    #Python 2
    from urllib import quote_plus


#BUGFIX TODO
#configure elsewhere
#url = 'https://demo.morf.se/marytts/process'
#url = "http://morf.se:59125/process"
url = "http://localhost:59125/process"

def marytts_preproc(lang, text, input_type="text"):
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
        text = mapSsmlTranscriptionsToMary(text, lang)

    payload = {
        "INPUT_TYPE": mary_input_type,
        #"OUTPUT_TYPE": "WORDS",
        "OUTPUT_TYPE": "INTONATION",
        #"OUTPUT_TYPE": "ALLOPHONES",
        "LOCALE": locale,
        "INPUT_TEXT": text
    }
    #Using output_type PHONEMES/INTONATION/ALLOPHONES means that marytts will phonetise the words first, and lexLookup will change the transcription if a word is found
    r = requests.get(url, params=payload)
    print("CALLING MARYTTS: %s" % r.url)
    
    xml = r.text
    #print "REPLY:", xml
    (marylang, utt) = maryxml2utt(xml)

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
    (marylang, utt) = maryxml2utt(xml)
    print("marytts_preproc_tokenised returns %s" % utt)
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
    r = requests.post(url, params=payload)
    print("CALLING MARYTTS: %s" % r.url)

    #Should raise an error if status is not OK (In particular if the url-too-long issue appears)
    r.raise_for_status()


    
    xml = r.text
    print("REPLY: %s" % xml)
    (marylang, utt) = maryxml2utt(xml)
    print("marytts_postproc returning: %s" % utt)
    return utt










def synthesise(lang,voice,input, presynth=False):
    if presynth:
        return synthesise_json(lang,voice,input)
    else:
        return synthesise_old(lang,voice,input)



def synthesise_old(lang,voice,input):

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
    print("MARYXML: %s" % maryxml)
     
    #BUGFIX TODO
    #url = 'https://demo.morf.se/marytts/process'
    #url = "%s/%s" % (voice["server"]["url"], "process")
    #url = "http://morf.se:59125/process"

    params = {
        "INPUT_TYPE":"INTONATION",
        #"INPUT_TYPE":"ALLOPHONES",
        "OUTPUT_TYPE":"REALISED_ACOUSTPARAMS",
        "LOCALE":locale,
        "VOICE":voice["name"],
        "INPUT_TEXT":maryxml
    }
    r = requests.post(url,params=params)

    print("runMarytts PARAMS URL (length %d): %s" % (len(r.url), r.url))

    xml = r.text.encode("utf-8")

    print("REPLY: %s" % xml)

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
    audio_r = requests.get(url,params=params)
    audio_url = audio_r.url

    #print("runMarytts AUDIO_URL: %s" % audio_url)

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
    print("MARYXML: %s" % maryxml)
     
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
    r = requests.post(url,params=params)

    print("runMarytts PARAMS URL (length %d): %s" % (len(r.url), r.url))

    json = r.json()

    print("REPLY: %s" % json)

    #Should raise an error if status is not OK (In particular if the url-too-long issue appears)
    r.raise_for_status()

    audio_url = json["audio"]
    output_tokens = json["tokens"]

    #print("runMarytts AUDIO_URL: %s" % audio_url)

    return (audio_url, output_tokens)



def mapSsmlTranscriptionsToMary(ssml, lang):
    phoneme_elements = re.findall("(<phoneme [^>]+>)", ssml)
    for element in phoneme_elements:
        #print(element)
        trans = re.findall("ph=\"(.+)\">", element)[0]
        #print(trans)
        mary_trans = mapperMapToMary(trans.replace("&quot;","\""), lang)
        #print(mary_trans)
        ssml = re.sub(trans, mary_trans.replace("\"", "&quot;"), ssml)
    #print("MAPPED SSML: %s" % ssml)
    return ssml

        

# def mapperMapToMary(trans):
#     #TODO
#     #Configure elsewhere
#     #get symbol set names
#     url = "http://localhost:8787/mapper/map?from=sv-se_ws-sampa&to=sv-se_sampa_mary&trans=%s" % quote_plus(trans)

#     r = requests.get(url)
#     print(r.url)
#     response = r.text
#     print("RESPONSE: %s" % response)
#     #try:
#     response_json = json.loads(response)
#     print("RESPONSE_JSON: %s" % response_json)
#     new_trans = response_json["Result"]
#     print("NEW TRANS: %s" % new_trans)
#     return new_trans
#     #except:
#     #    e = sys.exc_info()[0]
#     #    print("ERROR: unable to get mapper result (%s). Response was: %s" % (e, response))
#     #    return None









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

# def maryxml2utt(maryxmlstring):
#     utt = xmltodict.parse(maryxmlstring)
#     lang = utt["maryxml"]["@xml:lang"]
#     utt = dropMaryHeader(utt)
#     return (utt, lang)

# def utt2maryxml(utt, lang):
#     utt = addMaryHeader(utt,lang)
#     maryxmlstring = xmltodict.unparse(utt)
#     return maryxmlstring

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
                    expanded = None
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
                        #endtime_seconds = endtime/1000.0
                        #token = (orth,endtime_seconds)
                    elif child.tag == "{http://mary.dfki.de/2002/MaryXML}mtu":
                        print(child.attrib)
                        #The expanded words of the mtu
                        expanded = "".join(child.itertext()).strip()
                        #The original orthography
                        #TODO return both
                        orth = child.attrib["orig"]
                        print("ORTH:", orth)
                        tokendur = 0
                        for ph in child.findall(".//{http://mary.dfki.de/2002/MaryXML}ph"):
                            #print ph.attrib
                            #tokendur += ph.attrib['{http://mary.dfki.de/2002/MaryXML}d']
                            tokendur += int(ph.attrib['d'])

                        endtime += tokendur
                        #endtime_seconds = endtime/1000.0
                        #token = (orth,endtime_seconds)
                    elif child.tag == "{http://mary.dfki.de/2002/MaryXML}boundary":
                        orth = "PAUSE"
                        orth = ""
                        #print "ORTH:", orth
                        #print child.attrib
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
        mapped = mapSsmlTranscriptionsToMary(ws_ssml, "sv")
        self.assertEqual(mapped, mary_ssml)


class TestPreproc(unittest.TestCase):

    def test1(self):
        input_text = "Ett öra."
        expected = {'paragraphs': [{'sentences': [{'phrases': [{'boundary': {'tone': 'L-L%', 'breakindex': '5'}, 'tokens': [{'words': [{'pos': 'content', 'trans': '" E t', 'orth': 'Ett', 'accent': 'L+H*', 'g2p_method': 'lexicon'}], 'token_orth': 'Ett'}, {'words': [{'pos': 'content', 'trans': '"" 2: . r a', 'orth': 'öra', 'accent': '!H*', 'g2p_method': 'lexicon'}], 'token_orth': 'öra'}, {'words': [{'pos': '$PUNCT', 'orth': '.'}], 'token_orth': '.'}]}]}]}], 'lang': 'sv'}

        result = marytts_preproc("sv", input_text)
        print(result)
        self.assertEqual(expected, result)

        

if __name__ == "__main__":
    unittest.main()


