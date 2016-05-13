import sys, requests
import json

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
expected = ["sv", "en", "ar"]

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

payload = {
    "input":"test.",
    "lang":"sv"
}

## GET
r = requests.get("%s" % (host), params=payload)
res = r.json()
#print(res)
assert ( type(res) == type({}) )
assert ( type(res["tokens"]) == type([]) )
assert ( type(res["audio"]) == type("") )
test_done()


## POST
r = requests.post("%s" % (host), data=payload)
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
payload = {
    "input":"TEST_EXAMPLE",
    "lang":"en"
}

## GET
r = requests.get("%s" % (host), params=payload)
res = r.json()
#print(res)
assert ( type(res) == type({}) )
assert ( type(res["tokens"]) == type([]) )
assert ( type(res["audio"]) == type("") )
test_done()


#1.5
#textprocessor arg can be set, returns message if it isn't defined
## curl "http://localhost:10000/wikispeech/?lang=sv&input=test.&textprocessor=a_textprocessor_that_is_not_defined"
payload = {
    "input":"test.",
    "lang":"sv",
    "textprocessor":"a_textprocessor_that_is_not_defined"
}

## GET

r = requests.get("%s" % (host), params=payload)
res = r.text
#print(res)
assert ( type(res) == type("") )
expected = "ERROR: Textprocessor a_textprocessor_that_is_not_defined not defined for language sv"
assert ( res == expected ), "%s != %s" % (res, expected)
test_done()


#1.6
#voice arg can be set, returns message if the voice isn't defined
## curl "http://localhost:10000/wikispeech/?lang=sv&input=test.&voice=a_voice_that_is_not_defined"
payload = {
    "input":"test.",
    "lang":"sv",
    "voice":"a_voice_that_is_not_defined"
}

## GET
r = requests.get("%s" % (host), params=payload)
res = r.text
#print(res)
assert ( type(res) == type("") )
expected = "ERROR: voice a_voice_that_is_not_defined not defined for language sv."
assert ( res == expected ), "%s != %s" % (res, expected)
test_done()

#input and output formats can be redefined, but currently only input_format=text and output_format=json are allowed so no point in testing


#2) textprocessing api

# 2.1
# GET:  curl -X OPTIONS "http://localhost:10000/wikispeech/textprocessing/"
# TODO Currently nothing. Should return list of allowed parameters

# 2.2
# GET:  curl "http://localhost:10000/wikispeech/textprocessing/"
# Returns a (bad) error message
# TODO Better message, with suggested usage? Similar to /wikispeech/

# 2.3
# GET:  curl "http://localhost:10000/wikispeech/textprocessing/languages"
# returns list of supported languages

# 2.4
# GET:  curl "http://localhost:10000/wikispeech/textprocessing/languages/sv"
# returns list of defined textprocessors for <lang>

# 2.5
# GET:  curl "http://localhost:10000/wikispeech/textprocessing/?lang=en&input=test."
# returns json markup

# 2.6
# textprocessor can be an argument, returns message if not defined
# GET:  curl "http://localhost:10000/wikispeech/textprocessing/?lang=en&input=test.&textprocessor=undefined"



#3) synthesis api

# GET:  curl "http://localhost:10000/wikispeech/synthesis/"
# GET:  curl "http://localhost:10000/wikispeech/synthesis/voices"
# GET:  curl "http://localhost:10000/wikispeech/synthesis/voices/sv"
# GET:  curl "http://localhost:10000/wikispeech/synthesis/?lang=en&input=test."
# GET:  curl "http://localhost:10000/wikispeech/synthesis/?lang=en&input=test.&voice=cmu-slt-flite"
# GET:  curl "http://localhost:10000/wikispeech/synthesis/?lang=en&input=test.&voice=undefined"


all_done()
