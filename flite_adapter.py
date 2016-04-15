import os, re


def synthesise(lang, voice, input):
    voice = voice["flite_voice"]
    #convert utt to ssml
    ssml = utt2ssml(input)
    print ssml

    #send ssml to flite
    outfile = "tmp/flite_out"
    cmd = u"../flite/flite -voice %s -psdur -ssml -t '%s' -o %s.wav > %s.timing" % (voice, ssml, outfile, outfile)
    print cmd
    os.system(cmd)



    #read psdur file

    infh = open(outfile+".timing")
    segments = infh.read().strip().split(" ")
    infh.close()
    prevword = None
    prevwordend = "0"
    words = []
    addtime = 0
    for segment in segments:
        #print segment
        (symbol,endtime,word) = segment.split("|")
        if prevword == "0":
            prevword = "sil"

       
        #print("prevwordend: %f" % float(prevwordend))
        #print("endtime: %f" % float(endtime))


        #if prevword and prevword != "sil" and word != prevword:
        if prevword and word != prevword:
            words.append((prevword, str(float(prevwordend)+addtime) ))


        if float(endtime) < float(prevwordend):            
            addtime += float(prevwordend)
            print("New addtime: %f" % addtime)



        prevword = word
        prevwordend = endtime

    #last word
    if prevword == "0":
        prevword = "sil"
    #if prevword and prevword != "sil" and word != prevword:
    if prevword and word != prevword:
        words.append((prevword, str(float(prevwordend)+addtime) ))

    audio_url = "http://localhost/wikispeech_mockup/%s.wav" % outfile


    #return audio_url and tokens
    return (audio_url, words)

def utt2ssml(item):
    print item
    if item["tag"] == "t":
        word = item["text"]
        if item.has_key("ph"):
            phns = map2flite(item["ph"])
            ssml = """<phoneme ph="%s">%s</phoneme>""" % (phns, word)
        else:
            ssml = word
    elif item["tag"] == "boundary":
        ssml = "<break/>"
    else:
        ssml_list = []
        for child in item["children"]:
            ssml_list.append(utt2ssml(child))
        ssml = " ".join(ssml_list)
    return ssml

#mary2flite
flitemap = {}
flitemap["A"] = "aa"
flitemap["{"] = "ae"
flitemap["V"] = "ah"
flitemap["O"] = "ao"
flitemap["O"] = "aw"
flitemap["@"] = "ax"
flitemap["r="] = "axr"
flitemap["AI"] = "ay"
flitemap["b"] = "b"
flitemap["tS"] = "ch"
flitemap["d"] = "d"
flitemap["D"] = "dh"
flitemap["d"] = "dx"
flitemap["E"] = "eh"
flitemap["XX"] = "el"
flitemap["XX"] = "em"
flitemap["XX"] = "en"
flitemap["XX"] = "er"
flitemap["EI"] = "ey"
flitemap["f"] = "f"
flitemap["g"] = "g"
flitemap["h"] = "hh"
flitemap["XX"] = "hv"
flitemap["I"] = "ih"
flitemap["i"] = "iy"
flitemap["dZ"] = "jh"
flitemap["k"] = "k"
flitemap["l"] = "l"
flitemap["m"] = "m"
flitemap["n"] = "n"
flitemap["XX"] = "nx"
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
flitemap["XX"] = "pau"
flitemap["XX"] = "h#"
flitemap["XX"] = "brth"


def map2flite(phonestring):
    #h @ - ' l @U
    #hh ax l ow1
    phonestring = re.sub(" - "," ", phonestring)
    phonestring = re.sub("' ","1 ", phonestring)
    phones = phonestring.split(" ")
    flitephones = []
    for phone in phones:
        if flitemap.has_key(phone):
            flitephone = flitemap[phone]
        else:
            flitephone = phone
        flitephones.append(flitephone)
    flite = " ".join(flitephones)
    #move accents to following vowel
    flite = re.sub(r"1 (.+)(aa|ae|ah|ao|aw|ax|axr|ay|eh|ih|iy|ow|oy|uh|uw)", r"\1\2 1", flite)
    flite = re.sub(" 1", "1", flite)

    print "MAPPED %s TO %s" % (phonestring, flite)


    return flite

if __name__ == "__main__":
    input = {"children": [{"children": [{"children": [{"children": [{"accent": "!H*", "children": [{"children": [{"p": "h", "tag": "ph"}, {"p": "@", "tag": "ph"}], "ph": "h @", "tag": "syllable"}, {"accent": "!H*", "children": [{"p": "l", "tag": "ph"}, {"p": "@U", "tag": "ph"}], "ph": "l @U", "stress": "1", "tag": "syllable"}], "g2p_method": "lexicon", "ph": "h @ - ' l @U", "pos": "UH", "tag": "t", "text": "hello"}, {"pos": ".", "tag": "t", "text": ","}, {"children": [{"children": [{"p": "h", "tag": "ph"}, {"p": "@", "tag": "ph"}], "ph": "h @", "tag": "syllable"}, {"children": [{"p": "l", "tag": "ph"}, {"p": "@U", "tag": "ph"}], "ph": "l @U", "stress": "1", "tag": "syllable"}], "g2p_method": "lexicon", "ph": "h @ - ' l @U", "pos": ",", "tag": "t", "text": "hello"}, {"pos": ".", "tag": "t", "text": "."}, {"breakindex": "5", "tag": "boundary", "tone": "L-L%"}], "tag": "phrase"}], "tag": "s"}], "tag": "p"}], "tag": "utt"}


    lang = "en"
    voice = "slt"

    (audio_url, tokens) = synthesise(lang, voice, input)
    print audio_url
