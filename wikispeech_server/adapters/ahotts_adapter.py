#One simple possible wav of connecting to ahotts
#Better to use the ahotts_server
#Get timing of each word?


import os, re, sys

if __name__ == "__main__":
    sys.path.append(".")

import wikispeech_server.log as log
import wikispeech_server.config as config

cwdir = os.getcwd()
tmpdir = config.config.get("Audio settings","audio_tmpdir")
wavfile_name = "ahotts_out.wav"


def synthesise(lang, voice, utterance, presynth=False, hostname=None):
    log.info("Utterance: %s" % utterance)
    words = get_orth(utterance)
    log.info("Words: %s" % words)
    ahotts_command = "cd ~/ahotts-code/bin; echo \"%s\" > input.txt; ./tts; mv Output.wav %s/%s/%s" % (" ".join(words), cwdir, tmpdir, wavfile_name)
    log.info("Ahotts command: %s" % ahotts_command)
    os.system(ahotts_command)

    audio_url = "%s%s/%s" % (hostname, "audio",wavfile_name)
    tokens = []
    for word in words:
        tokens.append({"orth":word, "endtime":0})
    return (audio_url, tokens)



def get_orth(utterance):
    orth_list = []
    paragraphs = utterance["paragraphs"]
    for paragraph in paragraphs:
        sentences = paragraph["sentences"]
        for sentence in sentences:
            phrases = sentence["phrases"]
            for phrase in phrases:
                tokens = phrase["tokens"]
                for token in tokens:
                    words = token["words"]
                    for word in words:
                        orth_list.append(word["orth"])
    return orth_list




if __name__ == "__main__":
    input = {
        "lang": "eu",
        "paragraphs": [
            {
                "sentences": [
                    {
                        "phrases": [
                            {
                                "tokens": [
                                    {
                                        "words": [
                                            {
                                                "orth": "test",
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
    

    lang = "eu"
    log.log_level = "debug"
    voice = "ahotts"
    
    (audio_url, tokens) = synthesise(lang, voice, input)
    log.debug("AUDIO URL: %s" % audio_url)
    log.debug("TOKENS: %s" % tokens)
