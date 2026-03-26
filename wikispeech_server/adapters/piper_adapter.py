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
    wid=0
    for p0 in input["paragraphs"]:
        for s in p0["sentences"]:
            for p in s["phrases"]:
                chunk = []
                for t in p["tokens"]:
                    for w in t["words"]:
                        token = {
                            "orth": w["orth"],
                            "id": wid
                        }
                        if "prepunct" in w:
                            token["prepunct"] = w["prepunct"]
                        if "postpunct" in w:
                            token["postpunct"] = w["postpunct"]
                        wid+=1
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
    log.debug(f"piper_adapter tokens to piper_server: {tokens}")
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

    tokens = piper2utt(input, res["tokens"])
    return (audio_url, tokens)

def piper2utt(input, tokens):
    # print("??? piper2utt input", input)
    # print("??? piper2utt tokens", tokens)

    ### ORIGINAL INPUT
    # [{'name': 'text1', 'paragraphs': [{'name': 'par1', 'sentences': [{'name': 'sent1', 'phrases': [{'input': 'Karl XII', 'name': 'phrase1', 'tokens': [
    # {'name': 'token0', 'input_orth': 'Karl XII',
    #  'words': [
    #      {'orth': 'Karl', 'trans': '" k A: rl', 'g2p_method': 'lexicon', 'pos': 'PM NOM'},
    #      {'orth': 'den', 'trans': '" d e n', 'g2p_method': 'lexicon', 'pos': 'DT UTR SIN DEF'},
    #      {'orth': 'tolfte', 'trans': '"" t O l f . % t @', 'g2p_method': 'lexicon', 'pos': 'RO NOM'}
    #  ]}]}]}]}]}

    ### PIPER OUTPUT
    #  "tokens": [
    # {
    #   "endtime": 394,
    #   "g2p_method": "lexicon",
    #   "input": "kˈⱭɭ",
    #   "orth": "Karl",
    #   "phonemes": "kˈⱭɭ"
    # },
    # {
    #   "endtime": 638,
    #   "g2p_method": "lexicon",
    #   "input": "dˈen",
    #   "orth": "den",
    #   "phonemes": "dˈen"
    # },
    # {
    #   "endtime": 1544,
    #   "g2p_method": "lexicon",
    #   "input": "t°olft`ə",
    #   "orth": "tolfte",
    #   "phonemes": "t°olft`ə"
    # }
    #],

    ### EXPECTED OUTPUT
    # "tokens": [
    #     {
    #         "endtime": 1305,
    #         "orth": "Karl den tolfte"
    #     },
    #     {
    #         "endtime": 1705,
    #         "orth": "prickus"
    #     }
    #

    res = []
    global_wi = 0
    token_count = 0
    for p in input["paragraphs"]:
        for s in p["sentences"]:
            for phr in s["phrases"]:
                for t in phr["tokens"]:
                    token_count+=1
                    input_orth = t.get("input_orth","")
                    words = []
                    res_t = {
                        "orth": input_orth
                    }
                    expanded = []
                    #tts_input = []
                    #tts_phonemes = []
                    end_time = None
                    for w in t["words"]:
                        global_wi+=1
                        #print("??? w", w)
                        #print("??? from_tokens", tokens[global_wi-1])
                        if len(tokens) > global_wi-1 and w["orth"] == tokens[global_wi-1]["orth"]:
                            w = w | tokens[global_wi-1]
                            # piper internal fields
                            w["tts_input"] = w["input"]
                            w.pop("input")
                            w["tts_phonemes"] = w["phonemes"]
                            w.pop("phonemes")
                            #tts_input.append(w["tts_input"])
                            #tts_phonemes.append(w["tts_phonemes"])
                            expanded.append(w["orth"])
                            # attribute names
                            w["endtime"] = w["end_time"]
                            w.pop("end_time")
                            w.pop("start_time")
                            endtime=w["endtime"]
                            words.append(w)
                    res_t["endtime"]=endtime
                    expanded_s = " ".join(expanded)
                    if expanded_s != input_orth:
                        res_t["expanded"]=expanded_s
                    res_t["words"] = words
                    #res_t["tts_input"]=tts_input
                    #res_t["tts_phonemes"]=" ".join(tts_phonemes)                              
                    res.append(res_t)

    #print("piper_adapter debug: token count: ", global_wi, len(tokens), token_count)
        
    return res
    
    # res = []
    # for token in tokens:
    #     if "end_time" in token:
    #         token["endtime"] = token["end_time"]
    #         token.pop("end_time")
    #         token.pop("start_time")
    #     #if "phonemes" in token:
    #         #inputPhonemes = token["phonemes"]
    #         #mapped, err = mapFromPiper(inputPhonemes, lang, voice_config)
    #         #if err is None:
    #         #    token["phonemes"] = mapped
    #         #    if "input" in token and token["input"] == inputPhonemes:
    #         #        token["input"] = mapped
    #         #else:
    #         #    token["error"] = err
    #     res.append(token)
    # return res


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
        log.debug("RESPONSE_JSON: %s" % response_json)
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

