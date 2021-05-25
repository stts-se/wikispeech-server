# -*- coding: utf-8 -*-

import sys
import json
import wikispeech_server.wikispeech as ws
import wikispeech_server.log as log

i = 0
def test_done():
    global i
    log.debug("OK")
    sys.stdout.write(".")
    sys.stdout.flush()
    i += 1

def all_done():
    global i
    sys.stdout.write("\n%d tests OK\n" % i)

host = "/"
test_client = ws.app.test_client()


log.debug("RUNNING API TESTS")

#1 wikispeech api

#1.1
## OPTIONS <host>
## curl -X OPTIONS "http://localhost:10000/
## Expects description of call and parameters

log.debug("RUNNING TEST 1.1")

#expected_langs = ["sv", "nb", "en", "ar"]
#expected_langs = ["sv", "nb", "en"] # HL 2017-09-11
expected_langs = ["en"] # HB 2020-03-24

r = test_client.options(host)
res = json.loads(r.data.decode('utf-8'))
langs = res["GET"]["parameters"]["lang"]["allowed"]

assert (type(res) == type({}))
#assert ( res == expected ) , "%s and %s are not equal" % (expected, res)
#assert ( langs == expected_langs ) , "%s and %s are not equal" % (expected_langs, langs)


for lang in expected_langs:
    assert lang in langs, "expected_lang %s not found in %s (expected_langs: %s)" % (lang, langs, expected_langs)


test_done()

#1.2
## GET/POST <host>
## curl "http://localhost:10000/
## Expects html usage message
r = test_client.get(host)
res = r.data.decode('utf-8')
assert (type(res) == type(""))
test_done()


r = test_client.post(host)
res = r.data.decode('utf-8')
assert (type(res) == type(""))
test_done()

#1.3
## GET/POST <host> args: input, lang
## curl "http://localhost:10000/?lang=en&input=test."
## Expects json with audio_url and token list

parameters = {
    "input":"test.",
    "lang":"en"
}

## GET
r = test_client.get("%s" % (host), query_string=parameters)
res = json.loads(r.data.decode('utf-8'))
#print(res)
assert ( type(res) == type({}) )
assert ( type(res["tokens"]) == type([]) )
assert ( type(res["audio_data"]) == type("") )
test_done()


## POST
r = test_client.post("%s" % (host), data=parameters)
res = json.loads(r.data.decode('utf-8'))
#print(res)
assert ( type(res) == type({}) )
assert ( type(res["tokens"]) == type([]) )
assert ( type(res["audio_data"]) == type("") )
test_done()








#1.4
#Input can be "TEST_EXAMPLE" + lang
## curl "http://localhost:10000/?lang=en&input=TEST_EXAMPLE"
#TODO only defined for english. If not defined returns a message string instead
parameters = {
    "input":"TEST_EXAMPLE",
    "lang":"en"
}

## GET
r = test_client.get("%s" % (host), query_string=parameters)
res = json.loads(r.data.decode('utf-8'))
#print(res)
assert ( type(res) == type({}) )
assert ( type(res["tokens"]) == type([]) )
assert ( type(res["audio"]) == type("") )
test_done()


#1.5
#textprocessor arg can be set, returns message if it isn't defined
## curl "http://localhost:10000/?lang=sv&input=test.&textprocessor=a_textprocessor_that_is_not_defined"
parameters = {
    "input":"test.",
    "lang":"en",
    "textprocessor":"a_textprocessor_that_is_not_defined"
}

## GET

r = test_client.get("%s" % (host), query_string=parameters)
res = r.data.decode('utf-8')
#print(res)
assert ( type(res) == type("") )
expected = "ERROR: Textprocessor a_textprocessor_that_is_not_defined not defined for language %s" % parameters["lang"]
assert ( res == expected ), "%s != %s" % (res, expected)
test_done()


#1.6
#voice arg can be set, returns message if the voice isn't defined
## curl "http://localhost:10000/?lang=sv&input=test.&voice=a_voice_that_is_not_defined"
parameters = {
    "input":"test.",
    "lang":"en",
    "voice":"a_voice_that_is_not_defined"
}

## GET
r = test_client.get("%s" % (host), query_string=parameters)
res = r.data.decode('utf-8')
#print(res)
assert ( type(res) == type("") )
expected = "ERROR: voice %s not defined for language %s." % (parameters["voice"], parameters["lang"])
assert ( res == expected ), "%s != %s" % (res, expected)
test_done()

#input and output types can be redefined, but currently only input_typetext and output_type=json are allowed so no point in testing



#2) textprocessing api


host = "http://localhost:10000/textprocessing/"

# 2.1
# OPTIONS:  curl -X OPTIONS "http://localhost:10000/textprocessing/"


r = test_client.options("%s" % (host))
res = json.loads(r.data.decode('utf-8'))
expected = {}
assert ( type(res) == type(expected) ), "%s != %s" % (res, expected)
test_done()

# 2.2
# GET:  curl "http://localhost:10000/textprocessing/"
# Returns a (bad) error message
# TODO Better message, with suggested usage? Similar to /
# Now returns same as OPTIONS

r = test_client.get("%s" % (host))
res = r.data.decode('utf-8')
expected = "ERROR: No textprocessor available for language None"
#assert ( res == expected ), "%s != %s" % (res, expected)
test_done()

# 2.3
# GET:  curl "http://localhost:10000/textprocessing/languages"
# returns list of supported languages

r = test_client.get("%slanguages" % (host))
res = json.loads(r.data.decode('utf-8'))
assert ( type(res) == type([]) )


#expected = ["sv", "nb", "en"]
#Minimal: only test for english
expected = ["en"]
for lang in expected:    
    assert ( lang in res ), "%s not in  %s" % (lang, expected)
test_done()


# 2.4
# GET:  curl "http://localhost:10000/textprocessing/textprocessors/sv"
# returns list of defined textprocessors for <lang>

r = test_client.get("%stextprocessors/sv" % (host))
res = json.loads(r.data.decode('utf-8'))
assert ( type(res) == type([]) )
#HB 18/10 2017 Can't expect any particular textprocessor to exist
#expected = ["marytts_textproc_sv"]
#for textprocessor in res:    
#    assert ( textprocessor["name"] in expected ), "%s not in %s" % (textprocessor["name"], expected)
test_done()

# 2.5
# GET:  curl "http://localhost:10000/textprocessing/?lang=en&input=test."
# returns json markup

parameters = {
    "lang":"en",
    "input":"test."
}

r = test_client.get("%s" % (host), query_string=parameters)
res = json.loads(r.data.decode('utf-8'))
assert ( type(res) == type({}) )

#expected = {'paragraphs': [{'sentences': [{'phrases': [{'boundary': {'breakindex': '5', 'tone': 'L-L%'}, 'tokens': [{'token_orth': 'test', 'words': [{'accent': '!H*', 'g2p_method': 'lexicon', 'pos': 'NN', 'trans': "' t E s t", 'orth': 'test'}]}, {'token_orth': '.', 'words': [{'pos': '.', 'orth': '.'}]}]}]}]}], 'lang': 'en-US'}

#expected = {'lang': 'en-US', 'paragraphs': [{'sentences': [{'phrases': [{'tokens': [{'token_orth': 'test', 'words': [{'g2p_method': 'lexicon', 'pos': 'NN', 'trans': "' t E s t", 'accent': '!H*', 'orth': 'test'}]}, {'token_orth': '.', 'words': [{'pos': '.', 'orth': '.'}]}], 'boundary': {'breakindex': '5', 'tone': 'L-L%'}}]}]}]}

#Marytts 
expected = {'lang': 'en-US', 'paragraphs': [{'sentences': [{'phrases': [{'boundary': {'breakindex': '5', 'tone': 'L-L%'}, 'tokens': [{'token_orth': 'test', 'words': [{'accent': '!H*', 'g2p_method': 'lexicon', 'orth': 'test', 'pos': '', 'trans': "' t E s t"}]}, {'token_orth': '.', 'words': [{'orth': '.', 'pos': '.'}]}]}]}]}]}

#Flite
#expected = {'lang': 'en', 'original_text': 'test.', 'paragraphs': [{'sentences': [{'phrases': [{'tokens': [{'punct': '.', 'token_orth': 'test.', 'words': [{'orth': 'test'}]}]}]}]}]}



assert ( res == expected ), "%s != %s" % (res, expected)
test_done()

# 2.6
# textprocessor can be an argument, returns message if not defined
# GET:  curl "http://localhost:10000/textprocessing/?lang=en&input=test.&textprocessor=undefined"

parameters = {
    "lang":"en",
    "input":"test.",
    "textprocessor":"undefined"
}

r = test_client.get("%s" % (host), query_string=parameters)
res = r.data.decode('utf-8')
assert ( type(res) == type("") )

expected = "ERROR: Textprocessor undefined not defined for language en"

assert ( res == expected ), "%s != %s" % (res, expected)
test_done()

#Starting test of ssml input
#2.7
#input_type can be set to ssml
#the textprocessing will then use the ssml (to begin with phoneme, break, perhaps some say-as) to build the output json
#First full ssml. Later ssml chunks?
# GET:  curl "http://localhost:10000/textprocessing/?lang=sv&input_type=ssml&input=<SSML>"

ssml = """<?xml version="1.0" encoding="ISO-8859-1"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://www.w3.org/2001/10/synthesis
                 http://www.w3.org/TR/speech-synthesis11/synthesis.xsd"
       xml:lang="sv">

  Det här är ett test av <phoneme alphabet="x-sampa" ph="b a . b I . &quot; A: n">SSML</phoneme>

</speak>"""

testing_language = "sv"
#testing_language = "en"

parameters = {
    "input":ssml,
    "lang":"%s" % testing_language,
    "input_type":"ssml"
}

## GET
r = test_client.get("%s" % (host), query_string=parameters)


#This is what we want
res = json.loads(r.data.decode('utf-8'))
assert ( type(res) == type({}) )

if testing_language == "sv":
    expected = {'lang': 'sv', 'paragraphs': [{'sentences': [{'phrases': [{'boundary': {'breakindex': '5', 'tone': 'L-L%'}, 'tokens': [{'token_orth': 'Det', 'words': [{'accent': 'L+H*', 'orth': 'Det', 'pos': 'content', 'trans': '"" d e:'}]}, {'token_orth': 'här', 'words': [{'accent': 'L+H*', 'g2p_method': 'lexicon', 'orth': 'här', 'pos': 'AB', 'trans': '" h {: r'}]}, {'token_orth': 'är', 'words': [{'accent': 'L+H*', 'g2p_method': 'lexicon', 'orth': 'är', 'pos': 'VB', 'trans': '" {: r'}]}, {'token_orth': 'ett', 'words': [{'g2p_method': 'lexicon', 'orth': 'ett', 'pos': 'DT', 'trans': '" E t'}]}, {'token_orth': 'test', 'words': [{'accent': 'L+H*', 'g2p_method': 'lexicon', 'orth': 'test', 'pos': 'NN', 'trans': '" t E s t'}]}, {'token_orth': 'av', 'words': [{'accent': 'L+H*', 'orth': 'av', 'pos': 'content', 'trans': '" A: v'}]}, {'token_orth': 'SSML', 'words': [{'accent': '!H*', 'input_ssml_transcription': True, 'orth': 'SSML', 'pos': 'content', 'trans': 'b a . b I . " A: n'}]}]}]}]}]}

elif testing_language == "en":
    expected = {'paragraphs': [{'sentences': [{'phrases': [{'tokens': [{'token_orth': '<?xml', 'words': [{'orth': '<?xml'}]}, {'token_orth': 'version="1.0"', 'words': [{'orth': 'version="1.0"'}]}, {'token_orth': 'encoding="ISO-8859-1"?><speak', 'words': [{'orth': 'encoding="ISO-8859-1"?><speak'}]}, {'token_orth': 'version="1.1"', 'words': [{'orth': 'version="1.1"'}]}, {'token_orth': 'xmlns="http://www.w3.org/2001/10/synthesis"', 'words': [{'orth': 'xmlns="http://www.w3.org/2001/10/synthesis"'}]}, {'token_orth': 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"', 'words': [{'orth': 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'}]}, {'token_orth': 'xsi:schemaLocation="http://www.w3.org/2001/10/synthesis', 'words': [{'orth': 'xsi:schemaLocation="http://www.w3.org/2001/10/synthesis'}]}, {'token_orth': 'http://www.w3.org/TR/speech-synthesis11/synthesis.xsd"', 'words': [{'orth': 'http://www.w3.org/TR/speech-synthesis11/synthesis.xsd"'}]}, {'token_orth': 'xml:lang="sv">', 'words': [{'orth': 'xml:lang="sv">'}]}]}]}]}, {'sentences': [{'phrases': [{'tokens': [{'token_orth': 'Det', 'words': [{'orth': 'Det'}]}, {'token_orth': 'här', 'words': [{'orth': 'här'}]}, {'token_orth': 'är', 'words': [{'orth': 'är'}]}, {'token_orth': 'ett', 'words': [{'orth': 'ett'}]}, {'token_orth': 'test', 'words': [{'orth': 'test'}]}, {'token_orth': 'av', 'words': [{'orth': 'av'}]}, {'token_orth': '<phoneme', 'words': [{'orth': '<phoneme'}]}, {'token_orth': 'alphabet="x-sampa"', 'words': [{'orth': 'alphabet="x-sampa"'}]}, {'token_orth': 'ph="b', 'words': [{'orth': 'ph="b'}]}, {'token_orth': 'a', 'words': [{'orth': 'a'}]}, {'token_orth': '.', 'words': [{'orth': ''}], 'prepunct': '.'}, {'token_orth': 'b', 'words': [{'orth': 'b'}]}, {'token_orth': 'I', 'words': [{'orth': 'I'}]}, {'token_orth': '.', 'words': [{'orth': ''}], 'prepunct': '.'}, {'token_orth': '&quot;', 'words': [{'orth': '&quot'}], 'punct': ';'}]}, {'tokens': [{'token_orth': 'A:', 'words': [{'orth': 'A:'}]}, {'token_orth': 'n">SSML', 'words': [{'orth': 'n">SSML'}]}]}]}]}, {'sentences': [{'phrases': [{'tokens': [{'token_orth': '', 'words': [{'orth': ''}]}]}]}]}], 'lang': 'en', 'original_text': '<?xml version="1.0" encoding="ISO-8859-1"?>\n<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis"\n       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n       xsi:schemaLocation="http://www.w3.org/2001/10/synthesis\n                 http://www.w3.org/TR/speech-synthesis11/synthesis.xsd"\n       xml:lang="sv">\n\n  Det här är ett test av <phoneme alphabet="x-sampa" ph="b a . b I . &quot; A: n">SSML</phoneme>\n\n</speak>'}

    
#print("RES:\n%s\nEXP:\n%s\n" % (res, expected))

assert ( res == expected ), "%s != %s" % (res, expected)
test_done()

#HB 210128
#Adding test here for ssml with ipa input

ssml = """<?xml version="1.0" encoding="ISO-8859-1"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://www.w3.org/2001/10/synthesis
                 http://www.w3.org/TR/speech-synthesis11/synthesis.xsd"
       xml:lang="en-GB">

  test <phoneme alphabet="ipa" ph="bæ">SSML</phoneme>

</speak>"""

ssml2 = """<?xml version="1.0" encoding="UTF-8" ?>
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.w3.org/2001/10/synthesis http://www.w3.org/TR/speech-synthesis/synthesis.xsd"
  xml:lang="en-US">
Welcome<break/>to the world of speech synthesis!
</speak>
"""


#testing_language = "sv"
testing_language = "en"

parameters = {
    "input":ssml,
    "lang":"%s" % testing_language,
    "input_type":"ssml"
}

r = test_client.get("%s" % (host), query_string=parameters)

#print(r)
#print(r.data)

res = json.loads(r.data.decode('utf-8'))
assert ( type(res) == type({}) )

test_done()


#3) synthesis api

host = "http://localhost:10000/synthesis/"

# 3.1
# OPTIONS:  curl -X OPTIONS "http://localhost:10000/synthesis/"


r = test_client.options("%s" % (host))
res = json.loads(r.data.decode('utf-8'))
expected = {}
assert ( type(res) == type(expected) ), "%s != %s" % (res, expected)
test_done()

# 3.2
# GET:  curl "http://localhost:10000/synthesis/"
# Returns a (bad) error message
# TODO Better message, with suggested usage? Similar to /
# Now returns same as OPTIONS

r = test_client.get("%s" % (host))
res = r.data.decode('utf-8')
expected = "synthesis does not support language None"
#assert ( res == expected ), "%s != %s" % (res, expected)
test_done()


# 3.3
# GET:  curl "http://localhost:10000/synthesis/voices"
# returns list of voices for all supported languages

r = test_client.get("%svoices" % (host))
res = json.loads(r.data.decode('utf-8'))
assert ( type(res) == type([]) )

#expected = ["sv", "nb", "en"]
#for voice in res:    
#    assert ( voice["lang"] in expected ), "%s not in  %s" % (voice["lang"], expected)
#test_done()


# 3.4
# GET:  curl "http://localhost:10000/synthesis/voices/sv"
# returns list of defined voicess for <lang>

r = test_client.get("%svoices/sv" % (host))
res = json.loads(r.data.decode('utf-8'))
assert ( type(res) == type([]) )
expected = ["stts_sv_nst-hsmm", "espeak_mbrola_sv1"]
#HB 200218
#for voice in res:    
#    assert ( voice["name"] in expected ), "%s not in %s" % (voice["name"], expected)
test_done()

# 3.5
# GET:  curl "http://localhost:10000/synthesis/?lang=en&input=test."
# returns json, with "audio" url and "tokens" list

markup = {"lang": "en-US", "paragraphs": [{"sentences": [{"phrases": [{"boundary": {"breakindex": "5", "tone": "L-L%"}, "tokens": [{"token_orth": "\"", "words": [{"orth": "\"", "pos": "."}]}, {"token_orth": "test", "words": [{"g2p_method": "lexicon", "orth": "test", "pos": "``", "trans": "' t E s t"}]}, {"token_orth": ".", "words": [{"orth": ".", "pos": "."}]}, {"token_orth": "\"", "words": [{"orth": "\"", "pos": "."}]}]}]}]}]}



parameters = {
    "lang":"en",
    "input":json.dumps(markup)
}


r = test_client.get("%s" % (host), query_string=parameters)
res = json.loads(r.data.decode('utf-8'))
assert ( type(res) == type({}) )

#This doesn't always match..
#The order of parameters can be different!
expected = {"audio": "http://morf.se:59125/process?INPUT_TYPE=ALLOPHONES&LOCALE=en&INPUT_TEXT=%3C%3Fxml+version%3D%221.0%22+encoding%3D%22UTF-8%22%3F%3E%3Cmaryxml+version%3D%220.5%22+xml%3Alang%3D%22en%22+xmlns%3D%22http%3A%2F%2Fmary.dfki.de%2F2002%2FMaryXML%22+xmlns%3Axsi%3D%22http%3A%2F%2Fwww.w3.org%2F2001%2FXMLSchema-instance%22%3E%3Cp%3E%3Cs%3E%3Cphrase%3E%3Ct+accent%3D%22%21H%2A%22+g2p_method%3D%22lexicon%22+ph%3D%22%27+t+E+s+t%22+pos%3D%22NN%22%3Etest%3Csyllable+accent%3D%22%21H%2A%22+ph%3D%22t+E+s+t%22+stress%3D%221%22%3E%3Cph+p%3D%22t%22+%2F%3E%3Cph+p%3D%22E%22+%2F%3E%3Cph+p%3D%22s%22+%2F%3E%3Cph+p%3D%22t%22+%2F%3E%3C%2Fsyllable%3E%3C%2Ft%3E%3Ct+pos%3D%22.%22%3E.%3C%2Ft%3E%3Cboundary+breakindex%3D%225%22+tone%3D%22L-L%25%22+%2F%3E%3C%2Fphrase%3E%3C%2Fs%3E%3C%2Fp%3E%3C%2Fmaryxml%3E&VOICE=dfki-spike-hsmm&AUDIO=WAVE_FILE&OUTPUT_TYPE=AUDIO", "tokens": [["test", 0.465], [".", 0.465], ["", 1.265]]}

#assert ( res == expected ), "%s != %s" % (res, expected)
test_done()


# 3.6
# GET:  curl "http://localhost:10000/synthesis/?lang=en&input=test.&voice=cmu-slt-flite"
# GET:  curl "http://localhost:10000/synthesis/?lang=en&input=\{\}&voice=undefined"
# voice can be an argument, returns message if not defined


parameters = {
    "lang":"en",
    "input":json.dumps(markup),
    "voice":"undefined"
}

r = test_client.get("%s" % (host), query_string=parameters)
res = r.data.decode('utf-8')
assert ( type(res) == type("") )

expected = "ERROR: voice undefined not defined for language en."

assert ( res == expected ), "%s != %s" % (res, expected)
test_done()



##########################
all_done()
