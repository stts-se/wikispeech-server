import sys, requests, json, re
import sys, os, re, io


if __name__ == "__main__":
    sys.path.append(".")

import wikispeech_server.log as log
import wikispeech_server.config as config
from wikispeech_server.voice import VoiceException

textproc_url = config.config.get("Services", "textproc")

from urllib.parse import quote

def textproc(lang, cconfig, input, input_type="text"):
    url = textproc_url + "/process_utt"
    log.info(f"textproc adapter input {cconfig} {input} / {input_type}")
    # tokens = utt2textproc(input,lang,voice_config)
    params = {}
    if input_type == "text":
        params = {
            "name": cconfig["name"],
            "input_type":input_type,
            "input":input,
        }
        requrl = f"{url}?input={input}&name={cconfig['name']}&input_type={input_type}"
    elif input_type == "ssml":
        input_converted = mapSsmlTranscriptionsToTextproc(input, lang, cconfig)
        params = {
            "name": cconfig["name"],
            "input_type":"tokens",
            "input":input_converted,
        }
        requrl = f"{url}?input={input_converted}&name={cconfig['name']}&input_type={'tokens'}"

    # TODO: should be post
    r = requests.get(requrl)
    #r = requests.post(url, params=params)
    if not r.ok:
        from http.client import responses
        raise Exception(f"Textproc request returned status code {r.status_code} {responses[r.status_code]}")
    
    obj = r.json()
    log.debug("textproc adapter output: %s" % obj)
    res = mapFromTextprocUtt(obj)
    log.debug("textproc adapter output converted: %s" % res)
    return res

def mapSsmlTranscriptionsToTextproc(ssml, lang, tp_config):
    #.+? means shortest match
    phoneme_elements = re.findall("(<phoneme .+?\">)", ssml)
    for element in phoneme_elements:
        log.debug(element)
        
        trans = re.findall("ph=\"(.+)\">", element)[0]
        log.debug("trans: %s" % trans)
        trans = trans.replace("\"", "&quot;")
        trans = trans.replace("<", "&lt;")
        log.debug("trans(2): %s" % trans)

        ssml = re.sub(trans, trans, ssml)

    log.debug("MAPPED SSML: %s" % ssml)
    return ssml

# expected output: {"name": "utt1", "paragraphs": [{"name": "par1", "sentences": [{"name": "sent1", "phrases": [{"name": "phrase1", "tokens": [{"name": "token1", "text": "Token1"}, {"name": "token2", "punct": ",", "text": "token2"}]}, {"name": "phrase2", "tokens": [{"name": "token3", "text": "token3"}, {"name": "token4", "punct": ".", "text": "token4"}]}]}, {"name": "sent2", "phrases": [{"name": "phrase3", "tokens": [{"name": "token5", "text": "Token5"}, {"name": "token6", "punct": ".", "text": "token6"}]}]}, {"name": "sent3", "phrases": [{"name": "phrase4", "tokens": [{"name": "token7", "text": "Xxx"}, {"name": "token8", "punct": ".", "text": "yyy"}]}]}]}, {"name": "par2", "sentences": [{"name": "sent4", "phrases": [{"name": "phrase5", "tokens": [{"name": "token9", "punct": ".", "text": "Token9"}]}]}]}]}

def mapFromTextprocUtt(obj):
    tokens = []
    for i, t0 in enumerate(obj["tokens"]):
        tok = {
            "name": f"token{i}",
            "orth": t0["input"],
            "words": [{
                "orth": t0["converted"]
            }]
        }
        # flake8: noqa            
        if "punct" in t0:
            tok["punct"]: t0["punct"]
        tokens.append(tok)

    res = {
        "name": "text1",
        "paragraphs": [{
            "name": "par1",
            "sentences": [{
                "name": "sent1",
                "phrases": [{
                    "name": "phrase1",
                    "tokens": tokens
                }]
            }]
        }]
    }
    return res
