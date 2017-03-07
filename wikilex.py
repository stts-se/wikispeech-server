import sys, requests, json

try:
    #Python 3
    from urllib.parse import quote_plus
except:
    #Python 2
    from urllib import quote_plus
    
#cd ~/go/src/github.com/stts-se/pronlex/
#git pull
#cd lexserver
#go run ../createEmptyDB/createEmptyDB.go tmp.db
#go run ../addNSTLexToDB/addNSTLexToDB.go sv.se.nst tmp.db ~/git/wikimedia/langdata/svlex/sprakbanken_nstlex/swe030224NST.pron_utf8.txt
#mv tmp.db pronlex.db
#go run lexserver.go




def lexLookup_worksNotWithPyTokeniser(lang,utt):
    print("lexLookup: %s" % utt)
    #print("utt[s]: %s" % utt["s"])

    #Again - list if there are multiple sentences, otherwise OrderedDict
    tokenlist = []
    if type(utt["s"]) == type([]):
        for u in utt["s"]:
            for t in u["t"]:
                tokenlist.append(t)
    else:
        for t in utt["s"]["t"]:
            tokenlist.append(t)

    #wordByWord or sentenceBySentence
    wordByWord = False

    if wordByWord:
        for t in tokenlist:
            #print(t)
            orth = t["#text"]
            #print(orth)
            ph = getLookup(lang, orth)
            if ph:
                #print(ph)
                t["@ph"] = ph
                #print(t)

    else:
        #get transcriptions for the entire sentence
        orthlist = []
        for t in tokenlist:
            orth = t["#text"]
            orthlist.append(orth)

        responseDict = getLookupBySentence(lang, " ".join(orthlist))

        for t in tokenlist:
            orth = t["#text"]

            if orth.lower() in responseDict:
                ph = responseDict[orth.lower()]
                #print(ph)
                t["@ph"] = ph
                #print(t)
            else:
                print("No trans for %s" % orth)


    return utt

def lexLookup(lang,utt):
    print("lexLookup: %s" % utt)

    tokenlist = []

    for p in utt["paragraphs"]:
        for s in p["sentences"]:
            for phr in s["phrases"]:
                for token in phr["tokens"]:
                    if "mtu" in token and token["mtu"] == True:
                        for word in token["words"]:
                            print("SKIPPING %s" % word)
                    else:

                        #SSML
                        #If there are transcriptions (from marytts) that have no g2p_method, they came from ssml input and should not be overwritten! 
                        #if "g2p_method" in child and child["g2p_method"] in ["rules","lexicon"]:
                        for word in token["words"]:
                            if "g2p_method" in word:
                                tokenlist.append(word)
        

        #get transcriptions for the entire sentence
        orthlist = []
        for t in tokenlist:
            orth = t["orth"]
            orthlist.append(orth)

        responseDict = getLookupBySentence(lang, " ".join(orthlist))
        if responseDict:

            for t in tokenlist:
                orth = t["orth"]

                if orth.lower() in responseDict:
                    ph = responseDict[orth.lower()]
                    #print(ph)
                    t["trans"] = ph
                    #print(t)
                else:
                    print("No trans for %s" % orth)


    return utt




def lexLookupOLD(lang,utt):
    print("lexLookup: %s" % utt)
    #print("utt[s]: %s" % utt["s"])


    

    #Again - list if there are multiple sentences, otherwise OrderedDict
    tokenlist = []
    #if type(utt["s"]) == type([]):
    #    for u in utt["s"]:
    #        for t in u["t"]:
    #            tokenlist.append(t)
    #else:
    #    for t in utt["s"]["t"]:
    #        tokenlist.append(t)


    for p in utt["children"]:
        for s in p["children"]:
            for child in s["children"]:
                if child["tag"] == "mtu":
                    for t in child["children"]:
                        print("SKIPPING %s" % t)
                        #tokenlist.append(t)
                elif child["tag"] == "t":

                    #SSML
                    #If there are transcriptions (from marytts) that have no g2p_method, they came from ssml input and should not be overwritten! 
                    #if "g2p_method" in child and child["g2p_method"] in ["rules","lexicon"]:
                    if "g2p_method" in child:
                        tokenlist.append(child)
        

    #wordByWord or sentenceBySentence
    wordByWord = False

    if wordByWord:
        for t in tokenlist:
            #print(t)
            orth = t["#text"]
            #print(orth)
            ph = getLookup(lang, orth)
            if ph:
                #print(ph)
                t["@ph"] = ph
                #print(t)

    else:
        #get transcriptions for the entire sentence
        orthlist = []
        for t in tokenlist:
            orth = t["text"]
            orthlist.append(orth)

        responseDict = getLookupBySentence(lang, " ".join(orthlist))
        if responseDict:

            for t in tokenlist:
                orth = t["text"]

                if orth.lower() in responseDict:
                    ph = responseDict[orth.lower()]
                    #print(ph)
                    t["ph"] = ph
                    #print(t)
                else:
                    print("No trans for %s" % orth)


    return utt


def getLookupBySentence(lang,orth):
    if lang in ["sv"]:
        #wikimedia/code
        #sbt
        #~re-start

        #now:
        #~/go/src/github.com/stts-se/pronlex/lexserver$ go run lexserver.go 

        #localhost:8181/llookup/
        #url = "http://localhost:8181/llookup/%s" % orth.lower()
        #url = "http://localhost:8787/lexlookup?lexicons=sv.se.nst&words=%s" % orth.lower()
        url = "http://localhost:8787/lexicon/lookup?lexicons=sv-se.nst&words=%s" % orth.lower()
        r = requests.get(url)
        print(r.url)
        response = r.text

        if response == "null":
            return {}

        print("RESPONSE: %s" % response)

        try:
            response_json = json.loads(response)
            trans_dict = {}
            
            #with straight list response:
            if type(response_json) == type([]):
                for response_item in response_json:
                    print("STATUS: %s" % response_item["status"]["name"])
                    if not response_item["status"]["name"] == "delete":
                        response_orth = response_item["strn"]
                        first_trans = response_item["transcriptions"][0]["strn"]
                        if response_item["preferred"] == True:
                            print("ORTH: %s, PREFERRED TRANS: %s" % (response_orth,first_trans))
                            trans_dict[response_orth] = first_trans
                        else:
                            #only add the first reading if none is preferred
                            if not response_orth in trans_dict:
                                print("ORTH: %s, FIRST TRANS: %s" % (response_orth,first_trans))
                                trans_dict[response_orth] = first_trans

            else:
                #with dictionary response:
                for response_orth in response_json:
                    response_item = response_json[response_orth]
                    if not response_item["status"]["name"] == "delete":
                        first_trans = response_item[0]["transcriptions"][0]["strn"]
                        print("ORTH: %s, TRANS: %s" % (response_orth,first_trans))
                        if response_item["preferred"] == True:
                            trans_dict[response_orth] = first_trans
                        else:
                            #only add the first reading if none is preferred
                            if not response_orth in trans_dict:
                                trans_dict[response_orth] = first_trans

            return trans_dict
        except:
            e = sys.exc_info()[0]
            print("NO MATCH (%s): %s" % (e,response))
            raise
    
    if orth == "test":
        return "' t I s t"

    return None


def mapperMapToMary(trans):
    url = "http://localhost:8787/mapper/map?from=sv-se_ws-sampa&to=sv-se_sampa_mary&trans=%s" % quote_plus(trans)

    r = requests.get(url)
    print(r.url)
    response = r.text
    print("RESPONSE: %s" % response)
    try:
        response_json = json.loads(response)
        print("RESPONSE_JSON: %s" % response_json)
        new_trans = response_json["Result"]
        print("NEW TRANS: %s" % new_trans)
        return new_trans
    except:
        e = sys.exc_info()[0]
        print("ERROR: unable to get mapper result (%s). Response was: %s" % (e, response))
        return None
        
def localMapToMary(first_trans):
    # " -> ', "" -> ", . -> -
    #mary_fmt = first_trans.replace('""',"#")
    #mary_fmt = mary_fmt.replace('"',"'")
    #mary_fmt = mary_fmt.replace('#',"\"")
    #with llookup
    #mary_fmt = mary_fmt.replace('.',"-")
    
    #with lexlookup
    #mary_fmt = mary_fmt.replace('$',"-")
    
    new_trans_list = []
    if " " in first_trans:
        for symbol in first_trans.split(" "):
            new_trans_list.append(trans2maryttsMap[symbol])
            
    else:
        #read first two characters, see if they match key, otherwise see if first char matches key otherwise error
        rest = first_trans
        while rest != "":
            print(rest)
            #print(rest[:2])
            if rest[:2] in trans2maryttsMap:
                print("Found %s, mapping to %s" % (rest[:2], trans2maryttsMap[rest[:2]]))
                new_trans_list.append(trans2maryttsMap[rest[:2]])
                if len(rest) > 2:
                    rest = rest[2:]
                else:
                    rest = ""
            elif rest[0] in trans2maryttsMap:
                print("Found %s, mapping to %s" % (rest[0], trans2maryttsMap[rest[0]]))
                new_trans_list.append(trans2maryttsMap[rest[0]])
                if len(rest) > 1:
                    rest = rest[1:]
                else:
                    rest = ""
            else:
                print("ERROR: %s not in trans2maryttsMap" % rest)
                #After this error, skip one character and try again.
                #Or better to raise error?
                rest = rest[1:]


    mary_fmt = " ".join(new_trans_list)
    return mary_fmt



trans2maryttsMap = {
    "i:": "i:", 
    "I": "I", 
    "u0": "u0", 
    "}:": "}:", 
    "a": "a", 
    "A:": "A:", 
    "u:": "u:", 
    "U": "U", 
    "E:": "E:", 
    "E": "E", 
    "au": "a*U", 
    "y:": "y:", 
    "Y": "Y", 
    "e:": "e:", 
    "e": "e", 
    "2:": "2:", 
    "9": "9", 
    "o:": "o:", 
    "O": "O", 
    "@": "e", 
    "eu": "E*U", 
    "p": "p", 
    "b": "b", 
    "t": "t", 
    "rt": "rt", 
    "t`": "rt", 
    "m": "m", 
    "n": "n", 
    "d": "d", 
    "rd": "rd", 
    "d`": "rd", 
    "k": "k", 
    "g": "g", 
    "N": "N", 
    "rn": "rn", 
    "n`": "rn", 
    "f": "f", 
    "v": "v", 
    "C": "C", 
    "rs": "rs", 
    "s`": "rs", 
    "r": "r", 
    "l": "l", 
    "s": "s", 
    # ??????????????????
    "s'": "C", 
    #Which of these is correct?
    "x": "S", 
    "x\\": "S", 
    "h": "h", 
    "rl": "rl", 
    "l`": "rl", 
    "j": "j", 
    ".": "-", 
    "$": "-", 
    '"': "'", 
    '""': '"', 
    "%": "%", 
    " ": " "
};



def getLookup(lang,orth):
    if lang in ["sv"]:
        #wikimedia/code
        #sbt
        #~re-start
        #localhost:8181/llookup/
        #url = "http://localhost:8181/llookup/%s" % orth.lower()
        url = "http://localhost:8787/lexlookup?lexicons=sv.se.nst&words=%s" % orth.lower()
        r = requests.get(url)
        print(r.url)
        response = r.text
        print("RESPONSE: %s" % response)

        try:
            response_json = json.loads(response)
            first_trans = response_json[0]["transcriptions"][0]["strn"]
            print(first_trans)

            # " -> ', "" -> ", . -> -

            mary_fmt = first_trans.replace('""',"#")
            mary_fmt = mary_fmt.replace('"',"'")
            mary_fmt = mary_fmt.replace('#',"\"")
            mary_fmt = mary_fmt.replace('.',"-")
            print(mary_fmt)
            return mary_fmt
        except:
            print("NO MATCH: "+response)
    
    if orth == "test":
        return "' t I s t"

    return None
