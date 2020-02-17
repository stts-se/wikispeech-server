import sys, os, re, io, requests

if __name__ == "__main__":
    sys.path.append(".")

import wikispeech_server.log as log
import wikispeech_server.config as config


def synthesise(lang, voice, utt, hostname=None, nnmnkwii_url="http://localhost:8484"):
    #convert utt to htslabel
    htslabfile = utt2htslabel(utt)
    log.debug(htslabfile)

    tmpdir = config.config.get("Audio settings","audio_tmpdir")
    #write lab to tmpfile

    #send htslabel to nnmnkwii server
    res = requests.get("%s/synth?lab=%s" % (nnmnkwii_url, htslabfile))
    log.debug(res.url)
    wavfile = res.json()["wavfile"]

    retwavfile = "%s/%s" % (tmpdir, "nnmnkwii.wav")
    os.system("mv %s %s" % (wavfile, retwavfile))
    
    #return wavfile name and tokens with timing
    return ("http://localhost:10000/audio/nnmnkwii.wav", [])


                       
def utt2htslabel(utt):
    tlist = []
    for token in utt["paragraphs"][0]["sentences"][0]["phrases"][0]["tokens"]:
        tlist.append(token["words"][0]["trans"])
    tstring = " # ".join(tlist)
    cmd = "cd ~/git/simple-labels/; echo \"%s\" | python3 simplelabel.py sv | perl scripts/phone2state.pl > /tmp/apa.lab" % (tstring)
    print(cmd)
    os.system(cmd)
    return "/tmp/apa.lab"

    
        
if __name__ == "__main__":

    input = {
        "lang": "sv",
        "original_text": "2 babian lejon",
        "paragraphs": [
            {
                "sentences": [
                    {
                        "phrases": [
                            {
                                "tokens": [
                                    {
                                        "token_orth": "2",
                                        "words": [
                                            {
                                                "orth": "2",
                                                "trans": "t v o: 1"
                                            }
                                        ]
                                    },
                                    {
                                        "token_orth": "babian",
                                        "words": [
                                            {
                                                "orth": "babian",
                                                "trans": "b a 0 . b I 0 . A: n 1"
                                            }
                                        ]
                                    },
                                    {
                                        "token_orth": "lejon",
                                        "words": [
                                            {
                                                "orth": "lejon",
                                                "trans": "l E 2 . j O n 0"
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }




    lang = "sv"
    voice = "new_sv_test"
    log.log_level = "debug"
    nnmnkwii_url = "http://localhost:8484"
    
    (audio_url, tokens) = synthesise(lang, voice, input, nnmnkwii_url=nnmnkwii_url)
    log.debug("AUDIO URL: %s" % audio_url)
    log.debug("TOKENS: %s" % tokens)
