import re, requests

import wikispeech_mockup.log as log
import wikispeech_mockup.config as config

from wikispeech_mockup.adapters.lexicon_client import Lexicon, LexiconException
from wikispeech_mockup.adapters.mapper_client import Mapper, MapperException

class VoiceException(Exception):
    pass

class Voice(object):
    def __init__(self, voice_config):
        self.name = voice_config["name"]
        self.lang = voice_config["lang"]
        self.engine = voice_config["engine"]
        self.adapter = voice_config["adapter"]

        self.testVoice()

        
        if "mapper" in voice_config:
            try:
                self.mapper = Mapper(voice_config["mapper"]["from"], voice_config["mapper"]["to"])
            except MapperException as e:
                raise VoiceException(e)
            

    def testVoice(self):
        log.info("Testing voice %s" % self.name)
        if self.engine == "marytts":
            voice_host = config.config.get("Services", "marytts")
            url = re.sub("process","voices",voice_host)
            log.debug("Calling url: %s" % url)
            try:
                r = requests.get(url)
            except:
                msg = "Marytts server not found at url %s" % (url)
                log.error(msg)
                raise VoiceException(msg)

            response = r.text
            log.debug("Response:\n%s" % response)
            marytts_voicenames = self.getMaryttsVoicenames(response)
            if not self.name in marytts_voicenames:
                msg = "Voice %s not found at url %s" % (self.name, url)
                log.error(msg)
                raise VoiceException(msg)
            else:
                log.info("Voice found at url %s" % url)

    def getMaryttsVoicenames(self, response):
        names = []
        lines = response.split("\n")
        for line in lines:
            #example: stts_sv_nst-hsmm sv male hmm
            name = line.split(" ")[0]
            names.append(name)
        return names

    def __repr__(self):
        return "Voice:{name:%s, lang=%s}" % (self.name, self.lang)

    def __str__(self):
        return self.__repr__()



    
if __name__ == "__main__":

    log.log_level = "debug" #debug, info, warning, error

    voice_config = {
        "lang":"sv",
        "name":"stts_sv_nst-hsmm",
        "engine":"marytts",
        "adapter":"adapters.marytts_adapter",
        "mapper": {
            "from":"sv-se_ws-sampa",
            "to":"sv-se_sampa_mary"
        }
    }

    try:
        v = Voice(voice_config)
        log.info("Created voice %s from %s" % (v, voice_config))
    except VoiceException as e:
        log.error("Failed to create voice for %s\nException message was:\n%s" % (voice_config, e))
