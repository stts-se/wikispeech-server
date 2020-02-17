import sys, os, re
import time
import json, requests
import wikispeech_server.log as log


def transcribe(utt, lang, componentConfig):
    global conf
    conf = componentConfig

    print(conf)


    org_lang = lang
    if org_lang == "sv-en":
        lang = "sv"
    prev_word_lang = "sv"
    tokens = getTokens(utt)
    for token in tokens:
        word = token["orth"].lower()

        m = re.search("(.+)([,.?!:;]+)$", word)
        if m:
            word = m.group(1)
            punct = m.group(2)
        else:
            punct = None


        #if word == "sil":
        #    transcriptions.append("sil")
        #    continue

        if org_lang == "sv-en":
            svtrans = lookupWord(word, "sv")
            entrans = lookupWord(word, "en")
            if svtrans and entrans:
                if prev_word_lang == "sv":
                    trans = svtrans
                    source = "sv_lexicon"
                    lang = "sv"
                else:
                    trans = entrans
                    source = "en_lexicon"
                    lang = "en"
            elif svtrans:
                trans = svtrans
                source = "sv_lexicon"
                lang = "sv"
            elif entrans:
                trans = entrans
                source = "en_lexicon"
                lang = "en"
            else:
                trans = None
                

        else:
            trans = lookupWord(word, lang)
            source = "lexicon"

        if not trans and re.match("^[0-9]+$", word):
            word = rbnfCLI(word, lang)

        if not trans:
            trans = compound(word, lang)
            source = "compound"
        if not trans:
            trans = g2p(word, lang)
            trans = syllabify(trans, lang)
            source = "g2p"

        sys.stderr.write("%s\t%s\t%s\n" % (word, trans, source))

        mapped_trans = mapTrans(trans, lang)
        if org_lang == "sv-en" and lang == "en":
            mapped_trans = add_e_to_en_phones(mapped_trans)
            
        #transcriptions.append(mapped_trans)
        #transcriptions.append(trans)
        token["trans"] = mapped_trans
        prev_word_lang = lang

        #if punct:
        #    transcriptions.append("sil")

    #Final silence
    #if not punct:
    #    transcriptions.append("sil")
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


def transcribeText(text, lang):
    sys.stderr.write("transcribeText(%s, %s)\n" % (text,lang))
    org_lang = lang
    if org_lang == "sv-en":
        lang = "sv"
    prev_word_lang = "sv"
    
    transcriptions = []
    #Initial silence
    transcriptions.append("sil")


    for word in re.split("\s+", text):
        word = word.lower()

        m = re.search("(.+)([,.?!:;]+)$", word)
        if m:
            word = m.group(1)
            punct = m.group(2)
        else:
            punct = None


        if word == "sil":
            transcriptions.append("sil")
            continue

        if org_lang == "sv-en":
            svtrans = lookupWord(word, "sv")
            entrans = lookupWord(word, "en")
            if svtrans and entrans:
                if prev_word_lang == "sv":
                    trans = svtrans
                    source = "sv_lexicon"
                    lang = "sv"
                else:
                    trans = entrans
                    source = "en_lexicon"
                    lang = "en"
            elif svtrans:
                trans = svtrans
                source = "sv_lexicon"
                lang = "sv"
            elif entrans:
                trans = entrans
                source = "en_lexicon"
                lang = "en"
            else:
                trans = None
                

        else:
            trans = lookupWord(word, lang)
            source = "lexicon"

        if not trans and re.match("^[0-9]+$", word):
            word = rbnfCLI(word, lang)

        if not trans:
            trans = compound(word, lang)
            source = "compound"
        if not trans:
            trans = g2p(word, lang)
            trans = syllabify(trans, lang)
            source = "g2p"

        sys.stderr.write("%s\t%s\t%s\n" % (word, trans, source))

        mapped_trans = mapTrans(trans, lang)
        if org_lang == "sv-en" and lang == "en":
            mapped_trans = add_e_to_en_phones(mapped_trans)
            
        transcriptions.append(mapped_trans)
        #transcriptions.append(trans)
        prev_word_lang = lang

        if punct:
            transcriptions.append("sil")

    #Final silence
    if not punct:
        transcriptions.append("sil")
    return transcriptions

def rbnfCLI(word, lang):

    sys.stderr.write("rbnf: %s\n" % word)
    
    cmd = "~/git/rbnf/cmd/spellout/spellout -r spellout-numbering ~/git/rbnf/%s.xml %s 2> /dev/null > /tmp/rbnf.txt" % (lang, word)
    #sys.stderr.write(cmd+"\n")
    os.system(cmd)

    with open("/tmp/rbnf.txt", "r") as read_file:
        try:
            word = read_file.readlines()[0].strip().split("\t")[1]            
            #print(word)
            #The swedish rbnf has non-breaking hyphens (?)
            word = re.sub("­", "-", word)
            word = re.sub("\s+", "-", word)

            #Special case for Swedish rbnf
            word = re.sub("et-", "ett-", word)
           
            
            sys.stderr.write("rbnf: %s\n" % word)
            return word
        except:
            return "number"



    
def lookupWord(word, lang):
    #sys.stderr.write("lookupWord: %s\n" % word)

    
    #lexname = "sv_se_nst_lex:sv-se.nst"
    #lexname = "en_am_cmu_lex:en-us.cmu"

    #TODO
    #lexname = conf[lang]["lexicon"]
    lexname = conf["lexicon"]

    url = "http://localhost:8787/lexicon/lookup?lexicons=%s&words=%s" % (lexname, word)

    try:
        response = requests.get(url)
    except:
        cmd = "cd ../pronlex; nohup sh install/start_server.sh -a /media/bigdisk/wikispeech_appdir &"
        sys.stderr.write("%s\n" % cmd)
        os.system(cmd)
        while True:
            sys.stderr.write("Waiting for pronlex to start..\n")
            try:
                res = requests.get("http://localhost:8787/ping")
                sys.stderr.write("%s\n" % res.text)
                assert res.text == "pronlex"
                break
            except:
                time.sleep(1)
                pass
                
        return lookupWord(word)

    data = response.json()
    #First see if there is a preferred entry
    for entry in data:
        if entry["strn"] == word:
            if entry["preferred"] == True:
                trans = entry["transcriptions"][0]["strn"]
                return trans
    #Otherwise just pick one
    #reverse to pick the last :)
    data.reverse()
    for entry in data:
        if entry["strn"] == word:
            trans = entry["transcriptions"][0]["strn"]
            return trans
            
    return False


def compound(word, lang):
    #sys.stderr.write("compound: %s\n" % word)

    if not "-" in word:

        #TODO
        #decompname = conf[lang]["decompname"]
        decompname = conf["decompname"]

        url = "http://localhost:6778/decomp/%s/%s" % (decompname, word)

        try:
            response = requests.get(url)
        except:
            cmd = "cd ../decomp; nohup go run decompserver/decompserver.go decompserver/decomp_files/ &"
            sys.stderr.write("%s\n" % cmd)
            os.system(cmd)
            while True:
                sys.stderr.write("Waiting for decomp to start..\n")
                try:
                    res = requests.get("http://localhost:6778/ping")
                    sys.stderr.write("%s\n" % res.text.strip())
                    assert res.text.strip() == "decompserver"
                    break
                except:
                    time.sleep(1)
                    pass

            return compound(word, lang)



        data = response.json()
        if data == []:
            return False
        parts = data[0]["parts"]

    else:
        parts = word.split("-")
        
    trans = []
    for part in parts:
        parttrans = lookupWord(part, lang)
        if not parttrans:
            parttrans = g2p(part, lang)
        trans.append(parttrans)

    i = 0;
    while i < len(trans):
        trans[i] = re.sub("%", '', trans[i])
        if i > 0:
            trans[i] = re.sub("'", '%', trans[i])
        trans[i] = re.sub(" +", " ", trans[i])
        i += 1

                
    return " . ".join(trans)
            
                

def g2p(word, lang):
    if lang in conf and "g2p_type" in conf[lang] and conf[lang]["g2p_type"] == "http_phonetiser":
        return http_phonetiser(word, lang)
    else:
        return rbg2p(word, lang)
        
def http_phonetiser(word, lang):
    #sys.stderr.write("http_phonetiser: %s\n" % word)

    g2pname = "sws"
    #g2pname = conf[lang]["g2p_name"]

    url = "http://localhost:5000/%s/%s/%s" % (g2pname, g2pname, word)

    try:
        response = requests.get(url)
    except:
        #TODO use other g2p instead iof this - it's internal
        cmd = "cd ../validation/misc/http_phonetiser; nohup python http_phonetiser.py &"
        sys.stderr.write("%s\n" % cmd)
        os.system(cmd)
        while True:
            sys.stderr.write("Waiting for g2p to start..\n")
            try:
                res = requests.get("http://localhost:5000")
                sys.stderr.write("%s\n" % res.text.strip())
                assert res.text.strip() == "It works"
                break
            except:
                time.sleep(1)
                pass

        return g2p(word, lang)


    data = response.text.replace("\n", " ")
    m = re.search("<word [^>]+>([^<]+)</word>", data)
    trans = m.group(1)
    sys.stderr.write("http_phonetiser: %s -> %s\n" % (word, trans))
    return trans
    

def rbg2p(word, lang):
    #sys.stderr.write("rbg2p: %s\n" % word)

    #g2pname = conf[lang]["g2p_name"]
    g2pname = conf["g2p_name"]
    url = "http://localhost:6771/transcribe/%s/%s" % (g2pname, word)

    try:
        response = requests.get(url)
    except:
        #rbg2p and g2p_rules from github
        #g2p_rules only internal, otherwise use rbg2p/cmd/server/g2p_files instead
        #cmd = "cd ../rbg2p; nohup go run cmd/server/server.go cmd/server/g2p_files/ &"
        cmd = "cd ../rbg2p; nohup go run cmd/server/server.go ../g2p_rules/ &"
        sys.stderr.write("%s\n" % cmd)
        os.system(cmd)
        while True:
            sys.stderr.write("Waiting for g2p to start..\n")
            try:
                res = requests.get("http://localhost:6771/ping")
                sys.stderr.write("%s\n" % res.text.strip())
                assert res.text.strip() == "rbg2p"
                break
            except:
                time.sleep(1)
                pass

        return g2p(word, lang)


    data = response.json()
    trans = data["transes"][0]
    return trans
    
def syllabify(trans, lang):
    if not lang in conf or "syllabifier_name" in conf[lang]:
        return trans

    
    sys.stderr.write("syllabify: %s\n" % trans)

    trans = trans.replace('"', "'")


    #HB there's a problem with initial % in the syllabifier? But test in syll file doesn't fail..
    sec_first = False
    if trans.startswith("%"):
        sec_first = True
        trans = trans[2:]
    
    
    #g2pname = "sws"
    #url = "http://localhost:6771/transcribe/%s/%s" % (g2pname, word)
    #g2pname = "enu_ws-sampa"
    syllabifier_name = conf[lang]["syllabifier_name"]
    url = "http://localhost:6771/syllabify/%s/%s" % (syllabifier_name, trans)

    try:
        response = requests.get(url)
    except:
        #rbg2p and g2p_rules from github
        #g2p_rules only internal, otherwise use rbg2p/cmd/server/g2p_files instead
        #cmd = "cd ../rbg2p; nohup go run cmd/server/server.go cmd/server/g2p_files/ &"
        cmd = "cd ../rbg2p; nohup go run cmd/server/server.go ../g2p_rules/ &"
        sys.stderr.write("%s\n" % cmd)
        os.system(cmd)
        while True:
            sys.stderr.write("Waiting for syllabifier to start..\n")
            try:
                res = requests.get("http://localhost:6771/ping")
                sys.stderr.write("%s\n" % res.text.strip())
                assert res.text.strip() == "rbg2p"
                break
            except:
                time.sleep(1)
                pass

        return syllabify(trans, lang)


    #data = response.json()
    #trans = data["transes"][0]
    trans = response.text.strip()

    #HB there's a problem with initial % in the syllabifier? But test in syll file doesn't fail..
    if sec_first:
        trans = "% "+trans

    
    sys.stderr.write("syllabify returning: %s\n" % (trans))
    return trans
    

maptable = {
    "en": {
        "tx": "t",
        "3R": "r0",
        "{": "e",
        "@": "e0",
        "AU": "aU",
        "OU": "oU",
        "EU": "eU",
        "@U": "eU",
        "AI": "aI",
        "OI": "oI",
        "EI": "eI"
    },

    "sv": {
        "}:": "u1:",
        "9": "o9",
        "9:": "o9:",
        "2": "o2",
        "2:": "o2:",
        "{:": "AE:",
        "{": "E",
        "@": "e0",
        "eu": "EU",
        "au": "aU",
        "x": "S"
    }    
}

def mapTranscriptionsForSimpleLabel(transcriptions, lang):
    #TODO this mapping will need to be moved into transcribe, to allow for sv-en
    newtranscriptions = []
    for trans in transcriptions:
        newtrans = mapTrans(trans,lang)
        newtranscriptions.append(newtrans)
    return newtranscriptions


def mapTrans(trans, lang):
    newtrans = []
    stress = "0"
    for symbol in trans.split(" "):
        #sys.stderr.write("%s\n" % symbol)
        if symbol in ['"', "'"]:
            stress = "1"
            continue
        elif symbol == '""' and lang == "sv":
            stress = "2"
            continue
        elif symbol == '%':
            if lang == "sv":
                stress = "3"
            else:
                stress = "2"
            continue
            
        if symbol == ".":
            newtrans.append(stress)
            stress = "0"
        if symbol.endswith(";"):
            symbol = re.sub(";$",":", symbol)

        if symbol in maptable[lang]:
            #sys.stderr.write("%s\n" % "In maptable: %s -> %s" % (symbol, maptable[symbol]))
            newtrans.append(maptable[lang][symbol])
        else:
            newtrans.append(symbol)
    newtrans.append(stress)
    return " ".join(newtrans)


def add_e_to_en_phones(trans):
    newtrans = []
    for symbol in trans.split(" "):
        if not symbol in ["0", "1", "2", "3", ".", "#", "--"]:
            newsymbol = symbol+"_e"
            newtrans.append(newsymbol)
        else:
            newtrans.append(symbol)
    return " ".join(newtrans)



def process(text, lang):
    sys.stderr.write("INPUT TEXT: %s\n" % text)

    #text = re.sub("([.,?!:;()/-]) ", r" sil ", text)
    #text = re.sub("([.,?!:;()/-])", r"", text)

    text = re.sub("--", " sil ", text)
    text = re.sub("’", "'", text)
    
    text = re.sub("([^a-zåäöéA-ZÅÄÖÉ0-9 '-])", r" sil ", text)
    
    text = re.sub("\s+", " ", text)
    text = text.strip()
    #text = re.sub("([.,?!:;-])$", r"", text)
    sys.stderr.write("TEXT: %s\n" % text)
    
    transcriptions = transcribeText(text, lang)
    #transcriptions = mapTransForSimpleLabel(transcriptions, lang)
    print(" # ".join(transcriptions))

