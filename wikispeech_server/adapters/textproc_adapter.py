import sys, requests, json, re
import sys, os, re, io

import xml.etree.ElementTree as ET

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
            "input": [{
                    "type": "text",
                    "text": input
                }]
        }
        log.debug(f"text input converted: {params['input']}")
        requrl = f"{url}?input={input}&name={cconfig['name']}&input_type={input_type}"
        r = requests.get(requrl)
    elif input_type == "ssml":
        input_converted = mapSSMLToTextproc(input, lang, cconfig)
        log.debug(f"ssml input converted: {input_converted}")
        params = {
            "name": cconfig["name"],
            "input_type":"tokens",
            "input":input_converted
        }
        #requrl = f"{url}?input={input_converted}&name={cconfig['name']}&input_type={'tokens'}"
        r = requests.post(url, json=params)

    if not r.ok:
        from http.client import responses
        raise Exception(f"Textproc request returned status code {r.status_code} {responses[r.status_code]}")
    
    obj = r.json()
    log.debug("textproc adapter output: %s" % json.dumps(obj, indent=4))
    res = mapFromTextprocUtt(obj)
    log.debug("textproc adapter output converted: %s" % json.dumps(res, indent=4))
    return res

def mapSSMLToTextprocOLD(ssml, lang, tp_config):
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


def mapSSMLToTextproc(ssml_string, lang, tp_config):
    print("textproc_adapter SSML input", ssml_string)
    root = ET.fromstring(ssml_string)

    def extract(node):
        parts = []

        if node.text:
            text = node.text.strip().lstrip()
            if len(text) > 0:
                parts.append({
                    "text": text,
                    "type": "text"
                })
        
        for child in node:
            if child.tag == "sub":
                # Use alias if present, otherwise fallback to inner text
                alias = child.attrib.get("alias")
                if alias:
                    text = child.text.strip().lstrip()
                    parts.append({
                        "text": text,
                        "type": "alias",
                        "alias": alias
                    })
                else:
                    extract(child)
            elif child.tag == "phoneme":
                # Use alias if present, otherwise fallback to inner text
                trans = child.attrib.get("ph")
                if trans:
                    text = child.text.strip().lstrip()
                    parts.append({
                        "text": text,
                        "type": "phonemes",
                        "phonemes": trans
                    })
                else:
                    extract(child)
            elif child.text:
                text = child.text.strip().lstrip()
                if len(text) > 0:
                    parts.append({
                        "text": text,
                        "type": "text"
                    })
            else:
                raise IOException(f"Cannot handle nested input: {child}")

            # Tail text (after child)
            if child.tail:
                text = child.tail.lstrip()
                parts.append({
                    "text": text,
                    "type": "text"
                })

        return parts

    return extract(root)    

# <speak xml:lang="sv" version="1.0" xmlns="http:\\/\\/www.w3.org\\/2001\\/10\\/synthesis" xmlns:xsi="http:\\/\\/www.w3.org\\/2001\\/XMLSchema-instance" xsi:schemalocation="http:\\/\\/www.w3.org\\/2001\\/10\\/synthesis http:\\/\\/www.w3.org\\/TR\\/speech-synthesis\\/synthesis.xsd">
# "All Apologies" hamnade p\\u00e5 plats sju \\u00f6ver de <sub alias="tjugo">
# 20<\\/sub>
#  mest spelade Nirvana-l\\u00e5tarna n\\u00e5gonsin i Storbritannien, vilket var en lista framtagen av Phonographic Performance Limited f\\u00f6r att hedra Cobains <sub alias="femtio">
# 50<\\/sub>
# -\\u00e5rsdag den <sub alias="tjugonde februari tjugo hundra sjutton">
# 20 februari 2017<\\/sub>
# .<\\/speak>
# ",
    
        
    log.debug("MAPPED SSML: %s" % ssml)
    return ssml

# expected output: {"name": "utt1", "paragraphs": [{"name": "par1", "sentences": [{"name": "sent1", "phrases": [{"name": "phrase1", "tokens": [{"name": "token1", "text": "Token1"}, {"name": "token2", "punct": ",", "text": "token2"}]}, {"name": "phrase2", "tokens": [{"name": "token3", "text": "token3"}, {"name": "token4", "punct": ".", "text": "token4"}]}]}, {"name": "sent2", "phrases": [{"name": "phrase3", "tokens": [{"name": "token5", "text": "Token5"}, {"name": "token6", "punct": ".", "text": "token6"}]}]}, {"name": "sent3", "phrases": [{"name": "phrase4", "tokens": [{"name": "token7", "text": "Xxx"}, {"name": "token8", "punct": ".", "text": "yyy"}]}]}]}, {"name": "par2", "sentences": [{"name": "sent4", "phrases": [{"name": "phrase5", "tokens": [{"name": "token9", "punct": ".", "text": "Token9"}]}]}]}]}

def mapFromTextprocUtt(obj):
    tokens = []
    for i, t0 in enumerate(obj["tokens"]):
        words = []
        for w0 in t0["words"]:
            w = { "orth": w0["word"]}
            # flake8: noqa            
            if "prepunct" in w0:
                w["prepunct"] = w0["prepunct"]
            # flake8: noqa            
            if "postpunct" in w0:
                w["postpunct"] = w0["postpunct"]
            words.append(w)
        tok = {
            "name": f"token{i}",
            "input_orth": t0["text"],
            #"orth": t0["input"],
            "words": words
        }
        tokens.append(tok)

    res = {
        "name": "text1",
        "paragraphs": [{
            "name": "par1",
            "sentences": [{
                "name": "sent1",
                "phrases": [{
                    "input_orth": obj["input"],
                    "name": "phrase1",
                    "tokens": tokens
                }]
            }]
        }]
    }
    return res
