import os, re
import wikispeech_server.log as log
import wikispeech_server.config as config

def preproc(utt):
    #Nothing to be done here .. Maybe there will be?
    return utt

def synthesise(lang, voice, input, presynth=False, hostname="http:localhost:10000"):
    voice = voice["flite_voice"]
    #convert utt to ssml
    ssml = utt2ssml(input)
    log.debug(ssml)

    #send ssml to flite
    tmpdir = config.config.get("Audio settings","audio_tmpdir")
    wavfile_name = "flite_out.wav"
    timingfile_name = "flite_out.timing"
    #outfile = "%s/flite_out" % tmpdir
    cmd = u"./engines/flite -voice %s -psdur -ssml -t '%s' -o %s/%s > %s/%s" % (voice, ssml, tmpdir, wavfile_name, tmpdir, timingfile_name)
    log.debug(cmd)
    os.system(cmd)



    #read psdur file

    infh = open(tmpdir+"/"+timingfile_name)
    segments = infh.read().strip().split(" ")
    infh.close()
    prevword = None
    prevwordend = "0"
    words = []
    addtime = 0
    for segment in segments:
        log.debug(segment)
        (symbol,endtime,word) = segment.split("|")
        if prevword == "0":
            prevword = "sil"

       
        #log.debug("prevwordend: %f" % float(prevwordend))
        #log.debug("endtime: %f" % float(endtime))

        #TODO From the timing file we can't tell if a word is repeated
        #Try to find another way!
        #EXAMPLE:
        #pau|0.164|0
        #hh|0.233|hello
        #ax|0.282|hello
        #l|0.390|hello
        #ow|0.515|hello
        #hh|0.556|hello
        #ax|0.596|hello
        #l|0.708|hello
        #ow|0.934|hello
        #pau|1.199|0

        if prevword and prevword != "sil" and word != prevword:
            words.append({"orth":prevword, "endtime":str(float(prevwordend)+addtime)} )


        if float(endtime) < float(prevwordend):            
            addtime += float(prevwordend)
            log.debug("New addtime: %f" % addtime)



        prevword = word
        prevwordend = endtime

    #last word
    if prevword == "0":
        prevword = "sil"
    if prevword and prevword != "sil" and word != prevword:
        words.append({"orth":prevword, "endtime":str(float(prevwordend)+addtime)} )

    audio_url = "%s%s/%s" % (hostname, "audio", wavfile_name)
    log.debug("flite_adapter returning audio_url: %s" % audio_url) 

    #return audio_url and tokens
    return (audio_url, words)


def utt2ssml(utterance):
    log.debug(utterance)
    ssml_list = []
    paragraphs = utterance["paragraphs"]    
    for paragraph in paragraphs:
        sentences = paragraph["sentences"]
        for sentence in sentences:
            phrases = sentence["phrases"]
            for phrase in phrases:
                tokens = phrase["tokens"]
                for token in tokens:
                    words = token["words"]
                    for word in words:
                        orth = word["orth"]
                        if "trans" in word:
                            ws_trans = word["trans"]
                            log.debug("WS_TRANS: %s" % ws_trans)
                            flite_trans = map2flite(ws_trans)
                            log.debug("FLITE_TRANS: %s" % flite_trans)
                            ssml = """<phoneme ph="%s">%s</phoneme>""" % (flite_trans, orth)
                        else:
                            ssml = orth
                        ssml_list.append(ssml)
                if "boundary" in phrase:
                    ssml = "<break/>"
                    ssml_list.append(ssml)
    ssml = " ".join(ssml_list)
    return ssml


#mary2flite
flitemap = {}
flitemap["A"] = "aa"
flitemap["{"] = "ae"
flitemap["V"] = "ah"
flitemap["O"] = "ao"
#flitemap["O"] = "aw"
flitemap["@"] = "ax"
#flitemap["r="] = "axr"
flitemap["r="] = "er"
flitemap["AI"] = "ay"
flitemap["b"] = "b"
flitemap["tS"] = "ch"
flitemap["d"] = "d"
flitemap["D"] = "dh"
#flitemap["d"] = "dx"
flitemap["E"] = "eh"
#flitemap["XX"] = "el"
#flitemap["XX"] = "em"
#flitemap["XX"] = "en"
#flitemap["XX"] = "er"
flitemap["EI"] = "ey"
flitemap["f"] = "f"
flitemap["g"] = "g"
flitemap["h"] = "hh"
#flitemap["XX"] = "hv"
flitemap["I"] = "ih"
flitemap["i"] = "iy"
flitemap["dZ"] = "jh"
flitemap["k"] = "k"
flitemap["l"] = "l"
flitemap["m"] = "m"
flitemap["n"] = "n"
#flitemap["XX"] = "nx"
flitemap["N"] = "ng"
flitemap["@U"] = "ow"
flitemap["OI"] = "oy"
flitemap["p"] = "p"
flitemap["r"] = "r"
flitemap["s"] = "s"
flitemap["S"] = "sh"
flitemap["t"] = "t"
flitemap["T"] = "th"
flitemap["U"] = "uh"
flitemap["u"] = "uw"
flitemap["v"] = "v"
flitemap["w"] = "w"
flitemap["j"] = "y"
flitemap["z"] = "z"
flitemap["Z"] = "zh"
#flitemap["XX"] = "pau"
#flitemap["XX"] = "h#"
#flitemap["XX"] = "brth"


def map2flite(phonestring):
    #h @ - ' l @U
    #hh ax l ow1
    phonestring = re.sub("' ","1 ", phonestring)
    phones = phonestring.split(" ")
    flitephones = []
    for phone in phones:
        if phone in flitemap:
            flitephone = flitemap[phone]
        else:
            flitephone = phone
        flitephones.append(flitephone)
    flite = " ".join(flitephones)
    #move accents to following vowel
    flite = re.sub(r"1 ([^.]*)(aa|ae|ah|ao|aw|ax|axr|ay|eh|ey|ih|iy|ow|oy|uh|uw)", r"\1\2 1", flite)
    flite = re.sub(" 1", "1", flite)
    flite = re.sub(" \. "," ", flite)

    log.debug("MAPPED %s TO %s" % (phonestring, flite))


    return flite

if __name__ == "__main__":
    #input = {"children": [{"children": [{"children": [{"children": [{"accent": "!H*", "children": [{"children": [{"p": "h", "tag": "ph"}, {"p": "@", "tag": "ph"}], "ph": "h @", "tag": "syllable"}, {"accent": "!H*", "children": [{"p": "l", "tag": "ph"}, {"p": "@U", "tag": "ph"}], "ph": "l @U", "stress": "1", "tag": "syllable"}], "g2p_method": "lexicon", "ph": "h @ - ' l @U", "pos": "UH", "tag": "t", "text": "hello"}, {"pos": ".", "tag": "t", "text": ","}, {"children": [{"children": [{"p": "h", "tag": "ph"}, {"p": "@", "tag": "ph"}], "ph": "h @", "tag": "syllable"}, {"children": [{"p": "l", "tag": "ph"}, {"p": "@U", "tag": "ph"}], "ph": "l @U", "stress": "1", "tag": "syllable"}], "g2p_method": "lexicon", "ph": "h @ - ' l @U", "pos": ",", "tag": "t", "text": "hello"}, {"pos": ".", "tag": "t", "text": "."}, {"breakindex": "5", "tag": "boundary", "tone": "L-L%"}], "tag": "phrase"}], "tag": "s"}], "tag": "p"}], "tag": "utt"}


    input = {
        "lang": "en-US",
        "paragraphs": [
            {
                "sentences": [
                    {
                        "phrases": [
                            {
                                "boundary": {
                                    "breakindex": "5",
                                    "tone": "L-L%"
                                },
                                "tokens": [
                                    {
                                        "token_orth": "hello",
                                        "words": [
                                            {
                                                "accent": "!H*",
                                                "g2p_method": "lexicon",
                                                "orth": "hello",
                                                "pos": "UH",
                                                "trans": "h @ - ' l @U"
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }
    

    lang = "en"
    voice = {"flite_voice":"slt"}
    log.log_level = "debug"

    
    (audio_url, tokens) = synthesise(lang, voice, input)
    log.debug("AUDIO URL: %s" % audio_url)
    log.debug("TOKENS: %s" % tokens)
