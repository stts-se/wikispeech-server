import sys
import json
import wikispeech_mockup.wikispeech as ws
import wikispeech_mockup.log as log

log.info("RUNNING VOICE CONFIG TESTS")

host = "http://localhost:10000/wikispeech/"
test_client = ws.app.test_client()


r = test_client.options(host)
api_info = json.loads(r.data.decode('utf-8'))
supported_languages = api_info["GET"]["parameters"]["lang"]["allowed"]


def test_default_settings():
    #1) Test default settings for supported languages
    for lang in supported_languages:
        log.debug("START: %s" % lang)

        # GET:  curl "http://localhost:10000/wikispeech/?lang=en&input=test."
        r = test_client.get("%s?XXlang=%s&input=test." % (host,lang))
        log.debug(r.data.decode('utf-8'))
        log.debug("DONE: %s" % lang)

def test_all_settings():

    #2) Test all settings for supported languages.
    #foreach language
    #foreach textproc_config
    #foreach voice
    #test
    for lang in supported_languages:
        log.debug("START: %s" % lang)
        
        r = test_client.get("%stextprocessing/languages/%s" % (host,lang))
        #log.debug(r.url)
        textproc_configs = json.loads(r.data.decode('utf-8'))

        for textproc_config in textproc_configs:
            log.debug(textproc_config)
            tp_name = textproc_config["name"]

            log.debug("START %s" % tp_name)
            r = test_client.get("%stextprocessing/?input=test.&lang=%s&textprocessor=%s" % (host, lang, tp_name))
            tmp = json.loads(r.data.decode('utf-8'))                             
            #tmp = r.data.decode('utf-8')                             
            log.debug("TP OUTPUT: %s" % tmp)

            r = test_client.get("%ssynthesis/voices/%s" % (host,lang))
            voices = json.loads(r.data.decode('utf-8'))

            for voice in voices:
                log.debug(voice)
                voice_name = voice["name"]
                log.debug("START %s" % voice_name)

                payload = {
                    "input": json.dumps(tmp),
                    "lang": lang,
                    "voice": voice_name
                }

                r = test_client.post("%ssynthesis/" % (host), data=payload)
                #log.debug(r.url)
                res = json.loads(r.data.decode('utf-8'))
                log.debug(res)
                log.debug("DONE %s" % voice_name)


            log.debug("DONE %s" % tp_name)
        log.debug("DONE: %s" % lang)

test_default_settings()
test_all_settings()
