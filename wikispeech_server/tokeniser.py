#-*- coding: utf-8 -*-
import re, json, sys

import wikispeech_server.log as log

test1 = """
Token1 token2, token3 token4. Token5 token6. Xxx yyy.

Token9.
"""

test2 = """
<p>
<s>
Token1 token2, token3 token4.
</s>
<s>Token5 token6.</s>
<s>
<token>Xxx</token>
<token>yyy.</token>
</s>
</p>
<p>
Token9.
</p>
"""

# both return (with add_text set to False, otherwise they are different..):

#{"name": "utt1", "paragraphs": [{"name": "par1", "sentences": [{"name": "sent1", "phrases": [{"name": "phrase1", "tokens": [{"name": "token1", "text": "Token1"}, {"name": "token2", "punct": ",", "text": "token2"}]}, {"name": "phrase2", "tokens": [{"name": "token3", "text": "token3"}, {"name": "token4", "punct": ".", "text": "token4"}]}]}, {"name": "sent2", "phrases": [{"name": "phrase3", "tokens": [{"name": "token5", "text": "Token5"}, {"name": "token6", "punct": ".", "text": "token6"}]}]}, {"name": "sent3", "phrases": [{"name": "phrase4", "tokens": [{"name": "token7", "text": "Xxx"}, {"name": "token8", "punct": ".", "text": "yyy"}]}]}]}, {"name": "par2", "sentences": [{"name": "sent4", "phrases": [{"name": "phrase5", "tokens": [{"name": "token9", "punct": ".", "text": "Token9"}]}]}]}]}


#remove any start tags (<p>, <s>, <phrase>, <token>..). Remove all remaining "<[^>*]>" ? Any tags that can not be used.

end_paragraph = "</p>|\n\n"
#Svårt att läsa med positive lookbehind och lookahead, men det fungerar
end_sentence = "</s>|(?<=[.?!:]) (?=[A-ZÑÅÄÁÉÍÓÚ0-9])"
end_phrase = "</phrase>|(?<=[),;-]) | (?=[(])"

end_token = "</token>| "
punctuation = "[(),;.¿?¡!-]"




def tokenise(text, add_text=False, lang='en'):
    text = text.strip()
    pars = re.split(end_paragraph, text)
    paragraphs = []
    utt = {
        "paragraphs":paragraphs
    }
    if add_text:
        utt["text"] = text



    p_nr = 0
    s_nr = 0
    phr_nr = 0
    t_nr = 0


    for par in pars:
        p_nr += 1
        par = par.strip()
        par = re.sub("\n", "", par)
        #print("PAR: #%s#" % par)
        if par == "":
            continue

        sentences = []
        p = {
            #"name":"par"+str(p_nr),
            "sentences":sentences
        }
        if add_text:
            p["text"] = par



        paragraphs.append(p)

        if lang=='eu':
            end_sentence = "</s>|(?<=[?!:]) (?=[A-ZÑÅÄÁÉÍÓÚ0-9])"
        else:
            end_sentence = "</s>|(?<=[.?!:]) (?=[A-ZÑÅÄÁÉÍÓÚ0-9])"
        sents = re.split(end_sentence,par)                            
        
        for sent in sents:
            if sent == "":
                continue
            s_nr += 1
            #print("SENT: %d #%s#" % (s_nr, sent))

            sent = sent.strip()
            phraselist = []
            s =  {
                #"name":"sent"+str(s_nr),
                "phrases":phraselist
            }
            if add_text:
                s["text"] = sent


            sentences.append(s)
            phrases = re.split(end_phrase, sent)

            for phrase in phrases:
                phr_nr += 1
                phrase = phrase.strip()
                tokenlist = []
                phr =  {
                    #"name":"phrase"+str(phr_nr),
                    "tokens":tokenlist
                }
                if add_text:
                    phr["text"] = phrase



                phraselist.append(phr)
                #print("PHRASE: #%s#" % phrase)
                tokens = re.split(end_token, phrase)
                #print "TOKENS:", tokens

                for token in tokens:
                    token = token.strip()
                    if token == "":
                        continue
                    t_nr += 1
                    token = re.sub("<[^>]*>", "", token)
                    prepunct = None
                    punct = None
                    #.*? non-greedy match, because punctuation can be repeated '("hello?")'
                    m = re.search("^("+punctuation+"*)(.*?)("+punctuation+"*)$", token)
                    if m:
                        prepunct = m.group(1)
                        word = m.group(2)
                        punct = m.group(3)
                    
                    t =  {
                        #"name":"token"+str(t_nr),
                        "token_orth":token,
                        "words": [
                            {
                                "orth":word
                            }
                        ]
                    }

                    if prepunct:
                        t["prepunct"] = prepunct
                    if punct:
                        t["punct"] = punct

                    tokenlist.append(t)
                    #print("TOKEN: %s" % token)
    return utt



def utt2maryxml_TOKENS(lang, utt):
    maryxmllist = ['<?xml version="1.0" encoding="UTF-8"?><maryxml xmlns="http://mary.dfki.de/2002/MaryXML" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="0.5" xml:lang="%s">' % lang]
    for par in utt["children"]:
        maryxmllist.append("<p>")
        for sent in par["children"]:
            maryxmllist.append("<s>")
            for phrase in sent["children"]:
                #if len(sent["phrases"]) > 1:
                #    maryxmllist.append("<phr>")
                for token in phrase["children"]:
                    maryxmllist.append("<t>")
                    maryxmllist.append(token["text"])
                    maryxmllist.append("</t>")
                    if "punct" in token:
                        maryxmllist.append("<t>")
                        maryxmllist.append(token["punct"])
                        maryxmllist.append("</t>")
                        
                #if len(sent["phrases"]) > 1:
                #    maryxmllist.append("</phr>")
            maryxmllist.append("</s>")
        maryxmllist.append("</p>")
    maryxmllist.append("</maryxml>")

    return "\n".join(maryxmllist)


if __name__ == "__main__":
    from maryxml_converter import utt2maryxml

    utt1 = tokenise(test1)
    utt2 = tokenise(test2)

    if json.dumps(utt1, sort_keys=True) != json.dumps(utt2, sort_keys=True):
        print("ERROR: mismatch")
        print(json.dumps(utt1, sort_keys=True, indent=2))
        print("ERROR: mismatch")
        print(json.dumps(utt2, sort_keys=True, indent=2))
        print("ERROR: mismatch")
        sys.exit()

    #print(json.dumps(utt2, sort_keys=True))

    #print(json.dumps(tokenise("Det var en gång en (gubbe), som bodde i en låda. 123 hejsan! Sista meningen.", add_text=True), sort_keys=True, indent=2))

    utt3 = tokenise("Hej.")
    #print(json.dumps(utt3, sort_keys=True, indent=2))
    maryxml = utt2maryxml_TOKENS("sv", utt3)
    #maryxml = utt2maryxml("sv", utt3)
    if maryxml != """<?xml version="1.0" encoding="UTF-8"?><maryxml xmlns="http://mary.dfki.de/2002/MaryXML" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="0.5" xml:lang="sv">
<p>
<s>
<t>
Hej
</t>
<t>
.
</t>
</s>
</p>
</maryxml>""":
        print(maryxml)

    utt4 = tokenise("Hej, hej.")
    #print(json.dumps(utt3, sort_keys=True, indent=2))
    maryxml = utt2maryxml_TOKENS("sv", utt4)
    #maryxml = utt2maryxml("sv", utt4)
    if maryxml != """<?xml version="1.0" encoding="UTF-8"?><maryxml xmlns="http://mary.dfki.de/2002/MaryXML" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="0.5" xml:lang="sv">
<p>
<s>
<t>
Hej
</t>
<t>
,
</t>
<t>
hej
</t>
<t>
.
</t>
</s>
</p>
</maryxml>""":
        print(maryxml)
