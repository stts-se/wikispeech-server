import sys, requests, json, re
import sys, os, re, io


if __name__ == "__main__":
    sys.path.append(".")

import wikispeech_server.log as log
import wikispeech_server.config as config
from wikispeech_server.voice import VoiceException

mapper_url = config.config.get("Services", "mapper")
piper_url = config.config.get("Services", "piper")

from urllib.parse import quote

def testVoice(voice_config):
    piper_url = config.config.get("Services", "piper")
    url = piper_url + "/voices/"
    name = voice_config["name"]

    log.debug("Calling url: %s" % url)
    try:
        r = requests.get(url)
    except:
        msg = "Piper server not found at url %s" % (url)
        log.error(msg)
        raise VoiceException(msg)
    
    log.debug("Response:\n%s" % r.text)
    voicenames = getVoicenames(r)
    log.debug("piper voicenames: %s" % voicenames)
    if not name in voicenames:
        msg = "Piper voice %s not found at url %s" % (name, url)
        log.error(msg)
        raise VoiceException(msg)
    else:
        log.info("Piper voice found at url %s" % url)
        

def getVoicenames(response):
    names = []
    data = response.json()
    for voice in data:
        names.append(voice["name"])
    return names


def utt2piper(input,lang,voice_config):
    chunks = []
    for p0 in input["paragraphs"]:
        for s in p0["sentences"]:
            for p in s["phrases"]:
                chunk = []
                for t in p["tokens"]:
                    for w in t["words"]:
                        token = {
                            "orth": w["orth"]
                        }
                        if "trans" in w:
                            inputTrans = w['trans']
                            trans = mapToPiper(inputTrans,lang,voice_config)
                            token["phonemes"] = trans
                            if "g2p_method" in w:
                                token["g2p_method"] = w["g2p_method"]
                        if "lang" in w:
                            token["lang"] = w["lang"]
                        chunk.append(token)
                chunks.append(chunk)
    return chunks

def synthesise(lang, voice_config, input, hostname=None, speaker_id=None, speaking_rate=1.0):
    log.debug(f"piper_adapter input: {input}")
    url = piper_url + "/synthesize/"
    tokens = utt2piper(input,lang,voice_config)
    if speaker_id is None:
        speaker_id = -1
    params = {
        "voice":voice_config["name"],
        "input_type":"tokens",
        "input":tokens,
        "speaking_rate": speaking_rate,
        "speaker_id": speaker_id,
        "return_type":"json",
    }

    r = requests.post(url, json=params)
    if not r.ok:
        from http.client import responses
        raise Exception(f"Piper request returned status code {r.status_code} {responses[r.status_code]}")
    obj = r.json()
    if len(obj) != 1:
        raise Exception(f"Expected one item back from piper_tts, found {len(obj)}")
    
    res = obj[0]
    audio_url = os.path.join(piper_url, "static", res["audio"])

    log.info("piper AUDIO_URL: %s" % audio_url)

    tokens = []
    for token in res["input"]:
        if "end_time" in token:
            token["endtime"] = token["end_time"]
            token.pop("end_time")
            token.pop("start_time")
        #if "phonemes" in token:
            #inputPhonemes = token["phonemes"]
            #mapped, err = mapFromPiper(inputPhonemes, lang, voice_config)
            #if err is None:
            #    token["phonemes"] = mapped
            #    if "input" in token and token["input"] == inputPhonemes:
            #        token["input"] = mapped
            #else:
            #    token["error"] = err
        tokens.append(token)

    return (audio_url, tokens)

def mapToPiper(trans,lang,voice):
    log.info("piper_adapter.mapToPiper( %s , %s , %s )" % (trans, lang, voice))

    if "mapper" in voice:
        #Bad names.. It should be perhaps "external" and "internal" instead of "from" and "to"
        to_symbol_set = voice["mapper"]["to"]
        from_symbol_set = voice["mapper"]["from"]
        log.info("piper_adapter.mapToPiper %s -> %s" % (from_symbol_set, to_symbol_set))    
    else:
        log.info("No piper mapper defined for language %s" % lang)
        return trans

    url = mapper_url+"/mapper/map/%s/%s/%s" % (from_symbol_set, to_symbol_set, quote(trans))

    log.info("MAPPER URL before requests: %s" % url)

    r = requests.get(url)
    log.info("MAPPER URL: "+r.url)
    response = r.text
    #log.debug("RESPONSE: %s" % response)
    try:
        response_json = json.loads(response)
        #log.debug("RESPONSE_JSON: %s" % response_json)
        new_trans = response_json["result"]
        new_trans = new_trans.replace(".","") # TODO should be added to map table, but it's not allowed atm jan 2026 /HL
    except:
        log.error("unable to map %s, from %s to %s. response was %s" % (trans, from_symbol_set, to_symbol_set, response))
        raise
    log.info("NEW TRANS: %s" % new_trans)
    return new_trans


def mapFromPiper(trans,lang,voice):
    log.info("piper_adapter.mapFromPiper( %s , %s , %s )" % (trans, lang, voice))

    if "mapper" in voice:
        #Bad names.. It should be perhaps "external" and "internal" instead of "from" and "to"
        to_symbol_set = voice["mapper"]["from"]
        from_symbol_set = voice["mapper"]["to"]
        log.info("piper_adapter.mapFromPiper %s -> %s" % (from_symbol_set, to_symbol_set))    
    else:
        log.info("No piper mapper defined for language %s" % lang)
        return trans

    url = mapper_url+"/mapper/map/%s/%s/%s" % (from_symbol_set, to_symbol_set, quote(trans))

    log.info("MAPPER URL before requests: %s" % url)

    r = requests.get(url)
    log.info("MAPPER URL: "+r.url)
    response = r.text
    #log.debug("RESPONSE: %s" % response)
    try:
        response_json = json.loads(response)
        log.info("RESPONSE_JSON: %s" % response_json)
        if type(response_json) == dict:
            response_json = [response_json]
        for rj in response_json:
            if "type" in rj and rj["type"] == "error":
                msg = "unable to map %s, from %s to %s. response was %s" % (trans, from_symbol_set, to_symbol_set, response)
                log.error(msg)
                return "", msg
            else:
                new_trans = rj["result"]
    except:
        log.error("unable to map %s, from %s to %s. response was %s" % (trans, from_symbol_set, to_symbol_set, response))
        raise
    log.info("NEW TRANS: %s" % new_trans)
    return new_trans, None

