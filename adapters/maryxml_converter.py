# -*- coding: utf-8 -*-

import sys, re


#For conversion between maryxml and internal utt form
#
#
#
#first need a definition of the internal. Hm. It should the same as json. In python a combination of lists and dictionaries.

#Vad är rätt sak att göra? utt->paragraphs->sentences-> osv eller utt->children->children? Det skulle ju bli mer generellt då..

#utt = {}
#utt["name"] = "utt_name"
#utt["text"] = "utt_text"
#utt["paragraphs"] = paragraphs

#paragraphs = {}
#osv

#eller

#node = {}
#node["tag"] = "tag"
#node["name"] = "name"
#node["text"] = "text"
#node["childNodes"] = nodeList

#det blir ju enklare.
#sen kan noderna ha olika attribut beroende på vilken tag det är. 

#poäng är att childNodes alltid är en lista även om det är ett element i den!


import xml.etree.ElementTree as ET
def maryxml2utt(maryxml):
    (lang, maryxml) = dropHeader(maryxml)
    #lang = "sv"

    print(maryxml)

    root = ET.fromstring(maryxml.encode('utf-8'))
    #root = ET.fromstring(maryxml)
    ps = root.findall(".//p")
    
    utt = {"tag":"utt"}

    if len(ps) > 0:
        utt["children"] = buildUtt(ps)
    return (lang, utt)


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

def buildUtt(elements):
    nodelist = []
    for element in elements:
        tag = element.tag
        node = {"tag":tag}
        if len(element) > 0:
            node["children"] = buildUtt(element)

        #print element.attrib
        for attr in element.attrib.keys():
            #print "ATTR: %s" % attr
            node[attr] = element.attrib[attr]

        text = getText(element)
        text = text.strip()
        if text != "":
            #print "TEXT: %s" % text
            node["text"] = text

        nodelist.append(node)
    return nodelist

def getText(element):
    text = ""
    if element.text:
        text = element.text
    if element.tail:
        text += element.tail
    text = text.replace(u"\xad", " ")
    return text



def utt2maryxml(lang, utt):
    header = '<?xml version="1.0" encoding="UTF-8"?>'

    #<maryxml xmlns="http://mary.dfki.de/2002/MaryXML" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="0.5" xml:lang="%s">' % lang

    maryxml = ET.Element("maryxml")

    maryxml.attrib["xmlns"] = "http://mary.dfki.de/2002/MaryXML"
    maryxml.attrib["xmlns:xsi"] = "http://www.w3.org/2001/XMLSchema-instance"
    maryxml.attrib["version"] = "0.5"
    maryxml.attrib["xml:lang"] = lang

    pars = utt["children"]
    for par in buildMaryxml(pars):
        maryxml.append(par)


    if sys.version_info.major == 2:
        #This works in python2.7
        maryxmlstring = ET.tostring(maryxml, encoding="utf-8")
    else:
        #This works in python3
        maryxmlstring = ET.tostring(maryxml, encoding="unicode")

    print("utt2maryxml maryxml:\n%s%s" % (header,maryxmlstring))
    return "%s%s" % (header,maryxmlstring)

    
def buildMaryxml(items):
    elementlist = []
    for item in items:
        element = ET.Element(item["tag"])
        if "children" in item:
            for child in buildMaryxml(item["children"]):
                element.append(child)
        if "text" in item:
            element.text = item["text"]

        for key in item.keys():
            if not key in ["tag","children","text"]:
                element.attrib[key] = item[key]

        elementlist.append(element)
    return elementlist
 


def test():   
    maryxml = """<?xml version="1.0" encoding="UTF-8"?><maryxml xmlns="http://mary.dfki.de/2002/MaryXML" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="0.5" xml:lang="sv">
<p>
<s>
<t test="hej">
Hej
</t>
</s>
</p>
</maryxml>"""



    utt = {
        "tag":"utt",
        "children": [
            {
                "tag":"p",
                "children":[
                    {
                        "tag":"s",
                        "children": [
                            {
                                "tag":"t",
                                "test":"hej",
                                "text":"Hej",
                            }
                        ]
                    }
                ]
            }
        ]
    }
    
    (lang, utt2) = maryxml2utt(maryxml)
    maryxml2 = utt2maryxml(lang, utt2)
    if utt != utt2:
        print("ERROR")
        print(utt)
        print(utt2)
        #sys.exit()


    maryxml = dropHeader(maryxml)[1]
    maryxml = ET.tostring(ET.fromstring(maryxml))

    maryxml2 = dropHeader(maryxml2)[1]

    if maryxml != maryxml2:
        print("ERROR")
        print(type(maryxml))
        print(type(maryxml2))
        
        print("|%s|" % maryxml)
        print("|%s|" % maryxml2)

    
    maryxml3 = """<?xml version="1.0" encoding="UTF-8"?><maryxml xmlns="http://mary.dfki.de/2002/MaryXML" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="0.5" xml:lang="sv">
<p>
<s>
<t g2p_method="lexicon" ph="' t E s t" pos="content">
test
</t>
<mtu orig="123">
<t g2p_method="rules" ph="E - t h u0 n - d r a - C }: - g u: - ' t r e:" pos="content">
ett­hundra­tjugo­tre
</t>
</mtu>
<t g2p_method="lexicon" ph="' s l }: t" pos="content">
slut
</t>
<t pos="$PUNCT">
.
</t>
</s>
</p>
</maryxml>
"""
    maryxml2utt(maryxml3)

if __name__ == "__main__":
    test()
