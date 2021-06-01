import requests, re
import simplejson as json
import wikispeech_server.config as config
import wikispeech_server.log as log
import urllib.parse


#HB 191125
#Testing to include part-of-speech tags from lexicon instead of from textprocessing
#If there is a real pos tagger at work this should change.
#Also if pos tag is set by user
includePostag = True


def cleanupOrth(orth):

    orig = orth

    if orth == None:
        orth = ""
        return orth
    
    #Remove soft hyphen if it occurs - it's a hidden character that causes problems in lookup
    orth = orth.replace("\xad","")

    #Remove Arabic diacritics if they occur
    #Bad place for this but where else? In mapper?
    FATHATAN         = '\u064b' 
    DAMMATAN         = '\u064c' 
    KASRATAN         = '\u064d' 
    FATHA            = '\u064e' 
    DAMMA            = '\u064f' 
    KASRA            = '\u0650' 
    SHADDA           = '\u0651' 
    SUKUN            = '\u0652' 

    TASHKEEL  = (FATHATAN,DAMMATAN,KASRATAN,FATHA,DAMMA,KASRA,SUKUN,SHADDA)

    orth = re.sub("("+"|".join(TASHKEEL)+")","", orth)

    
    orth = orth.lower()

    log.debug("lexicon_client.cleanupOrth: %s -> %s" % (orig, orth))

    return orth
    
lexica = []
def loadLexicon(lexicon_name):
    try:
        lexicon = getLexiconByName(lexicon_name)
    except ValueError:
        lexicon = Lexicon(lexicon_name)
        lexica.append(lexicon)
    return lexicon


def lexLookup(utt, lang, componentConfig):
    lexicon_name = componentConfig["lexicon"]

    #TODO Load lexicon here, before we have an external call to loadLexicon
    loadLexicon(lexicon_name)
        
    tokens = getTokens(utt)
    orthstring = getOrth(tokens)
    log.debug("ORTH TO LOOKUP: %s" % orthstring)
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
                            #log.debug("SKIPPING %s" % word)
                            if "g2p_method" in word:
                                tokenlist.append(word)
                    else:

                        for word in token["words"]:
                            #Only append to tokenlist if word doesn't have 'input_ssml_transcription' attribute
                            if "input_ssml_transcription" not in word:
                                tokenlist.append(word)
                                log.debug("Appending to tokenlist: %s" % word)
    return tokenlist


def getOrth(tokenlist):
    orthlist = []
    for t in tokenlist:
        orth = t["orth"]
        orth = cleanupOrth(orth)
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
    raise ValueError("Lexicon %s not loaded\nLoaded lexica: %s" % (lexicon_name, lexica))


def convertResponse(response_json):
    trans_dict = {}

    if includePostag:
        trans_dict["postags"] = {}

    
    #with list response:
    if type(response_json) == type([]):
        for response_item in response_json:
            log.debug("STATUS: %s" % response_item["status"]["name"])
            if not response_item["status"]["name"] == "delete":
                response_orth = response_item["strn"]
                first_trans = response_item["transcriptions"][0]["strn"]
                pos = ""
                if includePostag and "partOfSpeech" in response_item:
                    pos = response_item["partOfSpeech"]
                if "preferred" in response_item and response_item["preferred"] == True:
                    log.debug("ORTH: %s, PREFERRED TRANS: %s" % (response_orth,first_trans))
                    trans_dict[response_orth] = first_trans
                    if includePostag:
                        trans_dict["postags"][response_orth] = pos
                else:
                    #only add the first reading if none is preferred
                    if not response_orth in trans_dict:
                        log.debug("ORTH: %s, FIRST TRANS: %s" % (response_orth,first_trans))
                        trans_dict[response_orth] = first_trans
                        if includePostag:
                            trans_dict["postags"][response_orth] = pos

    return trans_dict


def addTransFromResponse(tokenlist, responseDict):
    for t in tokenlist:
        orth = t["orth"]
        orth = cleanupOrth(orth)
        if orth in responseDict:
            ph = responseDict[orth]
            t["trans"] = ph
            t["g2p_method"] = "lexicon"
            if includePostag:
                t["pos"] = responseDict["postags"][orth]
        else:
            log.debug("No trans for %s" % orth)
    

class LexiconException(Exception):
    pass

class Lexicon(object):
    
    def __init__(self, lexicon_name, run_test=True):
        self.lexicon_name = lexicon_name
        
        self.base_url = "%s/lexicon" % config.config.get("Services", "lexicon")

        if run_test:
            self.test()


    def test(self):
        url = "%s/list" % self.base_url
        log.debug("LEXICON URL: %s" % url)
        #print("LEXICON URL: %s" % url)
        try:
            r = requests.get(url)
            response = r.text
            if r.status_code != 200:
                msg = "Unable to createlexicon client for %s at url %s. Response status_code: %s, Response string: %s" % (self.lexicon_name, self.base_url, r.status_code, response)
                log.error(msg)
                raise LexiconException(msg)
                
            response_json = json.loads(response)
            #print(response_json)
            exists = False
            #print(response_json)
            for lex in response_json:
                if lex['name'] == self.lexicon_name:
                    exists = True
            if not exists:
                msg = "Lexicon does not exist: %s" % (self.lexicon_name)
                log.error(msg)
                raise LexiconException(msg)
                
        except json.JSONDecodeError:
            msg = "Unable to create lexicon client for %s at url %s. Response was: %s" % (self.lexicon_name, self.base_url, response)
            log.error(msg)
            raise LexiconException(msg)
        except Exception as e:
            msg = "Unable to create lexicon client for %s at url %s. Reason: %s" % (self.lexicon_name, self.base_url, e)
            log.warning(msg)
            raise LexiconException(msg)



    def lookup(self, string):

        if string.strip() == "":
            log.warning("LEXICON LOOKUP STRING IS EMPTY!")
            return {}


        encString = urllib.parse.quote(string)
        url = "%s/%s?lexicons=%s&words=%s" % (self.base_url, "lookup", self.lexicon_name, encString)
        r = requests.get(url)
        log.debug("LEXICON LOOKUP URL: %s" % r.url)
        response = r.text
        try:
            response_json = json.loads(response)
            log.debug(response_json)
            return response_json
        except:
            log.error("unable to lookup '%s' in %s. response was %s" % (string, self.lexicon_name, response))
            raise LexiconException(response)
        
       


        
