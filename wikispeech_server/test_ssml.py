# -*- coding: utf-8 -*-


import sys
sys.path.append(".")


import json
import wikispeech_server.wikispeech as ws
import wikispeech_server.log as log

host = "/wikispeech/textprocessing/"
test_client = ws.app.test_client()

#Starting test of ssml input
#2.7
#input_type can be set to ssml
#the textprocessing will then use the ssml (to begin with phoneme, break, perhaps some say-as) to build the output json
#First full ssml. Later ssml chunks?
# GET:  curl "http://localhost:10000/wikispeech/textprocessing/?lang=sv&input_type=ssml&input=<SSML>"

ssml = """<?xml version="1.0" encoding="ISO-8859-1"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://www.w3.org/2001/10/synthesis
                 http://www.w3.org/TR/speech-synthesis11/synthesis.xsd"
       xml:lang="sv">

  Det här är ett test av <phoneme alphabet="x-sampa" ph="b a - b I - &quot; A: n">SSML</phoneme>

</speak>"""

parameters = {
    "input":ssml,
    "lang":"sv",
    "input_type":"ssml"
}

## GET
r = test_client.get("%s" % (host), query_string=parameters)

print(r)

#This is what we want
res = json.loads(r.data.decode('utf-8'))
assert ( type(res) == type({}) )

#expected = {"lang": "sv", "paragraphs": [{"sentences": [{"phrases": [{"boundary": {"breakindex": "5", "tone": "L-L%"}, "tokens": [{"token_orth": "Det", "words": [{"accent": "L+H*", "g2p_method": "userdict", "orth": "Det", "pos": "content", "trans": "\"\" d e:"}]}, {"token_orth": "h\u00e4r", "words": [{"accent": "L+H*", "g2p_method": "lexicon", "orth": "h\u00e4r", "pos": "content", "trans": "\" h {: r"}]}, {"token_orth": "\u00e4r", "words": [{"accent": "L+H*", "g2p_method": "lexicon", "orth": "\u00e4r", "pos": "content", "trans": "\" {: r"}]}, {"token_orth": "ett", "words": [{"g2p_method": "lexicon", "orth": "ett", "pos": "function", "trans": "\" E t"}]}, {"token_orth": "test", "words": [{"accent": "L+H*", "g2p_method": "lexicon", "orth": "test", "pos": "content", "trans": "\" t E s t"}]}, {"token_orth": "av", "words": [{"accent": "L+H*", "g2p_method": "rules", "orth": "av", "pos": "content", "trans": "\" A: v"}]}, {"token_orth": "SSML", "words": [{"accent": "!H*", "orth": "SSML", "pos": "content", "trans": "b a . b I . \" A: n"}]}]}]}]}]}

expected = {'paragraphs': [{'sentences': [{'phrases': [{'boundary': {'breakindex': '5', 'tone': 'L-L%'}, 'tokens': [{'words': [{'pos': 'content', 'orth': 'Det', 'accent': 'L+H*', 'trans': '"" d e:'}], 'token_orth': 'Det'}, {'words': [{'pos': 'content', 'orth': 'här', 'g2p_method': 'lexicon', 'accent': 'L+H*', 'trans': '" h {: r'}], 'token_orth': 'här'}, {'words': [{'pos': 'content', 'orth': 'är', 'g2p_method': 'lexicon', 'accent': 'L+H*', 'trans': '" {: r'}], 'token_orth': 'är'}, {'words': [{'orth': 'ett', 'g2p_method': 'lexicon', 'pos': 'function', 'trans': '" E t'}], 'token_orth': 'ett'}, {'words': [{'pos': 'content', 'orth': 'test', 'g2p_method': 'lexicon', 'accent': 'L+H*', 'trans': '" t E s t'}], 'token_orth': 'test'}, {'words': [{'pos': 'content', 'orth': 'av', 'accent': 'L+H*', 'trans': '" A: v'}], 'token_orth': 'av'}, {'words': [{'pos': 'content', 'orth': 'SSML', 'accent': '!H*', 'trans': 'b a . b I . " A: n', 'input_ssml_transcription': True}], 'token_orth': 'SSML'}]}]}]}], 'lang': 'sv'}

print("RES:\n%s\nEXP:\n%s\n" % (res, expected))

assert ( res == expected ), "%s != %s" % (res, expected)

#This should only be printed if the assert succeeds
print("test_ssml finished")


