import sys, requests, json, re
import sys, os, re, io


if __name__ == "__main__":
    sys.path.append(".")

import wikispeech_server.log as log
import wikispeech_server.config as config
from wikispeech_server.voice import VoiceException

mapper_url = config.config.get("Services", "mapper")
matcha_url = config.config.get("Services", "matcha")

from urllib.parse import quote

def testVoice(voice_config):
    matcha_url = config.config.get("Services", "matcha")
    url = matcha_url + "/voices/"
    name = voice_config["name"]

    log.debug("Calling url: %s" % url)
    try:
        r = requests.get(url)
    except:
        msg = "Matcha server not found at url %s" % (url)
        log.error(msg)
        raise VoiceException(msg)
    
    log.debug("Response:\n%s" % r.text)
    voicenames = getVoicenames(r)
    log.debug("matcha voicenames: %s" % voicenames)
    if not name in voicenames:
        msg = "Voice %s not found at url %s" % (name, url)
        log.error(msg)
        raise VoiceException(msg)
    else:
        log.info("Voice found at url %s" % url)
        

def getVoicenames(response):
    names = []
    data = response.json()
    for voice in data:
        names.append(voice["name"])
    return names


def utt2matcha(input,lang,voice_config):
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
                            trans = mapToMatcha(inputTrans,lang,voice_config)
                            token["phonemes"] = trans
                            if "g2p_method" in w:
                                token["g2p_method"] = w["g2p_method"]
                        if "lang" in w:
                            token["lang"] = w["lang"]
                        chunk.append(token)
                chunks.append(chunk)
    return chunks

def synthesise(lang, voice_config, input, hostname=None, speaker_id=None, speaking_rate=1.0):
    url = matcha_url + "/synthesize/"
    tokens = utt2matcha(input,lang,voice_config)
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
        raise Exception(f"Matcha request returned status code {r.status_code} {responses[r.status_code]}")
    obj = r.json()
    if len(obj) != 1:
        raise Exception(f"Expected one item back from matcha_tts, found {len(obj)}")
    
    res = obj[0]
    audio_url = os.path.join(matcha_url, "static",res["audio"])

    log.info("matcha AUDIO_URL: %s" % audio_url)

    tokens = []
    for token in res["tokens"]:
        if "end_time" in token:
            token["endtime"] = token["end_time"]
            token.pop("end_time")
            token.pop("start_time")
        if "phonemes" in token:
            inputPhonemes = token["phonemes"]
            mapped = mapFromMatcha(inputPhonemes, lang, voice_config)
            token["phonemes"] = mapped
            if "input" in token and token["input"] == inputPhonemes:
                token["input"] = mapped
        tokens.append(token)
    
    return (audio_url, tokens)

def mapToMatcha(trans,lang,voice):
    log.info("matcha_adapter.mapToMatcha( %s , %s , %s )" % (trans, lang, voice))

    if "mapper" in voice:
        #Bad names.. It should be perhaps "external" and "internal" instead of "from" and "to"
        to_symbol_set = voice["mapper"]["to"]
        from_symbol_set = voice["mapper"]["from"]
        log.info("matcha_adapter.mapToMatcha %s -> %s" % (from_symbol_set, to_symbol_set))    
    else:
        log.info("No matcha mapper defined for language %s" % lang)
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
    except:
        log.error("unable to map %s, from %s to %s. response was %s" % (trans, from_symbol_set, to_symbol_set, response))
        raise
    log.info("NEW TRANS: %s" % new_trans)
    return new_trans


def mapFromMatcha(trans,lang,voice):
    log.info("matcha_adapter.mapFromMatcha( %s , %s , %s )" % (trans, lang, voice))

    if "mapper" in voice:
        #Bad names.. It should be perhaps "external" and "internal" instead of "from" and "to"
        to_symbol_set = voice["mapper"]["from"]
        from_symbol_set = voice["mapper"]["to"]
        log.info("matcha_adapter.mapFromMatcha %s -> %s" % (from_symbol_set, to_symbol_set))    
    else:
        log.info("No matcha mapper defined for language %s" % lang)
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
    except:
        log.error("unable to map %s, from %s to %s. response was %s" % (trans, from_symbol_set, to_symbol_set, response))
        raise
    log.info("NEW TRANS: %s" % new_trans)
    return new_trans


if __name__ == "__main__":
    #input = {"children": [{"children": [{"children": [{"children": [{"accent": "!H*", "children": [{"children": [{"p": "h", "tag": "ph"}, {"p": "@", "tag": "ph"}], "ph": "h @", "tag": "syllable"}, {"accent": "!H*", "children": [{"p": "l", "tag": "ph"}, {"p": "@U", "tag": "ph"}], "ph": "l @U", "stress": "1", "tag": "syllable"}], "g2p_method": "lexicon", "ph": "h @ - ' l @U", "pos": "UH", "tag": "t", "text": "hello"}, {"pos": ".", "tag": "t", "text": ","}, {"children": [{"children": [{"p": "h", "tag": "ph"}, {"p": "@", "tag": "ph"}], "ph": "h @", "tag": "syllable"}, {"children": [{"p": "l", "tag": "ph"}, {"p": "@U", "tag": "ph"}], "ph": "l @U", "stress": "1", "tag": "syllable"}], "g2p_method": "lexicon", "ph": "h @ - ' l @U", "pos": ",", "tag": "t", "text": "hello"}, {"pos": ".", "tag": "t", "text": "."}, {"breakindex": "5", "tag": "boundary", "tone": "L-L%"}], "tag": "phrase"}], "tag": "s"}], "tag": "p"}], "tag": "utt"}


    input = {
        "lang": "en-US",
        "paragraphs": [
            {
                "sentences": [
                    {
                        "phrases": [
                            {
                                "boundary": {
                                    "breakindex": "5",
                                    "tone": "L-L%"
                                },
                                "tokens": [
                                    {
                                        "token_orth": "hello",
                                        "words": [
                                            {
                                                "accent": "!H*",
                                                "g2p_method": "lexicon",
                                                "orth": "hello",
                                                "pos": "UH",
                                                "trans": "h @ - ' l @U"
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
    

    lang = "en"
    voice = {"matcha_voice":"slt"}
    log.log_level = "debug"

    
    (audio_url, tokens) = synthesise(lang, voice, input)
    log.debug("AUDIO URL: %s" % audio_url)
    log.debug("TOKENS: %s" % tokens)
