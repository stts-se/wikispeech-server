import sys
import json
import xml.etree.ElementTree as ET
import xmltodict


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
    utt2 = xmltodict.parse(maryxmlstring)
    lang = utt2["maryxml"]["@xml:lang"]
    utt2 = dropMaryHeader(utt2)
    return (utt2, lang)

def maryxml2uttET(maryxmlstring):
    root = ET.fromstring(maryxmlstring)
    #root = doc.getroot()
    lang = root.attrib['{http://www.w3.org/XML/1998/namespace}lang']
    #lang = utt2["maryxml"]["@xml:lang"]
    ps = root.findall(".//{http://mary.dfki.de/2002/MaryXML}p")
    utt = []
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
                    elif child.tag == "{http://mary.dfki.de/2002/MaryXML}boundary":
                        orth = "PAUSE"
                        #print "ORTH:", orth
                        #print child.attrib
                        #endtime += child.attrib['{http://mary.dfki.de/2002/MaryXML}duration']
                        endtime += int(child.attrib['duration'])
                        endtime_seconds = endtime/1000.0
                        token = (orth,endtime_seconds)
                    sentence.append(token)
    #print utt
    return (utt, lang)

def utt2maryxml(utt, lang):
    utt = addMaryHeader(utt,lang)
    maryxmlstring = xmltodict.unparse(utt)
    return maryxmlstring

def json2utt(jsonstring):
    return json.loads(jsonstring)

def utt2json(utt):
    return json.dumps(utt)



if __name__ == "__main__":
    #jsonstring = open("sv_example_new.json").read()
    #utt1 = json2utt(jsonstring)
    
    maryxmlstring = open("sv_example_ra2.xml").read()
    (utt2,lang) = maryxml2uttET(maryxmlstring)
    print utt2
    sys.exit()

    if utt1 != utt2:
        print utt1
        print "------------------------------------------------------------"
        print utt2



    maryxmlstring2 = utt2maryxml(utt2,lang)

    #They are not actually equal strings, but 'equal' xml, so need to parse them to test
    if xmltodict.parse(maryxmlstring) != xmltodict.parse(maryxmlstring2):
        print maryxmlstring
        print "------------------------------------------------------------"
        print maryxmlstring2

    #print utt2json(utt2)
