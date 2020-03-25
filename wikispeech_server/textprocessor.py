if __name__ == "__main__":
    import sys
    sys.path.append("/media/bigdisk/git/wikispeech_mockup")
    print(sys.path)

import wikispeech_server.log as log

from wikispeech_server.adapters.lexicon_client import Lexicon, LexiconException
from wikispeech_server.adapters.mapper_client import Mapper, MapperException

#For testing marytts_adapter
#TODO? move to test function in marytts_adapter
import wikispeech_server.config as config
import requests

class TextprocessorException(Exception):
    pass

class Textprocessor(object):
    def __init__(self, tp_config):
        self.config = tp_config
        self.name = tp_config["name"]
        self.lang = tp_config["lang"]
        self.loadComponents(tp_config["components"])


    def loadComponents(self, cconfigs):
        self.components = []
        for cconfig in cconfigs:

            if "lexicon" in cconfig:
                try:
                    component = Lexicon(cconfig["lexicon"])
                    component.type = "Lexicon"
                except LexiconException as e:
                    raise TextprocessorException(e)
            else:
                try:
                    component = TextprocComponent(cconfig)
                except TextprocComponentException as e:
                    raise TextprocessorException(e)
                
            self.components.append(component)

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

class TextprocComponentException(Exception):
    pass

class TextprocComponent(object):

    def __init__(self, cconfig):
        self.type = "TextprocComponent"
        self.module = cconfig["module"]
        self.call = cconfig["call"]
        if "mapper" in cconfig:
            try:
                self.mapper = Mapper(cconfig["mapper"]["from"], cconfig["mapper"]["to"])
            except MapperException as e:
                raise TextprocComponentException(e)
        if "module" in cconfig and cconfig["module"] == "adapters.marytts_adapter":
            log.debug("Trying to create marytts component: %s" % cconfig)
            #For testing marytts_adapter
            #TODO? move to test function in marytts_adapter
            try:
                marytts_url = config.config.get("Services", "marytts")
                payload = {
                    "INPUT_TYPE": "TEXT",
                    "OUTPUT_TYPE": "INTONATION",
                    "LOCALE": "en_US",
                    "INPUT_TEXT": "test"
                }
                r = requests.get(marytts_url, params=payload)
                log.debug("CALLING MARYTTS: %s" % r.url)    
                xml = r.text
            except Exception as e:
                raise TextprocComponentException(e)

                                              

if __name__ == "__main__":

    log.log_level = "debug" #debug, info, warning, error

    tp_config = {
        "name":"wikitextproc_sv",
        "lang":"sv",
        "default": True,
        "components":[
            {
                "module":"adapters.marytts_adapter",
                "call":"marytts_preproc",
                "mapper": {
                    "from":"sv-se_ws-sampa",
                    "to":"sv-se_sampa_mary"
                },
            },
            {
                "module":"adapters.lexicon_client",
                "call":"lexLookup",
                "lexicon":"wikispeech_testdb:sv"
            }
        ]
    }
    try:
        tp = Textprocessor(tp_config)
        log.info("Created textprocessor %s from %s" % (tp, tp_config))

        print(tp)
        print(tp.isDefault())
        
    except TextprocessorException as e:
        log.error("Failed to create textprocessor for %s\nException message was:\n%s" % (tp_config, e))
