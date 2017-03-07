import os, re


def synthesise(lang, voice, input, presynth=False):
    mbrola_voice = voice["espeak_mbrola_voice"]
    voice = voice["espeak_voice"]
    #convert utt to ssml
    ssml = utt2phonemics(input)
    #ssml = utt2ssml(input)
    print(ssml)

    ssml = ssml.replace('"','\\"')

    #send ssml to espeak and print pho file
    outfile = "tmp/espeak_out"
    cmd = u"espeak -v %s --pho \"%s\" > %s.pho" % (mbrola_voice, ssml, outfile)
    print(cmd)
    os.system(cmd)

    #send ssml to espeak and generate wav file (should be possible to do both things at once but apparently not?)
    outfile = "tmp/espeak_out"
    cmd = u"espeak -v %s \"%s\" -w %s.wav" % (voice, ssml, outfile)
    print(cmd)
    os.system(cmd)



    #read pho file


    #TODO this doesn't work..
    #BETTER: read the pho into list of durations, then loop over words in input, add durations for each word

    infh = open(outfile+".pho")
    segments = infh.readlines()
    infh.close()
    prevword = None
    prevwordend = 0
    words = []
    addtime = 0
    for segment in segments:
        segment = segment.strip()
        if segment == "":
            words.append((prevword, str(float(prevwordend)+addtime) ))
            next
        print(segment)
        m = re.search("^(\S+)\t([0-9]+)", segment)
        symbol = m.group(1)
        duration = float(m.group(2))
        if prevword == "0":
            prevword = "sil"

        endtime = prevwordend+duration
       
        #print("prevwordend: %f" % float(prevwordend))
        #print("endtime: %f" % float(endtime))


        #if prevword and prevword != "sil" and word != prevword:
        #if prevword and word != prevword:
        #    words.append((prevword, str(float(prevwordend)+addtime) ))


        if float(endtime) < float(prevwordend):            
            addtime += float(prevwordend)
            print("New addtime: %f" % addtime)



        #prevword = word
        prevwordend = endtime

    #last word
    if prevword == "0":
        prevword = "sil"
    #if prevword and prevword != "sil" and word != prevword:
    #if prevword and word != prevword:
    #    words.append((prevword, str(float(prevwordend)+addtime) ))

    audio_url = "http://localhost/wikispeech_mockup/%s.wav" % outfile


    #return audio_url and tokens
    return (audio_url, words)

def utt2ssml(item):
    print(item)
    if item["tag"] == "t":
        word = item["text"]
        if "ph" in item:
            phns = map2espeak(item["ph"])
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

def utt2phonemicsOLD(item):
    print("utt2phonemics: %s" % item)
    if item["tag"] == "t":
        word = item["text"]
        if "ph" in item:
            phns = map2espeak(item["ph"])
            phonemics = "[[%s]]" % phns.replace(" ","")
            #ssml = """<phoneme ph="%s">%s</phoneme>""" % (phns, word)
        else:
            phonemics = word
            #ssml = word
    elif item["tag"] == "boundary":
        phonemics = ","
        #ssml = "<break/>"
    else:
        phn_list = []
        for child in item["children"]:
            phn_list.append(utt2phonemics(child))
        phonemics = " ".join(phn_list)
    return phonemics

def utt2phonemics(utterance):
    phn_list = []
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
                        if "trans" in word:
                            ws_trans = word["trans"]
                            print("WS_TRANS: %s" % ws_trans)
                            espeak_trans = map2espeak(ws_trans)
                            print("ESPEAK_TRANS: %s" % espeak_trans)
                            phn_list.append(espeak_trans)
    phonemics = "[["+" ".join(phn_list)+"]]"
    return phonemics

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

espeakmap = {
    "@U":"oU",

    "{:":"E",
    "{":"E"
}

def map2espeak(phonestring):
    #h @ - ' l @U
    #hh ax l ow1
    phonestring = re.sub(" - "," ", phonestring)
    #phonestring = re.sub("' ","1 ", phonestring)
    phones = phonestring.split(" ")
    espeakphones = []
    for phone in phones:
        if phone in espeakmap:
            espeakphone = espeakmap[phone]
        else:
            espeakphone = phone
        espeakphones.append(espeakphone)
    espeak = " ".join(espeakphones)
    #move accents to following vowel
    espeak = re.sub(r"' (.+)(@|oU|e|E)", r"\1 ' \2", espeak)
    espeak = re.sub(r"\" (.+)(@|oU|e|E)", r"\1 ' \2", espeak)

    print("MAPPED %s TO %s" % (phonestring, espeak))


    return espeak

if __name__ == "__main__":
    input = {"children": [{"children": [{"children": [{"children": [{"accent": "!H*", "children": [{"children": [{"p": "h", "tag": "ph"}, {"p": "@", "tag": "ph"}], "ph": "h @", "tag": "syllable"}, {"accent": "!H*", "children": [{"p": "l", "tag": "ph"}, {"p": "@U", "tag": "ph"}], "ph": "l @U", "stress": "1", "tag": "syllable"}], "g2p_method": "lexicon", "ph": "h @ - ' l @U", "pos": "UH", "tag": "t", "text": "hello"}, {"pos": ".", "tag": "t", "text": ","}, {"children": [{"children": [{"p": "h", "tag": "ph"}, {"p": "@", "tag": "ph"}], "ph": "h @", "tag": "syllable"}, {"children": [{"p": "l", "tag": "ph"}, {"p": "@U", "tag": "ph"}], "ph": "l @U", "stress": "1", "tag": "syllable"}], "g2p_method": "lexicon", "ph": "h @ - ' l @U", "pos": ",", "tag": "t", "text": "hello"}, {"pos": ".", "tag": "t", "text": "."}, {"breakindex": "5", "tag": "boundary", "tone": "L-L%"}], "tag": "phrase"}], "tag": "s"}], "tag": "p"}], "tag": "utt"}


    lang = "en"
    voice = {"espeak_voice":"mb-en1"}

    (audio_url, tokens) = synthesise(lang, voice, input)
    print(audio_url)


    pho = """

h	86
e	33	 0 117 80 109 100 109
j	65
s	100
a	33	 0 110 80 106 100 106
n	120	100 98

_	158
_	1
h	86
e	48	 0 105 80 81 100 81
j	65
s	100
a	33	 0 84 80 78 100 78
n	120	100 73

_	301
_	1
"""
