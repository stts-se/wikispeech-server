import requests, json

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
        url = "http://localhost:8787/lexlookup?lexicons=sv.se.nst&words=%s" % orth.lower()
        r = requests.get(url)
        print(r.url)
        response = r.text
        print("RESPONSE: %s" % response)

        try:
            response_json = json.loads(response)
            mary_fmt_dict = {}

            #with straight list response:
            if type(response_json) == type([]):
                for response_item in response_json:
                    response_orth = response_item["strn"]
                    first_trans = response_item["transcriptions"][0]["strn"]
            else:
                #with dictionary response:
                for response_orth in response_json:
                    response_item = response_json[response_orth]
                    first_trans = response_item[0]["transcriptions"][0]["strn"]


            print(first_trans)

            # " -> ', "" -> ", . -> -
            #mary_fmt = first_trans.replace('""',"#")
            #mary_fmt = mary_fmt.replace('"',"'")
            #mary_fmt = mary_fmt.replace('#',"\"")
            #with llookup
            #mary_fmt = mary_fmt.replace('.',"-")
            
            #with lexlookup
            #mary_fmt = mary_fmt.replace('$',"-")
            
            if " " in first_trans:
                new_trans_list = []
                for symbol in first_trans.split(" "):
                    new_trans_list.append(trans2maryttsMap[symbol])
                    mary_fmt = " ".join(new_trans_list)
                    
            else:
                #read first two characters, see if they match key, otherwise see if first char matches key otherwise error
                rest = first_trans
                new_trans_list = []
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
                mary_fmt = " ".join(new_trans_list)
                    


                print("%s: %s -> %s" % (response_orth, first_trans, mary_fmt))
                mary_fmt_dict[response_orth] = mary_fmt

            return mary_fmt_dict
        except:
            print("NO MATCH: "+response)
    
    if orth == "test":
        return "' t I s t"

    return None


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
    "2:": "9:", 
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
    "x": "S", 
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