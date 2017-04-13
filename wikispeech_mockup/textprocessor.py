import wikispeech_mockup.log as log

from wikispeech_mockup.adapters.lexicon_client import Lexicon, LexiconException
from wikispeech_mockup.adapters.mapper_client import Mapper, MapperException

class TextprocessorException(Exception):
    pass

class Textprocessor(object):
    def __init__(self, tp_config):
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
            
                                              

if __name__ == "__main__":

    log.log_level = "debug" #debug, info, warning, error

    tp_config = {
        "name":"wikitextproc_sv",
        "lang":"sv",
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
                "lexicon":"sv-se.nstXX"
            }
        ]
    }
    try:
        tp = Textprocessor(tp_config)
        log.info("Created textprocessor %s from %s" % (tp, tp_config))
    except TextprocessorException as e:
        log.error("Failed to create textprocessor for %s\nException message was:\n%s" % (tp_config, e))
