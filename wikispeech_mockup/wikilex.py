import sys, requests, json, re

try:
    #Python 3
    from urllib.parse import quote_plus
except:
    #Python 2
    from urllib import quote_plus
    
import wikispeech_mockup.config as config
import wikispeech_mockup.log as log
host = config.config.get("Services","lexicon")



def lexLookup(utt, lang, component_config):
    log.debug("lexLookup: %s" % utt)

    tokenlist = []

    for p in utt["paragraphs"]:
        for s in p["sentences"]:
            for phr in s["phrases"]:
                for token in phr["tokens"]:
                    if "mtu" in token and token["mtu"] == True:
                        for word in token["words"]:
                            log.debug("SKIPPING %s" % word)
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
            if lang == "ar":
                orth = re.sub("\u064F","",orth)

            orthlist.append(orth)

        responseDict = getLookupBySentence(" ".join(orthlist), component_config["lexicon"])
        if responseDict:

            for t in tokenlist:
                orth = t["orth"]
                if lang == "ar":
                    orth = re.sub("\u064F","",orth)

                if orth.lower() in responseDict:
                    ph = responseDict[orth.lower()]
                    #if lang == "ar":
                    #    ph = re.sub("'","&apos;",ph)
                    #log.debug(ph)
                    t["trans"] = ph
                    t["g2p_method"] = "lexicon"
                    #log.debug(t)
                else:
                    log.debug("No trans for %s" % orth)


    return utt





def getLookupBySentence(orth, lexicon):

    url = "%s/lexicon/lookup?lexicons=%s&words=%s" % (host, lexicon, orth.lower())
    r = requests.get(url)
    log.debug(r.url)
    response = r.text

    if response == "null":
        return {}

    log.debug("RESPONSE: %s" % response)

    try:
        response_json = json.loads(response)
        trans_dict = {}
            
        #with straight list response:
        if type(response_json) == type([]):
            for response_item in response_json:
                log.debug("STATUS: %s" % response_item["status"]["name"])
                if not response_item["status"]["name"] == "delete":
                    response_orth = response_item["strn"]
                    first_trans = response_item["transcriptions"][0]["strn"]
                    if response_item["preferred"] == True:
                        log.debug("ORTH: %s, PREFERRED TRANS: %s" % (response_orth,first_trans))
                        trans_dict[response_orth] = first_trans
                    else:
                        #only add the first reading if none is preferred
                        if not response_orth in trans_dict:
                            log.debug("ORTH: %s, FIRST TRANS: %s" % (response_orth,first_trans))
                            trans_dict[response_orth] = first_trans

        else:
            #with dictionary response:
            for response_orth in response_json:
                response_item = response_json[response_orth]
                if not response_item["status"]["name"] == "delete":
                    first_trans = response_item[0]["transcriptions"][0]["strn"]
                    log.debug("ORTH: %s, TRANS: %s" % (response_orth,first_trans))
                    if response_item["preferred"] == True:
                        trans_dict[response_orth] = first_trans
                    else:
                        #only add the first reading if none is preferred
                        if not response_orth in trans_dict:
                            trans_dict[response_orth] = first_trans

        return trans_dict
    except:
        e = sys.exc_info()[0]
        error("NO MATCH (%s): %s" % (e,response))
        raise
    


