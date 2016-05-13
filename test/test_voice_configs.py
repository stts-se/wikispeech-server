import sys, requests

r = requests.options("http://localhost:10000/wikispeech/")
supported_languages = r.json()
for lang in supported_languages:
    print("START: %s" % lang)

    # GET:  curl "http://localhost:10000/wikispeech/?lang=en&input=test."
    r = requests.get("http://localhost:10000/wikispeech/?lang=%s&input=test." % lang)
    print(r.text)
    print("DONE: %s" % lang)
