import requests, re
import simplejson as json
import wikispeech_mockup.config as config
import wikispeech_mockup.log as log

lexica = []

def loadLexicon(lexicon_name):
    lexicon = Lexicon(lexicon_name)
    lexica.append(lexicon)
    return lexicon

#legacy call (from wikilex)
def lexLookup(utt, lang, componentConfig):
    lexicon_name = componentConfig["lexicon"]

    #TODO Load lexicon here, before we have an external call to loadLexicon
    try:
        getLexiconByName(lexicon_name)
    except ValueError:
        loadLexicon(lexicon_name)
        
    tokens = getTokens(utt)
    orthstring = getOrth(tokens)
    responseDict = getLookupBySentence(orthstring, lexicon_name)
    addTransFromResponse(tokens, responseDict)
    return utt

def getTokens(utt):
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
                        #TODO this should be handled in a more general way
                        #'input_transcription' or something
                        for word in token["words"]:
                            if "g2p_method" in word:
                                tokenlist.append(word)
    return tokenlist


def getOrth(tokenlist):
    orthlist = []
    for t in tokenlist:
        orth = t["orth"]
        orthlist.append(orth)
    return " ".join(orthlist)


def getLookupBySentence(orth, lexicon_name):
    lexicon = getLexiconByName(lexicon_name)
    response = lexicon.lookup(orth)
    responseDict = convertResponse(response)
    return responseDict

def getLexiconByName(lexicon_name):
    for lexicon in lexica:
        if lexicon.lexicon_name == lexicon_name:
            return lexicon
    raise ValueError("Lexicon %s not loaded" % lexicon_name)


def convertResponse(response_json):
    trans_dict = {}
    #with list response:
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
    return trans_dict


def addTransFromResponse(tokenlist, responseDict):
    for t in tokenlist:
        orth = t["orth"]
        if orth.lower() in responseDict:
            ph = responseDict[orth.lower()]
            t["trans"] = ph
            t["g2p_method"] = "lexicon"
        else:
            log.debug("No trans for %s" % orth)
    

class LexiconException(Exception):
    pass

class Lexicon(object):
    
    def __init__(self, lexicon_name):
        self.lexicon_name = lexicon_name
        
        self.base_url = "%s/lexicon" % config.config.get("Services", "lexicon")

        self.test()


    def test(self):
        url = "%s/%s?lexicons=%s" % (self.base_url, "lookup", self.lexicon_name)
        log.debug(url)
        try:
            r = requests.get(url)
            response = r.text
            response_json = json.loads(response)
        except json.JSONDecodeError:
            msg = "Unable to create lexicon client for %s. Response was: %s" % (self.lexicon_name, response)
            log.error(msg)
            raise LexiconException(msg)
        except Exception as e:
            msg = "Unable to create lexicon client for %s at url %s. Reason: %s" % (self.lexicon_name, url, e)
            log.error(msg)
            raise LexiconException(msg)



    def lookup(self, string):
        
        url = "%s/%s?lexicons=%s&words=%s" % (self.base_url, "lookup", self.lexicon_name, string)
        r = requests.get(url)
        log.debug(r.url)
        response = r.text
        try:
            response_json = json.loads(response)
            log.debug(response_json)
            return response_json
        except:
            log.error("unable to lookup '%s' in %s. response was %s" % (string, self.lexicon_name, response))
            raise LexiconException(response)
        
       


        
