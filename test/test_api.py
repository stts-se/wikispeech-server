import sys, requests
import json

####################################
#
#  These tests require a running wikispeech.py server:
#
#  python3 wikispeech.py
#
#  python3 test/test_api.py
#




i = 0
def test_done():
    global i
    sys.stdout.write(".")
    sys.stdout.flush()
    i += 1

def all_done():
    global i
    sys.stdout.write("\n%d tests OK\n" % i)

host = "http://localhost:10000/wikispeech/"


#1 wikispeech api

#1.1
## OPTIONS <host>
## curl -X OPTIONS "http://localhost:10000/wikispeech/
## Expects list of languages
## TODO also return textprocessor and voice names for each language 
expected = ["sv", "nb", "en", "ar"]

r = requests.options(host)
res = r.json()

assert (type(res) == type([]))
assert ( res == expected ) , "%s and %s are not equal" % (expected, res)
test_done()

#1.2
## GET/POST <host>
## curl "http://localhost:10000/wikispeech/
## Expects html usage message
r = requests.get(host)
res = r.text
assert (type(res) == type(""))
test_done()


r = requests.post(host)
res = r.text
assert (type(res) == type(""))
test_done()


#1.3
## GET/POST <host> args: input, lang
## curl "http://localhost:10000/wikispeech/?lang=en&input=test."
## Expects json with audio_url and token list

parameters = {
    "input":"test.",
    "lang":"sv"
}

## GET
r = requests.get("%s" % (host), params=parameters)
res = r.json()
#print(res)
assert ( type(res) == type({}) )
assert ( type(res["tokens"]) == type([]) )
assert ( type(res["audio"]) == type("") )
test_done()


## POST
r = requests.post("%s" % (host), data=parameters)
res = r.json()
#print(res)
assert ( type(res) == type({}) )
assert ( type(res["tokens"]) == type([]) )
assert ( type(res["audio"]) == type("") )
test_done()


#1.4
#Input can be "TEST_EXAMPLE" + lang
## curl "http://localhost:10000/wikispeech/?lang=en&input=TEST_EXAMPLE"
#TODO only defined for english. If not defined returns a message string instead
parameters = {
    "input":"TEST_EXAMPLE",
    "lang":"en"
}

## GET
r = requests.get("%s" % (host), params=parameters)
res = r.json()
#print(res)
assert ( type(res) == type({}) )
assert ( type(res["tokens"]) == type([]) )
assert ( type(res["audio"]) == type("") )
test_done()


#1.5
#textprocessor arg can be set, returns message if it isn't defined
## curl "http://localhost:10000/wikispeech/?lang=sv&input=test.&textprocessor=a_textprocessor_that_is_not_defined"
parameters = {
    "input":"test.",
    "lang":"sv",
    "textprocessor":"a_textprocessor_that_is_not_defined"
}

## GET

r = requests.get("%s" % (host), params=parameters)
res = r.text
#print(res)
assert ( type(res) == type("") )
expected = "ERROR: Textprocessor a_textprocessor_that_is_not_defined not defined for language sv"
assert ( res == expected ), "%s != %s" % (res, expected)
test_done()


#1.6
#voice arg can be set, returns message if the voice isn't defined
## curl "http://localhost:10000/wikispeech/?lang=sv&input=test.&voice=a_voice_that_is_not_defined"
parameters = {
    "input":"test.",
    "lang":"sv",
    "voice":"a_voice_that_is_not_defined"
}

## GET
r = requests.get("%s" % (host), params=parameters)
res = r.text
#print(res)
assert ( type(res) == type("") )
expected = "ERROR: voice a_voice_that_is_not_defined not defined for language sv."
assert ( res == expected ), "%s != %s" % (res, expected)
test_done()

#input and output formats can be redefined, but currently only input_format=text and output_format=json are allowed so no point in testing


#2) textprocessing api

host = "http://localhost:10000/wikispeech/textprocessing/"

# 2.1
# OPTIONS:  curl -X OPTIONS "http://localhost:10000/wikispeech/textprocessing/"
# TODO Currently nothing. Should return list of allowed parameters?

r = requests.options("%s" % (host))
res = r.text
expected = ""
assert ( res == expected ), "%s != %s" % (res, expected)
test_done()

# 2.2
# GET:  curl "http://localhost:10000/wikispeech/textprocessing/"
# Returns a (bad) error message
# TODO Better message, with suggested usage? Similar to /wikispeech/

r = requests.get("%s" % (host))
res = r.text
expected = "ERROR: No textprocessor available for language None"
assert ( res == expected ), "%s != %s" % (res, expected)
test_done()

# 2.3
# GET:  curl "http://localhost:10000/wikispeech/textprocessing/languages"
# returns list of textprocessors for all supported languages

r = requests.get("%slanguages" % (host))
res = r.json()
assert ( type(res) == type([]) )

expected = ["sv", "nb", "en", "ar"]
for textprocessor in res:    
    assert ( textprocessor["lang"] in expected ), "%s not in  %s" % (textprocessor["lang"], expected)
test_done()


# 2.4
# GET:  curl "http://localhost:10000/wikispeech/textprocessing/languages/sv"
# returns list of defined textprocessors for <lang>

r = requests.get("%slanguages/sv" % (host))
res = r.json()
assert ( type(res) == type([]) )
expected = ["wikitextproc_sv"]
for textprocessor in res:    
    assert ( textprocessor["name"] in expected ), "%s not in %s" % (textprocessor["name"], expected)
test_done()

# 2.5
# GET:  curl "http://localhost:10000/wikispeech/textprocessing/?lang=en&input=test."
# returns json markup

parameters = {
    "lang":"en",
    "input":"test."
}

r = requests.get("%s" % (host), params=parameters)
res = r.json()
assert ( type(res) == type({}) )

expected = {"children": [{"children": [{"children": [{"children": [{"accent": "!H*", "children": [{"accent": "!H*", "children": [{"p": "t", "tag": "ph"}, {"p": "E", "tag": "ph"}, {"p": "s", "tag": "ph"}, {"p": "t", "tag": "ph"}], "ph": "t E s t", "stress": "1", "tag": "syllable"}], "g2p_method": "lexicon", "ph": "' t E s t", "pos": "NN", "tag": "t", "text": "test"}, {"pos": ".", "tag": "t", "text": "."}, {"breakindex": "5", "tag": "boundary", "tone": "L-L%"}], "tag": "phrase"}], "tag": "s"}], "tag": "p"}], "tag": "utt"}

assert ( res == expected ), "%s != %s" % (res, expected)
test_done()

# 2.6
# textprocessor can be an argument, returns message if not defined
# GET:  curl "http://localhost:10000/wikispeech/textprocessing/?lang=en&input=test.&textprocessor=undefined"

parameters = {
    "lang":"en",
    "input":"test.",
    "textprocessor":"undefined"
}

r = requests.get("%s" % (host), params=parameters)
res = r.text
assert ( type(res) == type("") )

expected = "ERROR: Textprocessor undefined not defined for language en"

assert ( res == expected ), "%s != %s" % (res, expected)
test_done()


#3) synthesis api

host = "http://localhost:10000/wikispeech/synthesis/"

# 3.1
# OPTIONS:  curl -X OPTIONS "http://localhost:10000/wikispeech/synthesis/"
# TODO Currently nothing. Should return list of allowed parameters?

r = requests.options("%s" % (host))
res = r.text
expected = ""
assert ( res == expected ), "%s != %s" % (res, expected)
test_done()

# 3.2
# GET:  curl "http://localhost:10000/wikispeech/synthesis/"
# Returns a (bad) error message
# TODO Better message, with suggested usage? Similar to /wikispeech/

r = requests.get("%s" % (host))
res = r.text
expected = "synthesis does not support language None"
assert ( res == expected ), "%s != %s" % (res, expected)
test_done()


# 3.3
# GET:  curl "http://localhost:10000/wikispeech/synthesis/voices"
# returns list of voices for all supported languages

r = requests.get("%svoices" % (host))
res = r.json()
assert ( type(res) == type([]) )

expected = ["sv", "nb", "en", "ar"]
for voice in res:    
    assert ( voice["lang"] in expected ), "%s not in  %s" % (voice["lang"], expected)
test_done()


# 3.4
# GET:  curl "http://localhost:10000/wikispeech/synthesis/voices/sv"
# returns list of defined voicess for <lang>

r = requests.get("%svoices/sv" % (host))
res = r.json()
assert ( type(res) == type([]) )
expected = ["stts_sv_nst-hsmm", "espeak_mbrola_sv1"]
for voice in res:    
    assert ( voice["name"] in expected ), "%s not in %s" % (voice["name"], expected)
test_done()

# 3.5
# GET:  curl "http://localhost:10000/wikispeech/synthesis/?lang=en&input=test."
# returns json, with "audio" url and "tokens" list
markup = {"children": [{"children": [{"children": [{"children": [{"accent": "!H*", "children": [{"accent": "!H*", "children": [{"p": "t", "tag": "ph"}, {"p": "E", "tag": "ph"}, {"p": "s", "tag": "ph"}, {"p": "t", "tag": "ph"}], "ph": "t E s t", "stress": "1", "tag": "syllable"}], "g2p_method": "lexicon", "ph": "' t E s t", "pos": "NN", "tag": "t", "text": "test"}, {"pos": ".", "tag": "t", "text": "."}, {"breakindex": "5", "tag": "boundary", "tone": "L-L%"}], "tag": "phrase"}], "tag": "s"}], "tag": "p"}], "tag": "utt"}

parameters = {
    "lang":"en",
    "input":json.dumps(markup)
}


r = requests.get("%s" % (host), params=parameters)
res = r.json()
assert ( type(res) == type({}) )

#This doesn't always match..
#The order of parameters can be different!
expected = {"audio": "http://morf.se:59125/process?INPUT_TYPE=ALLOPHONES&LOCALE=en&INPUT_TEXT=%3C%3Fxml+version%3D%221.0%22+encoding%3D%22UTF-8%22%3F%3E%3Cmaryxml+version%3D%220.5%22+xml%3Alang%3D%22en%22+xmlns%3D%22http%3A%2F%2Fmary.dfki.de%2F2002%2FMaryXML%22+xmlns%3Axsi%3D%22http%3A%2F%2Fwww.w3.org%2F2001%2FXMLSchema-instance%22%3E%3Cp%3E%3Cs%3E%3Cphrase%3E%3Ct+accent%3D%22%21H%2A%22+g2p_method%3D%22lexicon%22+ph%3D%22%27+t+E+s+t%22+pos%3D%22NN%22%3Etest%3Csyllable+accent%3D%22%21H%2A%22+ph%3D%22t+E+s+t%22+stress%3D%221%22%3E%3Cph+p%3D%22t%22+%2F%3E%3Cph+p%3D%22E%22+%2F%3E%3Cph+p%3D%22s%22+%2F%3E%3Cph+p%3D%22t%22+%2F%3E%3C%2Fsyllable%3E%3C%2Ft%3E%3Ct+pos%3D%22.%22%3E.%3C%2Ft%3E%3Cboundary+breakindex%3D%225%22+tone%3D%22L-L%25%22+%2F%3E%3C%2Fphrase%3E%3C%2Fs%3E%3C%2Fp%3E%3C%2Fmaryxml%3E&VOICE=dfki-spike-hsmm&AUDIO=WAVE_FILE&OUTPUT_TYPE=AUDIO", "tokens": [["test", 0.465], [".", 0.465], ["", 1.265]]}

#assert ( res == expected ), "%s != %s" % (res, expected)
test_done()


# 3.6
# GET:  curl "http://localhost:10000/wikispeech/synthesis/?lang=en&input=test.&voice=cmu-slt-flite"
# GET:  curl "http://localhost:10000/wikispeech/synthesis/?lang=en&input=\{\}&voice=undefined"
# voice can be an argument, returns message if not defined


parameters = {
    "lang":"en",
    "input":json.dumps(markup),
    "voice":"undefined"
}

r = requests.get("%s" % (host), params=parameters)
res = r.text
assert ( type(res) == type("") )

expected = "ERROR: voice undefined not defined for language en."

assert ( res == expected ), "%s != %s" % (res, expected)
test_done()


#######################################################


all_done()
