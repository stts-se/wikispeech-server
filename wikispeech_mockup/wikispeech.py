#-*- coding: utf-8 -*-
import sys, os, re
from tempfile import NamedTemporaryFile
from importlib import import_module
import requests
from flask import Flask, request, json, Response, make_response, render_template
from flask_cors import CORS

from wikispeech_mockup.voice_config import textprocessor_configs, voices
#HB moved into this file: from wikispeech_mockup.options import *
import wikispeech_mockup.wikilex as wikilex
import wikispeech_mockup.config as config



#################
#
# Test opusenc before anything else
#
################

retval = os.system("opusenc -V")
if retval != 0:
    print("ERROR: opusenc was not found. You should probably run something like\nsudo apt install opus-tools\n")
    sys.exit(1)


################
#
# Flask app
#
###############

app = Flask(__name__)
CORS(app)









################################################################
#
# wikispeech api
#
# POST: curl -d "lang=en" -d "input=test." http://localhost:10000/wikispeech/
# GET:  curl "http://localhost:10000/wikispeech/?lang=en&input=test."


@app.route('/wikispeech/', methods=["OPTIONS"])
def wikispeech_options():

    options = getWikispeechOptions()
    print(options)

    resp = make_response(json.dumps(options))
    resp.headers["Content-type"] = "application/json"
    resp.headers["Allow"] = "OPTIONS, GET, POST, HEAD"
    return resp



@app.route('/wikispeech/languages', methods=["GET"])
def list_languages():
    json_data = json.dumps(getSupportedLanguages())
    return Response(json_data, mimetype='application/json')

@app.route('/wikispeech/', methods=["GET", "POST"])
def wikispeech():
    global hostname


    lang = getParam("lang")
    input_type = getParam("input_type", "text")
    output_type = getParam("output_type", "json")

    #For use with synthesis only
    presynth = getParam("presynth", False)
    if presynth == "True":
        presynth = True
    else:
        presynth = False


    input = getParam("input")

    textprocessor_name = getParam("textprocessor", "default_textprocessor")
    voice_name = getParam("voice", "default_voice")



    print("WIKISPEECH CALL - LANG: %s, INPUT_TYPE: %s, OUTPUT_TYPE: %s, INPUT: %s" % (lang, input_type, output_type, input))

    supported_languages = getSupportedLanguages()
    hostname = request.url_root

    if not lang or not input:
        return render_template("usage.html", server=hostname, languages=supported_languages)
    if lang not in supported_languages:
        return "Language %s not supported. Supported languages are: %s" % (lang, supported_languages)


    if input == "TEST_EXAMPLE":
        return json.dumps(getTestExample(lang))


    if input_type in ["text","ssml"]:
        markup = textproc(lang, textprocessor_name, input, input_type=input_type)
        if type(markup) == type(""):
            print("RETURNING MESSAGE: %s" % markup)
            return markup
    else:
        return "input_type %s not supported" % input_type

    if output_type == "json":
        result = synthesise(lang, voice_name, markup,"markup",output_type, hostname=hostname, presynth=presynth)
        if type(result) == type(""):
            print("RETURNING MESSAGE: %s" % result)
            return result

        #TODO
        #The player being developed at wikimedia depends on the output matching input exactly
        #phabricator T147547 
        #Some special characters, like "—" (em-dash) aren't returned properly by the TTS-server. This breaks the token-to-HTML mapping, since it relies on finding the exact same strings in the HTML as the tokens orth values.
        #Add a test for that here,
        #And then require adapter components to conform to this?
        #how, exactly ...
        msg = checkInputAndOutputTokens(input,result["tokens"])
        if msg:
            result["message"] = msg



        json_data = json.dumps(result)
        return Response(json_data, mimetype='application/json')

    else:
        return "output_type %s not supported" % output_type




def getSupportedLanguages():
    supported_languages = []
    for lang in textprocSupportedLanguages():
        if lang in synthesisSupportedLanguages():
            supported_languages.append(lang)
    return supported_languages




##############################################
#
# textprocessing api
#
# POST: curl -d "lang=en" -d "input=test." http://localhost:10000/textprocessing/
# GET:  curl "http://localhost:10000/textprocessing/?lang=en&input=test."
#





@app.route('/wikispeech/textprocessing/languages', methods=["GET"])
def list_tp_configs():
    json_data = json.dumps(textprocessor_configs)
    return Response(json_data, mimetype='application/json')

@app.route('/wikispeech/textprocessing/languages/<lang>', methods=["GET"])
def return_tp_configs_by_language(lang):
    json_data = json.dumps(list_tp_configs_by_language(lang))
    return Response(json_data, mimetype='application/json')

def list_tp_configs_by_language(lang):
    l = []
    for tp_config in textprocessor_configs:
        if tp_config["lang"] == lang:
            l.append(tp_config)
    return l





@app.route('/wikispeech/textprocessing/', methods=["OPTIONS"])
def textprocessing_options():

    options = getTextprocessingOptions()


    resp = make_response(json.dumps(options))
    resp.headers["Content-type"] = "application/json"
    resp.headers["Allow"] = "OPTIONS, GET, POST, HEAD"
    return resp



@app.route('/wikispeech/textprocessing/', methods=["GET", "POST"])
def textprocessing():
    lang = getParam("lang")
    textprocessor_name = getParam("textprocessor", "default_textprocessor")
    input_type = getParam("input_type", "text")
    output_type = getParam("output_type", "json")
    input = getParam("input")

    if input_type in ["text","ssml"]:
        markup = textproc(lang,textprocessor_name, input, input_type=input_type)
        if type(markup) == type(""):
            print("RETURNING MESSAGE: %s" % markup)
            return markup
    else:
        return "input_type %s not supported" % input_type

    if output_type == "json":
        json_data = json.dumps(markup)
        return Response(json_data, mimetype='application/json')
    else:
        return "output_type %s not supported" % output_type


def textprocSupportedLanguages():
    supported_languages = []
    for t in textprocessor_configs:
        if t["lang"] not in supported_languages:
            supported_languages.append(t["lang"])
    return supported_languages

def textproc(lang, textprocessor_name, text, input_type="text"):

    tp_configs = list_tp_configs_by_language(lang)
    textprocessor = None
    if textprocessor_name == "default_textprocessor":
        for tp in tp_configs:
            if tp["lang"] == lang:
                textprocessor = tp
                break
        if textprocessor == None:
            return "ERROR: No textprocessor available for language %s" % lang
    else:
        for tp in tp_configs:
            if tp["name"] == textprocessor_name:
                textprocessor = tp
                break
        if textprocessor == None:
            #example http://localhost/wikispeech/?lang=sv&input=test&textprocessor=undefined
            return "ERROR: Textprocessor %s not defined for language %s" % (textprocessor_name, lang)


    print("TEXTPROCESSOR: %s" % textprocessor)

    for (module_name,component_name) in textprocessor["components"]:

        print("MODULE: %s" % module_name)
        print("COMPONENT: %s" % component_name)

        #Import the defined module and function
        #mod = import_module(module_name)
        #HB testing
        mod = import_module("wikispeech_mockup."+module_name)
        #print(mod)
        #print(dir(mod))
        process = getattr(mod, component_name)
        print("PROCESS: %s" % process)

        #TODO clean this up to always use process(utt)
        if component_name == "tokenise":
            utt = process(text)
        elif component_name == "marytts_preproc":
            utt = process(lang,text, input_type=input_type)
        else:
            try:
                utt = process(utt)
            except:
                utt = process(lang, utt)
        print(utt)

    return utt





###################################################################################
#
# synthesis api
#
# POST: curl -d "lang=en" -d "input={"s": {"phrase": {"boundary": {"@breakindex": "5", "@tone": "L-L%"}, "t": [{"#text": "test", "@accent": "!H*", "@g2p_method": "lexicon", "@ph": "' t E s t", "@pos": "NN", "syllable": {"@accent": "!H*", "@ph": "t E s t", "@stress": "1", "ph": [{"@p": "t"}, {"@p": "E"}, {"@p": "s"}, {"@p": "t"}]}}, {"#text": ".", "@pos": "."}]}}}" http://localhost:10000/textprocessing/
# GET:  curl 'http://localhost:10000/textprocessing/?lang=en&input={"s": {"phrase": {"boundary": {"@breakindex": "5", "@tone": "L-L%"}, "t": [{"#text": "test", "@accent": "\!H\*", "@g2p_method": "lexicon", "@ph": "\' t E s t", "@pos": "NN", "syllable": {"@accent": "\!H\*", "@ph": "t E s t", "@stress": "1", "ph": [{"@p": "t"}, {"@p": "E"}, {"@p": "s"}, {"@p": "t"}]}}, {"#text": ".", "@pos": "."}]}}}'
#
#
#
#curl  -X POST -H "Content-Type: application/json" -d "lang=en" -d 'input={"s":{"phrase":{"boundary":{"@breakindex":"5","@tone":"L-L%"},"t":[{"#text":"test","@g2p_method":"lexicon","@ph":"\'+t+E+s+t","@pos":"NN","syllable":{"@ph":"t+E+s+t","@stress":"1","ph":[{"@p":"t"},{"@p":"E"},{"@p":"s"},{"@p":"t"}]}},{"#text":".","@pos":"."}]}}}' http://localhost:10000/textprocessing/

#curl -X POST -H "Content-Type: application/json" -d '{"key":"val"}' URL
#curl -X POST -H "Content-Type: application/json" -d "lang=en" --data-binary @test.json http://localhost:10000/synthesis/

#nej ingen av dessa funkar..



@app.route('/wikispeech/synthesis/voices', methods=["GET"])
def list_voices():
    json_data = json.dumps(voices)
    return Response(json_data, mimetype='application/json')

@app.route('/wikispeech/synthesis/voices/<lang>', methods=["GET"])
def return_voices_by_language(lang):
    json_data = json.dumps(list_voices_by_language(lang))
    return Response(json_data, mimetype='application/json')

def list_voices_by_language(lang):
    v = []
    for voice in voices:
        if voice["lang"] == lang:
            v.append(voice)
    return v

def synthesisSupportedLanguages():
    langs = []
    for voice in voices:
        if voice["lang"] not in langs:
            langs.append(voice["lang"])
    return langs
                        


@app.route('/wikispeech/synthesis/', methods=["OPTIONS"])
def synthesis_options():

    options = getSynthesisOptions()


    resp = make_response(json.dumps(options))
    resp.headers["Content-type"] = "application/json"
    resp.headers["Allow"] = "OPTIONS, GET, POST, HEAD"
    return resp




@app.route('/wikispeech/synthesis/', methods=["GET","POST"])
def synthesis():
    hostname = request.url_root

    lang = getParam("lang")
    input = getParam("input")
    voice_name = getParam("voice", "default_voice")
    input_type = getParam("input_type", "markup")
    output_type = getParam("output_type", "json")
    presynth = getParam("presynth", False)
    if presynth == "True":
        presynth = True
    else:
        presynth=False

    #print "SYNTHESIS CALL - LANG: %s, INPUT_TYPE: %s, OUTPUT_TYPE: %s, INPUT: %s" % (lang, input_type, output_type, input)

    if lang not in synthesisSupportedLanguages():
        return "synthesis does not support language %s" % lang

    #The input is a json string, needs to be a python dictionary
    input = json.loads(input)
    result = synthesise(lang,voice_name,input,input_type,output_type,hostname=hostname,presynth=presynth)
    if type(result) == type(""):
        print("RETURNING MESSAGE: %s" % result)
        return result
    json_data = json.dumps(result)
    return Response(json_data, mimetype='application/json')


def synthesise(lang,voice_name,input,input_type,output_type,hostname="http://localhost/", presynth=False):

    #presynth for use with marytts WIKISPEECH_JSON output type
    #presynth = True


    #if input_type not in ["markup","transcription"]:
    if input_type not in ["markup"]:
        return "Synthesis cannot handle input_type %s" % input_type

    ##if input_type == "transcription":
        

    
    voices = list_voices_by_language(lang)
    #print(voices)
    voice = None
    if voice_name == "default_voice":
        if len(voices) > 0:
            voice = voices[0]
        if voice == None:
            return "No voice available for language %s" % lang
    else:
        for v in voices:
            if v["name"] == voice_name:
                voice = v
        if voice == None:
            return "ERROR: voice %s not defined for language %s." % (voice_name, lang)




    #print(voice)

    #Import the defined module and function
    #TODO drop synthesise for voice[function] (?)

    mod = import_module("wikispeech_mockup."+voice["adapter"])
    print(mod)
    print(dir(mod))

    process = getattr(mod, "synthesise")
    
    print("PROCESS: %s" % process)

    #process = getattr(__import__(voice["adapter"]), "synthesise")



    (audio_url, output_tokens) = process(lang, voice, input, presynth=presynth)

    #Get audio from synthesiser, convert to opus, save locally, return url
    #TODO return wav url also? Or client's choice?
    opus_audio = saveAndConvertAudio(audio_url, presynth)
    if "localhost:10000" in hostname:
        hostname = "http://localhost"
    audio_url = "%s/%s/%s" % (hostname,config.config.get("Audio settings","audio_url_prefix"),opus_audio)
    print("audio_url: %s" % audio_url)


    data = {
        "audio":audio_url,
        "tokens":output_tokens
    }

    
    return data




###################################################################
#
# various stuff
#


def checkInputAndOutputTokens(input_string,output_token_list):
    msgs = []
    for token in output_token_list:
        print(token)
        if token["orth"] not in input_string:
            msgs.append("output token \"%s\" not found in input string \"%s\"" % (token["orth"], input_string))

            
    #attempt to correct ...
    if len(msgs) > 0:
        input_string = re.sub(r"\s*([,.?!\"()])\s*",r" \1 ", input_string)
        input_string = re.sub(r"\s+", r" ", input_string)
        input_string = input_string.strip()
        
        input_list = input_string.split(" ")
        output_list = [elem["orth"] for elem in output_token_list if elem["orth"] != ""]
        if len(input_list) != len(output_list):
            msgs.append("WARNING: Unable to correct output token list. Input contains %d tokens, output contains %d non-empty tokens." % (len(input_list), len(output_list)))
            msgs.append("input token list : %s" % input_list)
            msgs.append("output token list: %s" % output_list)
        else:
            i = 0
            j = 0
            while i < len(input_list) and j < len(output_token_list):
                input_orth = input_list[i]
                output_orth = output_token_list[j]["orth"]
                #output_orth = output_list[i]
                if output_orth == "":
                    j += 1
                    print("skipping empty output token")
                else:
                    print("%s\t%s" % (input_orth, output_orth))
                    if input_orth != output_orth:
                        output_token_list[j]["orth"] = input_orth
                        msgs.append("REPLACED: %s -> %s" % (output_orth, input_orth))
                    i += 1
                    j += 1
                                
                        
            
    return msgs




def saveAndConvertAudio(audio_url,presynth=False):
    global config

    print("PRESYNTH: %s, type: %s" % (presynth, type(presynth)) )

    tmpdir = config.config.get("Audio settings","audio_tmpdir")
    print("TMPDIR: %s" % tmpdir)
    
    fh = NamedTemporaryFile(mode='w+b', dir=tmpdir, delete=False)
    tmpwav = fh.name    
    
    if presynth:
        fh.close()
        #The "url" is actually a filename at this point
        cmd = "mv %s %s" % (audio_url, tmpwav)
        print(cmd)
        os.system(cmd)

    else:

        print("audio_url:\n%s" % audio_url)
        r = requests.get(audio_url)
        print(r.headers['content-type'])

        audio_data = r.content

        fh = NamedTemporaryFile(mode='w+b', dir=tmpdir, delete=False)
        tmpwav = fh.name    

        fh.write(audio_data)
        fh.close()

    #tmpwav is now the synthesised wav file
    #tmpopus = "%s/%s.opus" % (tmpdir, tmpfilename)
    tmpopus = "%s.opus" % tmpwav

    convertcmd = "opusenc %s %s" % (tmpwav, tmpopus)
    print("convertcmd: %s" % convertcmd)
    os.system(convertcmd)

    #remove everything before the tmpdir, to build the external url
    #HB problem with wikimedia usage?
    #opus_url_suffix = re.sub("^.*/%s/" % tmpdir, "%s/" % tmpdir, tmpopus)
    opus_url_suffix = re.sub("^.*/%s/" % tmpdir, "", tmpopus)
    print("opus_url_suffix: %s" % opus_url_suffix)

    #return tmpopus
    return opus_url_suffix


def getTestExample(lang):
    if lang == "en":
        return {"tokens": [["sil", "0.197"], ["this", "0.397"], ["is", "0.531"], ["a", "0.587"], ["test", "0.996"], ["sil", "1.138"]], "audio": "https://morf.se/flite_test/tmp/flite_tmp.wav"}
    elif lang == "hi":
        return {"tokens": [["sil", "0.186"], ["\u0928\u091c\u093c\u0930", "0.599"], ["\u0906\u0924\u093e", "0.905"], ["\u0939\u0948\u0964", "1.134"], ["sil", "1.384"], ["sil", "1.564"], ["\u0907\u0938\u0940", "1.871"], ["\u0915\u093e\u0930\u0923", "2.39"], ["sil", "2.565"]], "audio": "https://morf.se/flite_test/tmp/flite_tmp.wav"}
    else:
        return "No test example found for %s" % lang



def getParam(param,default=None):
    value = None
    print("getParam %s, request.method: %s" % (param, request.method))
    if request.method == "GET":
        value = request.args.get(param)
    elif request.method == "POST":
        #print(request)
        #print(request.form)
        if param in request.form:
            value = request.form[param]
    print("VALUE: %s" % value)
    if value == None:
        value = default
    return value



####################
# OPTIONS
#
####################


def getWikispeechOptions():

    wikispeech_options = {
        "GET": {
            "description": "Get speech from text",
            "parameters": {
                "input": {
                    "type": "string",
                    "description": "The text to be synthesised",
                    "required": True,
                    "default": None
                },
            "lang": {
                "type": "string",
                "description": "ISO 639-1 two-letter code for textprocessing and synthesis language",
                "required": True,
                "allowed": getSupportedLanguages(),
                "default": None
            },
            "textprocessor": {
                "type": "string",
                "description": "name of a defined wikispeech textprocessor for this language",
                "required": False,
                "default": "The default textprocessor for this language"
            },
            "voice": {
                "type": "string",
                "description": "name of a defined wikispeech voice for this language",
                "required": False,
                "default": "The default voice for this language"
            },
            "input_type": {
                "type": "string",
                "description": "the type of the input, for instance with or without markup",
                "required": False,
                "allowed": ["text", "ssml"],
                "default": "text"
            },
            "output_type": {
                "type": "string",
                "description": "the type of the output, for instance with or without timing information",
                "required": False,
                "allowed": "json",
                "default": "json"
            }                
        },
        "examples": [
            {
                "input": "Det här är ett test",
                "lang": "sv"
            },
            {
                "input": "Det här är ett test",
                "lang": "sv",
                "textprocessor": "wikitextproc_sv",
                "voice": "stts_sv_nst-hsmm",
                "input_type": "text",
                "output_type": "json"
            }
        ]
            
        }
    }
                

    #Parameters for POST are the same as for GET. If they're not, "POST" needs to be defined separately!
    wikispeech_options["POST"] = wikispeech_options["GET"]
    return wikispeech_options





def getTextprocessingOptions():

    options = {
        "GET": {
            "description": "Get markup from text",
            "parameters": {
                "input": {
                    "type": "string",
                    "description": "The text to be processed",
                    "required": True,
                    "default": None
                },
                "lang": {
                    "type": "string",
                    "description": "ISO 639-1 two-letter code for textprocessing language",
                    "required": True,
                    "allowed": textprocSupportedLanguages(),
                    "default": None
                },
                "textprocessor": {
                    "type": "string",
                    "description": "name of a defined wikispeech textprocessor for this language",
                    "required": False,
                    "default": "The default textprocessor for this language"
                },
                "input_type": {
                    "type": "string",
                    "description": "the type of the input, for instance with or without markup",
                    "required": False,
                    "allowed": ["text", "ssml"],
                    "default": "text"
                },
                "output_type": {
                    "type": "string",
                    "description": "the type of the output. Only json implemented so meaningless at the moment",
                    "required": False,
                    "allowed": "json",
                    "default": "json"
                }                
            },
            "examples": [
                {
                    "input": "Det här är ett test",
                    "lang": "sv"
                },
                {
                    "input": "Det här är ett test",
                    "lang": "sv",
                    "textprocessor": "wikitextproc_sv",
                    "input_type": "text",
                    "output_type": "json"
                }
            ]
            
        }
    }
                

    #Parameters for POST are the same as for GET. If they're not, "POST" needs to be defined separately!
    options["POST"] = options["GET"]

    return options



def getSynthesisOptions():

    options = {
        "GET": {
            "description": "Get speech from markup",
            "parameters": {
                "input": {
                    "type": "string",
                    "description": "The markup to be synthesised",
                    "required": True,
                    "default": None
                },
                "lang": {
                    "type": "string",
                    "description": "ISO 639-1 two-letter code for synthesis language",
                    "required": True,
                    "allowed": synthesisSupportedLanguages(),
                    "default": None
                },
                "voice": {
                    "type": "string",
                    "description": "name of a defined wikispeech voice for this language",
                    "required": False,
                    "default": "The default voice for this language"
                },
                "input_type": {
                    "type": "string",
                    "description": "the type of the input. Only 'markup' implemented, so currently meaningless",
                    "required": False,
                    "allowed": "markup",
                    "default": "markup"
                },
                "output_type": {
                    "type": "string",
                    "description": "the type of the output, for instance with or without timing information",
                    "required": False,
                    "allowed": "json",
                    "default": "json"
                }                
            },
            "examples": [
                {
                    "input": {"children": [{"children": [{"children": [{"children": [{"accent": "!H*", "children": [{"accent": "!H*", "children": [{"p": "t", "tag": "ph"}, {"p": "E", "tag": "ph"}, {"p": "s", "tag": "ph"}, {"p": "t", "tag": "ph"}], "ph": "t E s t", "stress": "1", "tag": "syllable"}], "g2p_method": "lexicon", "ph": "' t E s t", "pos": "NN", "tag": "t", "text": "test"}, {"pos": ".", "tag": "t", "text": "."}, {"breakindex": "5", "tag": "boundary", "tone": "L-L%"}], "tag": "phrase"}], "tag": "s"}], "tag": "p"}], "tag": "utt"},
                    "lang": "sv"
                },
                {
                    "input": {"children": [{"children": [{"children": [{"children": [{"accent": "!H*", "children": [{"accent": "!H*", "children": [{"p": "t", "tag": "ph"}, {"p": "E", "tag": "ph"}, {"p": "s", "tag": "ph"}, {"p": "t", "tag": "ph"}], "ph": "t E s t", "stress": "1", "tag": "syllable"}], "g2p_method": "lexicon", "ph": "' t E s t", "pos": "NN", "tag": "t", "text": "test"}, {"pos": ".", "tag": "t", "text": "."}, {"breakindex": "5", "tag": "boundary", "tone": "L-L%"}], "tag": "phrase"}], "tag": "s"}], "tag": "p"}], "tag": "utt"},
                    "lang": "sv",
                    "voice": "stts_sv_nst-hsmm",
                    "input_type": "markup",
                    "output_type": "json"
                }
            ]
            
        }
    }
                

    #Parameters for POST are the same as for GET. If they're not, "POST" needs to be defined separately!
    options["POST"] = options["GET"]

    return options




#########################
#
# Tests
#
#########################






def test_wikilex():
    sent = "apa hund färöarna"
    trans = {}
    trans["apa"] = '"" A: . p a'
    trans["hund"] = '" h u0 n d'
    trans["färöarna"] = '"" f {: . % r 2: . a . rn a'

    try:
        lex = wikilex.getLookupBySentence("sv", sent)
        print("LEX: %s" % lex)
    except:
        print("Failed to do lexicon lookup.\nError type: %s\nError info:%s" % (sys.exc_info()[0], sys.exc_info()[1]))

        import traceback
        print("Stacktrace:")
        traceback.print_tb(sys.exc_info()[2])
        print("END stacktrace")

        print("ERROR: lexicon lookup test failure")
        print("Is the lexserver running?")
        sys.exit()
        
    for word in sent.split(" "):
        try:
            if lex[word] != trans[word]:
                print("ERROR: lexicon lookup test failure")
                print("ERROR: word %s, found %s, expected %s" % (word, lex[word], trans[word]))
                sys.exit()
        except KeyError:
            print("ERROR: lexicon lookup test failure")
            print("ERROR: word %s not found, expected %s" % (word, trans[word]))
            sys.exit()
            
                
    print("SUCCESS: lexicon lookup test")


def test_textproc():
    sent = "apa"
    trans = {}
    trans["apa"] = '" A: - p a'
    try:
        res = textproc("sv","default_textprocessor", sent)
    except:
        print("Failed to do textprocessing.\nError type: %s\nError info:%s" % (sys.exc_info()[0], sys.exc_info()[1]))

        import traceback
        print("Stacktrace:")
        traceback.print_tb(sys.exc_info()[2])
        print("END stacktrace")

        print("ERROR: textprocessing test failure")
        print("Is the marytts server running?")
        sys.exit()
        
        
    #TODO Better with exception than return value
    if type(res) == type("") and res.startswith("ERROR:"):
        print("Failed to do textprocessing")
        print(res)
        print("ERROR: textprocessing test failure")
        sys.exit()
        
    print("%s --> %s" % (sent,res))
    print("SUCCESS: textprocessing test")

    
def test_wikispeech():
    sent = "apa"
    trans = {}
    trans["apa"] = '" A: - p a'
    lang = "sv"
    try:
        tmp = textproc(lang,"default_textprocessor", sent)
        res = synthesise(lang,"default_voice",tmp,"markup","json")
    except FileNotFoundError:
        print("Failed to do wikispeech test.\nError type: %s\nError info:%s" % (sys.exc_info()[0], sys.exc_info()[1]))

        import traceback
        print("Stacktrace:")
        traceback.print_tb(sys.exc_info()[2])
        print("END stacktrace")

        print("ERROR: wikispeech test failure")
        print("Is the audio_tmpdir %s correctly configured?" % config.config.get("Audio settings", "audio_tmpdir"))
        sys.exit()
        
    except:
        print("Failed to do wikispeech test.\nError type: %s\nError info:%s" % (sys.exc_info()[0], sys.exc_info()[1]))

        import traceback
        print("Stacktrace:")
        traceback.print_tb(sys.exc_info()[2])
        print("END stacktrace")

        print("ERROR: wikispeech test failure")
        print("Is the marytts server running?")
        sys.exit()

    #TODO Better with exception than return value
    if type(res) == type("") and res.startswith("No voice available"):
        print("Failed to do wikispeech test")
        print(res)
        print("ERROR: wikispeech test failure")
        sys.exit()
        
    print("%s --> %s" % (sent,res))
    print("SUCCESS: wikispeech test")


if __name__ == '__main__':



    print("RUNNING SELF-TESTS...")
    test_wikilex()
    test_textproc()
    test_wikispeech()
    print("ALL SELF-TESTS RUN SUCCESSFULLY")

    app.run(host='0.0.0.0', port=10000, debug=True, threaded=True)