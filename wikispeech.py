#-*- coding: utf-8 -*-
import sys
from importlib import import_module
import requests
from flask import Flask, request, json, Response
from flask.ext.cors import CORS

from voice_config import textprocessor_configs, voices




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
    return json.dumps(getSupportedLanguages())



@app.route('/wikispeech/', methods=["GET", "POST"])
def wikispeech():

    lang = getParam("lang")
    input_type = getParam("input_type", "text")
    output_type = getParam("output_type", "json")
    input = getParam("input")

    textprocessor_name = getParam("textprocessor", "default_textprocessor")
    voice_name = getParam("voice", "default_voice")



    print("WIKISPEECH CALL - LANG: %s, INPUT_TYPE: %s, OUTPUT_TYPE: %s, INPUT: %s" % (lang, input_type, output_type, input))

    supported_languages = getSupportedLanguages()
    if not lang or not input:
        return getUsageText(supported_languages)
    if lang not in supported_languages:
        return "Language %s not supported. Supported languages are: %s" % (lang, supported_languages)


    if input == "TEST_EXAMPLE":
        return json.dumps(getTestExample(lang))


    if input_type == "text":
        markup = textproc(lang, textprocessor_name, input)
    else:
        return "input_type %s not supported" % input_type

    if output_type == "json":
        json_data = json.dumps(synthesise(lang, voice_name, markup,"markup",output_type))
        return Response(json_data, mimetype='application/json')

    else:
        return "output_type %s not supported" % output_type


def getUsageText(supported_languages):
    text = """

USAGE: wikispeech/?lang=LANG&input=TEXT
<br>
Supported languages are: %s
<br>
EXAMPLE: <a href='http://localhost/wikispeech/?lang=sv&input=Det här är ett test'>http://localhost/wikispeech/?lang=sv&input=Det här är ett test</a>
<hr>
Other things to try:
<br>
<a href='http://localhost/wikispeech/textprocessing/languages'>http://localhost/wikispeech/textprocessing/languages</a>
<br>
<a href='http://localhost/wikispeech/textprocessing/languages/sv'>http://localhost/wikispeech/textprocessing/languages/sv</a>
<br>
<a href='http://localhost/wikispeech/synthesis/voices'>http://localhost/wikispeech/synthesis/voices</a>
<br>
<a href='http://localhost/wikispeech/synthesis/voices/sv'>http://localhost/wikispeech/synthesis/voices/sv</a>
<br>

""" % (supported_languages)
    return text



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

@app.route('/wikispeech/textprocessing/', methods=["GET", "POST"])
def textprocessing():
    lang = getParam("lang")
    textprocessor_name = getParam("textprocessor", "default_textprocessor")
    input_type = getParam("input_type", "text")
    output_type = getParam("output_type", "json")
    input = getParam("input")

    json_data = json.dumps(textproc(lang,textprocessor_name, input))
    return Response(json_data, mimetype='application/json')


def textprocSupportedLanguages():
    supported_languages = []
    for t in textprocessor_configs:
        if t["lang"] not in supported_languages:
            supported_languages.append(t["lang"])
    return supported_languages

def textproc(lang, textprocessor_name, text):

    tp_configs = list_tp_configs_by_language(lang)
    textprocessor = None
    if textprocessor_name == "default_textprocessor":
        for tp in tp_configs:
            if tp["lang"] == lang:
                textprocessor = tp
                break
        if textprocessor == None:
            return "No textprocessor available for language %s" % lang
    else:
        for tp in tp_configs:
            if tp["name"] == textprocessor_name:
                textprocessor = tp
                break
        if textprocessor == None:
            #TODO this doesn't return to browser when called from http://localhost/wikispeech
            return "ERROR: Textprocessor %s not defined for language %s" % (textprocessor_name, lang)


    print("TEXTPROCESSOR: %s" % textprocessor)

    for (module_name,component_name) in textprocessor["components"]:

        print("MODULE: %s" % module_name)
        print("COMPONENT: %s" % component_name)

        #Import the defined module and function
        mod = import_module(module_name)
        #print(mod)
        #print(dir(mod))
        process = getattr(mod, component_name)
        print("PROCESS: %s" % process)

        #TODO clean this up to always use process(utt)
        if component_name == "tokenise":
            utt = process(text)
        elif component_name == "marytts_preproc":
            utt = process(lang,text)
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
                        


@app.route('/wikispeech/synthesis/', methods=["GET","POST"])
def synthesis():

    lang = getParam("lang")
    input = getParam("input")
    voice_name = getParam("voice", "default_voice")
    input_type = getParam("input_type", "markup")
    output_type = getParam("output_type", "json")

    #print "SYNTHESIS CALL - LANG: %s, INPUT_TYPE: %s, OUTPUT_TYPE: %s, INPUT: %s" % (lang, input_type, output_type, input)

    if lang not in synthesisSupportedLanguages():
        return "synthesis does not support language %s" % lang

    #The input is a json string, needs to be a python dictionary
    input = json.loads(input)
    json_data = json.dumps(synthesise(lang,voice_name,input,input_type,output_type))
    return Response(json_data, mimetype='application/json')


def synthesise(lang,voice_name,input,input_type,output_type):
    if input_type != "markup":
        return "Synthesis cannot handle input_type %s" % input_type


    
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

    mod = import_module(voice["adapter"])
    print(mod)
    print(dir(mod))
    process = getattr(mod, "synthesise")
    print("PROCESS: %s" % process)

    #process = getattr(__import__(voice["adapter"]), "synthesise")



    (audio_url, output_tokens) = process(lang, voice, input)
    data = {
        "audio":audio_url,
        "tokens":output_tokens
    }

    return data




###################################################################
#
# various stuff
#

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


def test_wikilex():
    sent = "apa"
    trans = {}
    trans["apa"] = '" A: - p a'
    import wikilex
    lex = wikilex.getLookupBySentence("sv", sent)
    for word in sent.split(" "):
        if lex[word] != trans[word]:
            print("ERROR: word %s, found %s, expected %s" % (word, lex[word], trans[word]))
            sys.exit()


def test_textproc():
    sent = "apa"
    trans = {}
    trans["apa"] = '" A: - p a'
    res = textproc("sv","default_textprocessor", sent)
    print("%s --> %s" % (sent,res))

def test_wikispeech():
    sent = "apa"
    trans = {}
    trans["apa"] = '" A: - p a'
    lang = "sv"
    tmp = textproc(lang,"default_textprocessor", sent)
    res = synthesise(lang,"default_voice",tmp,"markup","json")
    print("%s --> %s" % (sent,res))


if __name__ == '__main__':


    print("RUNNING SELF-TESTS...")
    test_wikilex()
    test_textproc()
    test_wikispeech()
    print("ALL SELF-TESTS RUN SUCCESSFULLY")

    app.run(port=10000, debug=True)
