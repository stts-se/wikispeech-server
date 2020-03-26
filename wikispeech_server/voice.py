import sys, re, requests, os, socket, struct

import wikispeech_server.log as log
import wikispeech_server.config as config

from wikispeech_server.adapters.lexicon_client import Lexicon, LexiconException
from wikispeech_server.adapters.mapper_client import Mapper, MapperException

import wikispeech_server.util as util

class VoiceException(Exception):
    pass

class Voice(object):
    def __init__(self, voice_config):
        self.config = voice_config
        self.name = voice_config["name"]
        self.lang = voice_config["lang"]
        self.engine = voice_config["engine"]
        self.adapter = voice_config["adapter"]

        if "skip_test" in voice_config and voice_config["skip_test"] == True:
            pass
        else:
            try:
                if "directory" in voice_config:
                    directory = voice_config["directory"]
                else:
                    directory = "wikispeech_server"
                adapter = util.import_module(directory, self.config["adapter"])
                adapter.testVoice(self.config)
            except Exception as e:
                msg = "Test failed for adapter %s. Reason: %s" % (self.adapter, e)
                log.warning(msg)
                raise

        
        if "mapper" in voice_config:
            try:
                self.mapper = Mapper(voice_config["mapper"]["from"], voice_config["mapper"]["to"])
            except MapperException as e:
                raise VoiceException(e)
            

            

    def isDefault(self):
        if "default" in self.config and self.config["default"] == True:
            return True
        return False
    
    def __repr__(self):
        l = []
        l.append("name:%s" % self.name)
        l.append("lang:%s" % self.lang)
        if self.isDefault():
            l.append("default: True")
        if "config_file" in self.config:
            l.append("config_file: %s" % (self.config["config_file"]))
        
        return "{%s}" % ", ".join(l)

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
