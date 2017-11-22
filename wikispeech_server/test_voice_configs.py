import sys
import json
if __name__ == "__main__":
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/..")
    print(sys.path)
    
import wikispeech_server.wikispeech as ws
import wikispeech_server.log as log

log.info("RUNNING VOICE CONFIG TESTS")

host = "http://localhost:10000/"
test_client = ws.app.test_client()


r = test_client.options(host)
api_info = json.loads(r.data.decode('utf-8'))
supported_languages = api_info["GET"]["parameters"]["lang"]["allowed"]


def test_default_settings():
    #1) Test default settings for supported languages
    for lang in supported_languages:
        log.debug("START: %s" % lang)

        # GET:  curl "http://localhost:10000/?lang=en&input=test."
        r = test_client.get("%s?lang=%s&input=test." % (host,lang))
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
        
        r = test_client.get("%stextprocessing/textprocessors/%s" % (host,lang))
        #log.debug(r.url)
        textproc_configs = json.loads(r.data.decode('utf-8'))

        for textproc_config in textproc_configs:
            log.debug(textproc_config)
            tp_name = textproc_config["name"]

            log.debug("START %s" % tp_name)
            url = "%stextprocessing/?input=test.&lang=%s&textprocessor=%s" % (host, lang, tp_name)
            log.debug("url: %s" % url)
            r = test_client.get(url)
            tmp = json.loads(r.data.decode('utf-8'))
            
            #tmp = r.data.decode('utf-8')                             
            log.debug("TP OUTPUT: %s" % tmp)

            url = "%ssynthesis/voices/%s" % (host,lang)
            log.debug("trying url: %s" % url)
            r = test_client.get(url)
            voices = json.loads(r.data.decode('utf-8'))

            for voice in voices:
                log.debug(voice)
                voice_name = voice["name"]
                log.debug("START %s" % voice_name)

                payload = {
                    "input": json.dumps(tmp),
                    "lang": lang,
                    "voice": voice_name,
                    "output_type": "test"
                }

                url = "%ssynthesis/" % (host)
                r = test_client.post(url, data=payload)
                if r.status_code != 200:
                    log.fatal("test call to URL %s failed, server error: %s" % (url, r))
                res = json.loads(r.data.decode('utf-8'))
                log.debug(res)
                log.debug("DONE %s" % voice_name)


            log.debug("DONE %s" % tp_name)
        log.debug("DONE: %s" % lang)

test_default_settings()
test_all_settings()
