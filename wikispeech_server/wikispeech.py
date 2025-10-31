#-*- coding: utf-8 -*-
import sys, os, re, glob
from tempfile import NamedTemporaryFile
#from importlib import import_module
import requests
from flask import Flask, request, json, Response, make_response, render_template, redirect
from flask_cors import CORS

import wikispeech_server.config as config

from wikispeech_server.options import *
import wikispeech_server.adapters.lexicon_client as lexicon_client
import wikispeech_server.log as log
import wikispeech_server.util as util

from wikispeech_server.textprocessor import Textprocessor, TextprocessorException
from wikispeech_server.voice import Voice, VoiceException

import os.path
import datetime
import pytz
from pytz import timezone
import subprocess
import base64

from urllib.parse import quote


###
#change from import to load json, to allow for different voice config files!
from wikispeech_server.voice_config import textprocessor_configs, voice_configs

use_json_conf = False
if config.config.has_option("Voice config", "config_files_location"):
    use_json_conf = True
    #if use_json_conf, the json files defined in *.conf will be loaded, replacing voice_config.py
    
#RUN TEST: set to False if we want textprocessors to load even if there is no corresponding lexicon etc (Kalle 1/6 2021)
run_test = True
if config.config.has_option("Tests", "load_components_on_error"):
    #print(config.config.get("Tests", "load_components_on_error"))
    if config.config.get("Tests", "load_components_on_error") == "True":
        run_test = False

    


#################
#
# Test opusenc before anything else
#
################

log.info("\nOPUSENC\n\nChecking that opusenc is installed on your system..")
retval = os.system('opusenc -V')
if retval != 0:
    os.system("opusenc -V")
    log.error("ERROR: opusenc was not found. You should probably run something like\nsudo apt install opus-tools\n")
    sys.exit(1)
else:
    log.info("opusenc found.\n\nEND OPUSENC\n")



################
#
# Flask app
#
###############

app = Flask(__name__, static_url_path='')
CORS(app)




###############################################################
#
# API
#
# /ping
# /version
# /options
# /languages
# /, /wikispeech
# /textprocessing
# /synthesis



################################################################
#
# /ping
#
# GET:  curl "http://localhost:10000/ping"

@app.route('/ping')
def ping():
    resp = make_response("wikispeech")
    resp.headers["Content-type"] = "text/plain"
    return resp


################################################################
#
# /version
#
# GET:  curl "http://localhost:10000/version"

@app.route('/version')
def version():
    resp = make_response("\n".join(vInfo))
    resp.headers["Content-type"] = "text/plain"
    return resp
    
def versionInfo():
    res = []
    buildInfoFile = "/wikispeech/wikispeech_server/build_info.txt"
    if os.path.isfile(buildInfoFile):
        with open(buildInfoFile) as fp:  
            lines = fp.readlines()
            fp.close()
            for l in lines:
                res.append(l.strip())
                    
    else:
        res.append("Application name: wikispeech")
        res.append("Build timestamp: n/a")
        res.append("Built by: user")

        try:
            tag = subprocess.check_output(["git","describe","--tags"]).decode("utf-8").strip()
            branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode("utf-8").strip()
            log.info(tag)
            log.info(branch)
            res.append( ("Release: %s on branch %s") % (tag, branch) )
        except:
            log.warning("couldn't retrieve git release info: %s" % sys.exc_info()[1])
            res.append("Release: unknown");

    res.append("Started: " + startedAt)
    return res
    


def genStartedAtString():
    from time import strftime, gmtime
    from tzlocal import get_localzone
    local_tz = get_localzone()
    now = datetime.datetime.now()
    if local_tz != None:
        now = now.replace(tzinfo=local_tz)
    now = now.astimezone(pytz.utc)
    return '{:%Y-%m-%d %H:%M:%S %Z}'.format(now)

#These are set when running the server
startedAt = genStartedAtString()
vInfo = versionInfo()



################################################################
#
# /options
#
# GET:  curl "http://localhost:10000/options"
# OPTIONS: http OPTIONS "http://localhost:10000/"



@app.route('/', methods=["OPTIONS"])
def wikispeech_options():

    options = getWikispeechOptions()
    log.debug(options)
    resp = make_response(json.dumps(options))
    resp.headers["Content-type"] = "application/json"
    resp.headers["Allow"] = "OPTIONS, GET, POST, HEAD"
    return resp

@app.route('/options', methods=["GET", "POST"])
def wikispeech_options2():
    options = getWikispeechOptions()
    log.debug(options)
    resp = make_response(json.dumps(options))
    resp.headers["Content-type"] = "application/json"
    resp.headers["Allow"] = "OPTIONS, GET, POST, HEAD"
    return resp

################################################################
#
# /languages
#
# GET:  curl "http://localhost:10000/languages"

@app.route('/languages', methods=["GET"])
def list_languages():
    json_data = json.dumps(getSupportedLanguages())
    return Response(json_data, mimetype='application/json')


################################################################
#
# /default_voices
#
# GET:  curl "http://localhost:10000/default_voices"

@app.route('/default_voices', methods=["GET"])
def list_default_voices():
    json_data = json.dumps(getDefaultVoices())
    return Response(json_data, mimetype='application/json')


################################################################
#
# /, /wikispeech
#
# POST: curl -d "lang=en" -d "input=test." http://localhost:10000/
# GET:  curl "http://localhost:10000/?lang=en&input=test."
# POST: curl -d "lang=en" -d "input=test." http://localhost:10000/wikispeech/
# GET:  curl "http://localhost:10000/wikispeech/?lang=en&input=test."


@app.route('/', methods=["GET", "POST"])
@app.route('/wikispeech', methods=["GET", "POST"])
def wikispeech():
    global hostname

    from urllib.parse import urlparse
    parsed_uri = urlparse(request.url)
    hostname = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)

    # log.debug("request.url: %s" % hostname)
    log.debug("request: %s" % request)
    log.info("request.url: %s" % request.url)
    log.debug("hostname: %s" % hostname)
    if not hostname.endswith("/"):
        hostname = hostname+"/"
    if "wikispeech.morf.se" in hostname: ## HL 20171121: force https for wikispeech.morf.se
        hostname = hostname.replace("http://","https://")
    log.debug("hostname: %s" % hostname)
        
    lang = getParam("lang")
    input = getParam("input")
    input_type = getParam("input_type", "text")
    output_type = getParam("output_type", "json")




    textprocessor_name = getParam("textprocessor", "default_textprocessor")
    voice_name = getParam("voice", "default_voice")



    log.debug("WIKISPEECH CALL - LANG: %s, INPUT_TYPE: %s, OUTPUT_TYPE: %s, INPUT: %s" % (lang, input_type, output_type, input))

    supported_languages = getSupportedLanguages()

    if not lang or not input:
        return render_template("usage.html", server=hostname, languages=supported_languages)

    if lang not in supported_languages:
        return "Language %s not supported. Supported languages are: %s" % (lang, supported_languages)


    if input == "TEST_EXAMPLE":
        return json.dumps(getTestExample(lang))


    if input_type == "ipa":
        if lang == "en":
            xmllang = "en-US"
        else:
            xmllang = lang
        input = """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://www.w3.org/2001/10/synthesis
                   http://www.w3.org/TR/speech-synthesis/synthesis.xsd"
         xml:lang="%s">
    <phoneme alphabet="ipa" ph="%s">%s</phoneme>
</speak>""" % (xmllang, input, "word")
        input_type = "ssml"
    

    if input_type in ["text","ssml"]:
        markup = textproc(lang, textprocessor_name, input, input_type=input_type)
        if type(markup) == type(""):
            log.debug("RETURNING MESSAGE: %s" % markup)
            return markup
    else:
        return "input_type %s not supported" % input_type

    if output_type in ["json", "html"]:
        result = synthesise(lang, voice_name, markup,"markup",output_type, hostname=hostname)
        if type(result) == type(""):
            log.debug("RETURNING MESSAGE: %s" % result)
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

                
        if output_type == "json":
            return Response(json_data, mimetype='application/json')

        elif output_type == "html":
            newtokens = []
            starttime = 0
            for token in result["tokens"]:
                token["starttime"] = starttime
                #T260293
                token["dur"] = token["endtime"]/1000-starttime
                #token["dur"] = token["endtime"]-starttime
                newtokens.append(token)
                starttime = token["endtime"]/1000
                #starttime = token["endtime"]
            
            return render_template("output.html", audio_data=result["audio_data"], tokens=newtokens)


    else:
        return "output_type %s not supported" % output_type




def getSupportedLanguages():
    supported_languages = []
    for lang in textprocSupportedLanguages():
        if lang in synthesisSupportedLanguages():
            supported_languages.append(lang)
    return supported_languages

def getDefaultVoices():
    voices = []
    for lang in getSupportedLanguages():
        textproc = getTextprocessorByName("default_textprocessor", lang)
        voice = getVoiceByName("default_voice", lang)
        voices.append({"lang":lang, "default_textprocessor":textproc["name"], "default_voice":voice["name"]})
    return voices

##############################################
#
# /textprocessing
#
# POST: curl -d "lang=en" -d "input=test." http://localhost:10000/textprocessing/
# GET:  curl "http://localhost:10000/textprocessing/?lang=en&input=test."
#





@app.route('/textprocessing/languages', methods=["GET"])
def list_textprocSupportedLanguages():
    json_data = json.dumps(textprocSupportedLanguages())
    return Response(json_data, mimetype='application/json')

@app.route('/textprocessing/textprocessors', methods=["GET"])
def list_textprocessors():
    """Returns list of loaded textprocessors."""
    t = []
    for tp in textprocessors:
        for tpc in textprocessor_configs:
            if tpc["name"] == tp.name:
                t.append(tpc)
    json_data = json.dumps(t)
    return Response(json_data, mimetype='application/json')

@app.route('/textprocessing/textprocessors/<lang>', methods=["GET"])
def return_tp_configs_by_language(lang):
    json_data = json.dumps(list_tp_configs_by_language(lang))
    return Response(json_data, mimetype='application/json')

def list_tp_configs_by_language(lang):
    l = []
    for tp in textprocessors:
        if tp.lang == lang:
            l.append(tp.config)
    return l

def get_tp_config_by_name(name):
    for tp in textprocessors:
        log.debug("get_tp_config_by_name: %s" % tp)
        log.debug("name: %s, wanted: %s" % (tp.name, name))
        if tp.name == name:
            log.debug("RETURNING: %s" % tp.config)
            return tp.config
    return None



@app.route('/textprocessing/', methods=["OPTIONS"])
def textprocessing_options():

    options = getTextprocessingOptions()
    resp = make_response(json.dumps(options))
    resp.headers["Content-type"] = "application/json"
    resp.headers["Allow"] = "OPTIONS, GET, POST, HEAD"
    return resp



@app.route('/textprocessing/', methods=["GET", "POST"])
def textprocessing():
    lang = getParam("lang")
    textprocessor_name = getParam("textprocessor", "default_textprocessor")
    input_type = getParam("input_type", "text")
    output_type = getParam("output_type", "json")
    input = getParam("input")

    if lang == None or input == None:
        options = getTextprocessingOptions()
        resp = make_response(json.dumps(options))
        resp.headers["Content-type"] = "application/json"
        resp.headers["Allow"] = "OPTIONS, GET, POST, HEAD"
        return resp

    
    if input_type in ["text","ssml"]:
        markup = textproc(lang,textprocessor_name, input, input_type=input_type)
        #If "markup" is a string, just return it, it's an error message to the client.
        #TODO nicer way to handle error messages
        if type(markup) == type(""):
            log.debug("RETURNING MESSAGE: %s" % markup)
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
    for t in textprocessors:
        if t.lang not in supported_languages:
            supported_languages.append(t.lang)
    return supported_languages

def textproc(lang, textprocessor_name, text, input_type="text"):

    

    textprocessor = getTextprocessorByName(textprocessor_name, lang)

    if textprocessor == None:
        #example http://localhost/?lang=sv&input=test&textprocessor=undefined
        return "ERROR: Textprocessor %s not defined for language %s" % (textprocessor_name, lang)
    log.debug("TEXTPROCESSOR: %s" % textprocessor)

    #HB 210128
    #mapper for ssml with ipa 
    if input_type == "ssml" and 'alphabet="ipa"' in text:
        try:
            text = mapIpaInput(text, textprocessor)
        except ValueError as e:
            return "ERROR: %s" % e

    #Loop over the list of components, modifying the utt structure created by the first component
    for component in textprocessor["components"]:

        module_name = component["module"]
        call = component["call"]

        log.debug("MODULE: %s" % module_name)
        log.debug("CALL: %s" % call)


        if "directory" in component:
            if not os.path.isdir(component["directory"]):
                log.fatal("directory %s not found" % component["directory"])
                sys.exit()
            directory = component["directory"]
        else:
            directory = "wikispeech_server"


        mod = import_module(directory, module_name)

        
        #Get the method to call (instead of defining the call in voice_config we could always use the same method name..) 
        process = getattr(mod, call)
        log.debug("PROCESS: %s" % process)

        #TODO clean this up to always use process(utt,lang,component)
        #The first component needs to accept text and return a tokenised utterance (at the moment calls "tokenise" or "marytts_preproc")
        #If this is always true it should be a requirement, now it is just assumed
        if call == "tokenise":
            utt = process(text,lang=lang)
            utt["lang"] = lang
            utt["original_text"] = text
            #Simple mechanism to do only tokenisation
            #Build on this to do partial processing in other ways
            #HB 200217 not used atm but leaving it for now as a reminder
            if getParam("process", "none") == "tokenise":
                return utt

        elif call == "marytts_preproc":
            utt = process(text, lang, component, input_type=input_type)


        #Following the first component, they take and return an utterance
        else:
            utt = process(utt, lang=lang, componentConfig=component)

        log.debug(str(utt))

    return utt


mapper_url = config.config.get("Services", "mapper")
def mapIpaInput(ssml, textprocessor, sampa=None):
    for comp in textprocessor["components"]:
        if "mapper" in comp:
            sampa = comp["mapper"]["from"]
    if not sampa:
        raise ValueError("No mapper defined in voice %s, don't know how to map ipa!" % textprocessor["name"])

    phoneme_elements = re.findall("(<phoneme .+?\">)", ssml)
    for element in phoneme_elements:
        log.debug("Phoneme element: %s" % element)
        alphabet = re.findall("alphabet=\"([^\"]+)\"", element)[0]
        if alphabet == "ipa":        
            ipa_trans = re.findall("ph=\"(.+)\">", element)[0]

            url = mapper_url+"/mapper/map/ipa/%s/%s" % (sampa, quote(ipa_trans))
            r = requests.get(url)
            response = r.text
            try:
                response_json = json.loads(response)
            except:
                raise ValueError(response)       
            sampa_trans = response_json["Result"]



            ssml = re.sub('alphabet="ipa"', 'alphabet="x-sampa"', ssml)        
            ssml = re.sub(ipa_trans, sampa_trans, ssml)
    log.debug("mapIpaInput returns %s" % ssml)
    return ssml




###################################################################################
#
# /synthesis
#

#Example call using HTTPie:
#http 'http://localhost:10000/synthesis/?lang=en&input={ "lang": "en-US", "paragraphs": [ { "sentences": [ { "phrases": [ { "boundary": { "breakindex": "5", "tone": "L-L%" }, "tokens": [ { "token_orth": "test", "words": [ { "accent": "!H*", "g2p_method": "lexicon", "orth": "test", "pos": "", "trans": "t E s t" } ] } ] } ] } ] } ]}'



@app.route('/synthesis/languages', methods=["GET"])
def list_synthesisSupportedLanguages():
    json_data = json.dumps(synthesisSupportedLanguages())
    return Response(json_data, mimetype='application/json')


@app.route('/synthesis/voices', methods=["GET"])
def list_voices():
    """Returns list of loaded voices."""
    v = []
    for voice in voices:
        for vc in voice_configs:
            if vc["name"] == voice.name:
                v.append(vc)
    json_data = json.dumps(v)
    return Response(json_data, mimetype='application/json')

@app.route('/synthesis/voices/<lang>', methods=["GET"])
def return_voices_by_language(lang):
    json_data = json.dumps(list_voices_by_language(lang))
    return Response(json_data, mimetype='application/json')

def list_voices_by_language(lang):
    v = []
    for voice in voices:
        if voice.lang == lang:
            v.append(voice.config)
    return v


def synthesisSupportedLanguages():
    langs = []
    for voice in voices:
        if voice.lang not in langs:
            langs.append(voice.lang)
    return langs



@app.route('/synthesis/', methods=["OPTIONS"])
def synthesis_options():

    options = getSynthesisOptions()
    resp = make_response(json.dumps(options))
    resp.headers["Content-type"] = "application/json"
    resp.headers["Allow"] = "OPTIONS, GET, POST, HEAD"
    return resp




@app.route('/synthesis/', methods=["GET","POST"])
def synthesis():
    hostname = request.url_root

    lang = getParam("lang")
    input = getParam("input")
    voice_name = getParam("voice", "default_voice")
    input_type = getParam("input_type", "markup")
    output_type = getParam("output_type", "json")



    if lang == None or input == None:
        options = getSynthesisOptions()
        resp = make_response(json.dumps(options))
        resp.headers["Content-type"] = "application/json"
        resp.headers["Allow"] = "OPTIONS, GET, POST, HEAD"
        return resp


    if lang not in synthesisSupportedLanguages():
        return "synthesis does not support language %s" % lang

    input = json.loads(input)
    result = synthesise(lang,voice_name,input,input_type,output_type,hostname=hostname)
    #If result is a string, it is an error message to the client.
    #TODO nicer way of dealing with messages
    if type(result) == type(""):
        log.debug("RETURNING MESSAGE: %s" % result)
        return result
    json_data = json.dumps(result)
    return Response(json_data, mimetype='application/json')


def synthesise(lang,voice_name,input,input_type,output_type,hostname="http://localhost/"):

    #TODO? Add a simple transcription input type?
    #if input_type not in ["markup","transcription"]:
    if input_type not in ["markup"]:
        return "Synthesis cannot handle input_type %s" % input_type

    ##if input_type == "transcription":
        

    voice = getVoiceByName(voice_name, lang)
    if voice == None:
        return "ERROR: voice %s not defined for language %s." % (voice_name, lang)



    #Import the defined module and function
    if "directory" in voice:
        if not os.path.isdir(voice["directory"]):
            log.fatal("directory %s not found" % voice["directory"])
            sys.exit()
        directory = voice["directory"]
    else:
        directory = "wikispeech_server"

    #mod = import_module("wikispeech_server."+voice["adapter"])
    #log.debug(str(mod))
    #log.debug(str(dir(mod)))

    mod = import_module(directory, voice["adapter"])

    #This use of getattr makes it possible to define the method to call in the voice_config.
    #Not used now and not sure it will ever be a useful thing to do. Leaving this here anyway just to illustrate that it can be done.
    #These lines could, as they are now, be replaced by
    #(audio_file, output_tokens) = mod.synthesise(lang, voice, input, hostname=hostname)
    
    #method_name =  voice["method_name"]
    method_name = "synthesise"
    process = getattr(mod, method_name)
    log.debug("PROCESS: %s" % process)
    (audio_url_0, output_tokens) = process(lang, voice, input, hostname=hostname)


    #Get audio from synthesiser, convert to opus, save locally, return url
    #TODO return wav url also? Or client's choice?
    #Feb 2020 We're talking now about not returning url but audio data in json instead. So this should change.

    #HB 200325 It's a start.. Works for flite, not for marytts, because the audio_file variable is in fact a url :)
    #So 1) Require adapters to return a local file name 2) convert the file to base64 (or opus if we want to keep it for a while) 3) optionally delete the wav file 4) return data, opus-url or wav-url depending on what was asked for, 5) clean up tmp dir on startup + sometimes (say every 10th call)? 
    #Also remove "hostname" from call to adapter.synthesise, if needed it's better added here

    #HB 200326 Easiest way right now: include base64 encoding in saveAndConvertAudio

    audio_data = ""
    if output_type != "test":
        (audio_file, audio_data) = saveAndConvertAudio(audio_url_0)

    audio_url = "%s%s/%s" % (hostname, "audio", audio_file)
    log.debug("audio_url: %s" % audio_url)

    #T260293 Convert seconds to milliseconds in tokens
    output_tokens = convertTokenTimingsToMilliseconds(output_tokens)


    #T257659 Add voice to output (voice contains language, name, and other info)
    data = {
        "voice":voice,
        "audio": audio_url,
        #"audio":audio_url, #The sound file is no longer returned, deleted after base64 encoding
        "audio_data":audio_data,
        "tokens":output_tokens
    }

    
    return data


def encode_audio(wav_file):
    f=open(wav_file, "rb")
    enc=base64.b64encode(f.read())
    f.close()
    return enc


#T260293
def convertTokenTimingsToMilliseconds(tokens):
    for token in tokens:
        if "endtime" in token:
            token["endtime"] = int(token["endtime"]*1000)
    return tokens


############################################
#
#  serve the audio file if needed (should usually be behind proxy)
from flask import send_from_directory

@app.route('/audio/<path:path>')
def static_proxy_audio(path):
    audio_tmpdir = config.config.get("Audio settings","audio_tmpdir")
    audio_file_name = audio_tmpdir+"/"+path
    log.info("Looking for audio file %s" % audio_file_name)
    # send_static_file will guess the correct MIME type
    #return send_from_directory("tmp", path)
    return send_from_directory(os.getcwd()+"/"+audio_tmpdir, path)

############################################
#
#  serve test file if needed (should usually be behind proxy)

@app.route('/test.html')
@app.route('/wikispeech/test.html')
def static_test():
    log.info("Looking for static file %s" % "test.html")
    #HB this is wrong (won't work on morf)
    #hostname = "http://localhost:10000"
    hostname = request.url_root
    return render_template("test.html", server=hostname)


@app.route('/wikispeech_simple_player.js')
def static_proxy_js():
    filename = "wikispeech_simple_player.js"
    root_dir = os.getcwd()
    log.info("Looking for static file %s/%s" % (root_dir, filename))
    return send_from_directory(root_dir, filename)


@app.route('/workflow_demo/<path:path>')
def static_proxy_workflow(path):
    filename = "workflow_demo/"+path
    root_dir = os.getcwd()
    log.info("Looking for static file %s/%s" % (root_dir, filename))
    return send_from_directory(root_dir, filename)





##############################################
#
#   Connection to lexicon server running on same machine
#   Used in workflow demo. Other uses?

from flask import stream_with_context

@app.route('/lexserver/<path:url>')
def lexserver_proxy(url):
    lexicon_host = config.config.get("Services","lexicon")
    redirect_url = "%s/%s%s" % ((lexicon_host, url, "?" + request.query_string.decode("utf-8") if request.query_string else ""))
    log.info("Lexserver proxy to: %s" % redirect_url)
    req = requests.get(redirect_url, stream = True)
    return Response(stream_with_context(req.iter_content()), content_type = req.headers['content-type'])


###############
#
# Load textprocessors and voices
#
###############


textprocessors = []
def loadTextprocessor(tp_config):
    try:
        log.info("Loading textprocessor %s" % (tp_config["name"]))
        tp = Textprocessor(tp_config, run_test)
        log.info("Done loading textprocessor %s" % (tp_config["name"]))
        textprocessors.append(tp)
    except TextprocessorException as e:
        log.warning("Failed to load textprocessor from %s. Reason:\n%s" % (tp_config,e))
        raise
        
voices = []
def loadVoice(voice_config):
    try:
        log.info("Loading voice %s" % (voice_config["name"]))
        v = Voice(voice_config, run_test)        
        log.info("Done loading voice %s" % (voice_config["name"]))
        voices.append(v)
    except VoiceException as e:
        log.warning("Failed to load voice from %s. Reason:\n%s" % (voice_config,e))
        raise

def loadJsonConfigurationFiles():
    global textprocessor_configs, voice_configs
    textprocessor_configs = []
    voice_configs = []

    cf_dir = "wikispeech_server"
    if config.config.has_option("Voice config", "config_files_location"):
        cf_dir = config.config.get("Voice config", "config_files_location")

    #The testing config file should always be there 
    #config_files = ["voice_config_for_testing.json"]
    #OR maybe it shouldn't??
    config_files = []
    
    if config.config.has_option("Voice config", "config_files"):
        #print(config.config.get("Voice config", "config_files"))
        cfs = config.config.get("Voice config", "config_files").split("\n")
        for cf in cfs:
            if cf not in config_files and cf != "":
                config_files.append(cf)

    for config_file in config_files:
        if os.path.isfile(config_file):
            path = config_file
        elif os.path.isfile("%s/%s" % (cf_dir, config_file)):
            path = "%s/%s" % (cf_dir, config_file)
        else:
            log.fatal("Config file %s or %s not found" % (config_file, "%s/%s" % (cf_dir, config_file)))
            sys.exit()
        with open(path) as json_file:
            log.info("Reading config file: %s" % path)
            json_like = json_file.read()
            json_str = remove_comments(json_like)
            #cf = json.load(json_file)
            cf = json.loads(json_str)
            if "textprocessor_configs" in cf:
                for tconf in cf["textprocessor_configs"]:
                    #Is the tp name already in the list?
                    addTp = True
                    for tc in textprocessor_configs:
                        if tc["name"] == tconf["name"]:
                            log.warning("Textprocessor %s defined more than once: file %s" % (tconf["name"], path))
                            addTp = False
                    if addTp:
                        tconf["config_file"] = path
                        textprocessor_configs.append(tconf)

            if "voice_configs" in cf:
                for vconf in cf["voice_configs"]:
                    #Is the voice name already in the list?
                    addVoice = True
                    for vc in voice_configs:
                        if vc["name"] == vconf["name"]:
                            log.warning("Voice %s defined more than once: file %s" % (vconf["name"], path))
                            addVoice = False
                    if addVoice:
                        vconf["config_file"] = path
                        voice_configs.append(vconf)

def remove_comments(json_like):
    """
    Removes C-style comments from *json_like* and returns the result.  Example::
        >>> test_json = '''\
        {
            "foo": "bar", // This is a single-line comment
            "baz": "blah" /* Multi-line
            Comment */
        }'''
        >>> remove_comments('{"foo":"bar","baz":"blah",}')
        '{\n    "foo":"bar",\n    "baz":"blah"\n}'
    """
    comments_re = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE
    )
    def replacer(match):
        s = match.group(0)
        if s[0] == '/': return ""
        return s
    return comments_re.sub(replacer, json_like)



def getTextprocessorByName(textprocessor_name, lang):        
    tp_configs = list_tp_configs_by_language(lang)
    textprocessor = None
    if textprocessor_name == "default_textprocessor":
        for tp in tp_configs:
            textprocessor = tp
            #break #returns the first tp matching lang
            if "default" in tp and tp["default"] == True:
                return textprocessor # returns the first 'default'.
        #If no 'default', returns first tp matching lang 
        return tp_configs[0]
    else:
        for tp in tp_configs:
            if tp["name"] == textprocessor_name:
                textprocessor = tp
                break #returns the first tp matching name
    return textprocessor


def getVoiceByName(voice_name, lang):
    voices = list_voices_by_language(lang)
    voice = None
    if voice_name == "default_voice":
        for v in voices:
            if "default" in v and v["default"] == True:
                return v # returns the first 'default'.
        #If no 'default', returns first voice matching lang 
        return voices[0]
    else:
        for v in voices:
            if v["name"] == voice_name:
                voice = v
    return voice


    


###################################################################
#
# various stuff
#


def checkInputAndOutputTokens(input_string,output_token_list):
    msgs = []
    for token in output_token_list:
        log.debug(token)
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
                    log.debug("skipping empty output token")
                else:
                    log.debug("%s\t%s" % (input_orth, output_orth))
                    if input_orth != output_orth:
                        output_token_list[j]["orth"] = input_orth
                        msgs.append("REPLACED: %s -> %s" % (output_orth, input_orth))
                    i += 1
                    j += 1
                                
                        
            
    return msgs




def saveAndConvertAudio(audio_url):
    global config


    tmpdir = config.config.get("Audio settings","audio_tmpdir")
    log.debug("TMPDIR: %s" % tmpdir)

    if not os.path.isdir(tmpdir):
        os.system("mkdir -p %s" % tmpdir)
    
    fh = NamedTemporaryFile(mode='w+b', dir=tmpdir, delete=False)
    tmpwav = fh.name  

    log.debug("audio_url:\n%s" % audio_url)
    r = requests.get(audio_url)
    log.debug(r.headers['content-type'])
    
    audio_data = r.content
    
    #fh = NamedTemporaryFile(mode='w+b', dir=tmpdir, delete=False)
    #tmpwav = fh.name    
    
    fh.write(audio_data)
    fh.close()
    
    tmpopus = "%s.opus" % tmpwav

    convertcmd = "opusenc %s %s" % (tmpwav, tmpopus)
    log.debug("convertcmd: %s" % convertcmd)
    if log.log_level != "debug":
        convertcmd = "opusenc --quiet %s %s" % (tmpwav, tmpopus)
    retval = os.system(convertcmd)
    if retval != 0:
        log.error("ERROR: opusenc was not found. You should probably run something like\nsudo apt install opus-tools\n")

    opus_url_suffix = re.sub("^.*/%s/" % tmpdir, "", tmpopus)
    log.debug("opus_url_suffix: %s" % opus_url_suffix)

    return_audio_data = True
    if return_audio_data:
        audio_data = "%s" % encode_audio(tmpopus).decode()
    else:
        audio_data = ""


    #Removing any remaining files in the tmpdir
    #tmpfiles = glob.glob("%s/*" % tmpdir)
    #for f in tmpfiles:
    #    os.unlink(f)

    #HB 210525
    #BUG files dropped under "siege"
    os.unlink(tmpwav)
    #os.unlink(tmpopus)
    

    return (opus_url_suffix, audio_data)


def getTestExample(lang):
    if lang == "en":
        return {"tokens": [["sil", "0.197"], ["this", "0.397"], ["is", "0.531"], ["a", "0.587"], ["test", "0.996"], ["sil", "1.138"]], "audio": "https://morf.se/flite_test/tmp/flite_tmp.wav"}
    elif lang == "hi":
        return {"tokens": [["sil", "0.186"], ["\u0928\u091c\u093c\u0930", "0.599"], ["\u0906\u0924\u093e", "0.905"], ["\u0939\u0948\u0964", "1.134"], ["sil", "1.384"], ["sil", "1.564"], ["\u0907\u0938\u0940", "1.871"], ["\u0915\u093e\u0930\u0923", "2.39"], ["sil", "2.565"]], "audio": "https://morf.se/flite_test/tmp/flite_tmp.wav"}
    else:
        return "No test example found for %s" % lang



def getParam(param,default=None):
    value = None
    log.debug("getParam %s, request.method: %s" % (param, request.method))
    if request.method == "GET":
        value = request.args.get(param)
    elif request.method == "POST":
        #log.debug(request)
        #log.debug(request.form)
        if param in request.form:
            value = request.form[param]
    log.debug("VALUE: %s" % value)
    if value == None:
        value = default
    return value


def import_module(directory, module_name):
    return util.import_module(directory, module_name)

        



#########################
#
# Tests
#
#########################






def test_lexicon_client():
    lexicon = "wikispeech_lexserver_demo:sv"
    sent = "apa hund färöarna"
    trans = {}
    trans["apa"] = '"" A: . p a'
    trans["hund"] = '" h u0 n d'
    trans["färöarna"] = '"" f {: . % r 2: . a . rn a'

    try:
        lexicon_client.loadLexicon(lexicon)
        lex = lexicon_client.getLookupBySentence(sent, lexicon)
        log.debug("LEX: %s" % lex)
    except:
        log.error("Failed to do lexicon lookup.\nError type: %s\nError info:%s" % (sys.exc_info()[0], sys.exc_info()[1]))

        import traceback
        log.debug("Stacktrace:")
        if log.log_level == "debug":
            traceback.print_tb(sys.exc_info()[2])
        log.debug("END stacktrace")

        log.error("lexicon lookup test failure")
        log.error("No running lexserver found at %s" % config.config.get("Services","lexicon"))
        raise
        
    for word in sent.split(" "):
        try:
            if lex[word] != trans[word]:
                log.error("lexicon lookup test failure")
                log.error("word %s, found %s, expected %s" % (word, lex[word], trans[word]))
                raise
        except KeyError:
            log.error("Lexicon lookup test failure: Word %s not found in lexicon %s" % (word, lexicon))
            raise
            
                
    log.debug("SUCCESS: lexicon lookup test")


def test_textproc():
    sent = "apa"
    try:
        #HB 210125
        res = textproc("sv","default_textprocessor", sent)
    except:
        log.error("Failed to do textprocessing.\nError type: %s\nError info:%s" % (sys.exc_info()[0], sys.exc_info()[1]))

        import traceback
        log.debug("Stacktrace:")
        traceback.print_tb(sys.exc_info()[2])
        log.debug("END stacktrace")

        log.error("textprocessing test failure")
        log.error("No running marytts server found at %s" % config.config.get("Services","marytts"))
        raise
        
        
    #TODO Better with exception than return value
    if type(res) == type("") and res.startswith("ERROR:"):
        log.error("Failed to do textprocessing")
        log.error(res)
        log.error("textprocessing test failure")
        raise
        
    log.debug("%s --> %s" % (sent,res))
    log.debug("SUCCESS: textprocessing test")

    
def test_wikispeech():
    sent = "apa"
    trans = {}
    trans["apa"] = '" A: - p a'
    lang = "sv"
    try:
        tmp = textproc(lang,"default_textprocessor", sent)
        res = synthesise(lang,"default_voice",tmp,"markup","json")
    except FileNotFoundError:
        log.error("Failed to do wikispeech test.\nError type: %s\nError info:%s" % (sys.exc_info()[0], sys.exc_info()[1]))

        import traceback
        log.debug("Stacktrace:")
        traceback.print_tb(sys.exc_info()[2])
        log.debug("END stacktrace")

        log.error("wikispeech test failure")
        log.error("Is the audio_tmpdir %s correctly configured?" % config.config.get("Audio settings", "audio_tmpdir"))
        raise
        
    except:
        log.error("Failed to do wikispeech test.\nError type: %s\nError info:%s" % (sys.exc_info()[0], sys.exc_info()[1]))

        import traceback
        log.debug("Stacktrace:")
        traceback.print_tb(sys.exc_info()[2])
        log.debug("END stacktrace")

        log.error("wikispeech test failure")
        log.error("No running marytts server found at %s" % config.config.get("Services","marytts"))
        raise

    #TODO Better with exception than return value
    if type(res) == type("") and res.startswith("No voice available"):
        log.error("Failed to do wikispeech test")
        log.error(res)
        log.error("wikispeech test failure")
        raise
        
    log.debug("%s --> %s" % (sent,res))
    log.debug("SUCCESS: wikispeech test")


def test_config():
    log.debug("\nTEST CONFIG\n")

    log.debug("Testing that audio_tmpdir exists and is writeable")
    try:
        tmpdir = config.config.get("Audio settings","audio_tmpdir")
        log.debug("TMPDIR: %s" % tmpdir)
        if not os.path.isdir(tmpdir):
            os.system("mkdir -p %s" % tmpdir)
        fh = NamedTemporaryFile(mode='w+b', dir=tmpdir, delete=False)
        tmpfile = fh.name        
        fh.write("test".encode("utf-8"))
        fh.close()
    except:
        log.error("audio_tmpdir does not exist or is not writeable")
        raise



    log.debug("Testing to make sure that config file contains url to lexicon server:")
    try:
        assert ( config.config.has_option("Services", "lexicon") == True )
        log.debug("Services|lexicon = %s" % config.config.get("Services", "lexicon"))
        log.debug("ok")
    except:
        log.error("Services|lexicon not found in config file\n")
        raise
    log.debug("\nEND TEST CONFIG\n")
        

if use_json_conf:
    loadJsonConfigurationFiles()
    

if __name__ == '__main__':
    print("use wikispeech-server/bin/wikispeech to run")


