import sys, requests
import json


host = "http://localhost:10000/wikispeech/"

r = requests.options(host)
supported_languages = r.json()


def test_default_settings():
    #1) Test default settings for supported languages
    for lang in supported_languages:
        print("START: %s" % lang)

        # GET:  curl "http://localhost:10000/wikispeech/?lang=en&input=test."
        r = requests.get("%s?lang=%s&input=test." % (host,lang))
        print(r.text)
        print("DONE: %s" % lang)

def test_all_settings():

    #2) Test all settings for supported languages.
    #foreach language
    #foreach textproc_config
    #foreach voice
    #test
    for lang in supported_languages:
        print("START: %s" % lang)
        
        r = requests.get("%stextprocessing/languages/%s" % (host,lang))
        #print(r.url)
        textproc_configs = r.json()

        for textproc_config in textproc_configs:
            print(textproc_config)
            tp_name = textproc_config["name"]

            print("START %s" % tp_name)
            r = requests.get("%stextprocessing/?input=test.&lang=%s&textprocessor=%s" % (host, lang, tp_name))
            tmp = r.json()                             
            #tmp = r.text                             
            print("TP OUTPUT: %s" % tmp)

            r = requests.get("%ssynthesis/voices/%s" % (host,lang))
            voices = r.json()

            for voice in voices:
                print(voice)
                voice_name = voice["name"]
                print("START %s" % voice_name)

                payload = {
                    "input": json.dumps(tmp),
                    "lang": lang,
                    "voice": voice_name
                }

                r = requests.post("%ssynthesis/" % (host), data=payload)
                print(r.url)
                res = r.json()
                print(res)
                print("DONE %s" % voice_name)


            print("DONE %s" % tp_name)
        print("DONE: %s" % lang)

test_default_settings()
test_all_settings()
