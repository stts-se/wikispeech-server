from wikispeech_mockup.adapters.lexicon_client import Lexicon
from wikispeech_mockup.adapters.mapper_client import Mapper


class Textprocessor(object):
    def __init__(self, tp_config):
        self.name = tp_config["name"]
        self.lang = tp_config["lang"]
        self.loadComponents(tp_config["components"])

    def loadComponents(self, cconfigs):
        self.components = []
        for cconfig in cconfigs:

            if "lexicon" in cconfig:
                component = Lexicon(cconfig["lexicon"])
            else:
                component = TextprocComponent(cconfig)
            self.components.append(component)

class TextprocComponent(object):

    def __init__(self, cconfig):
        self.module = cconfig["module"]
        self.call = cconfig["call"]
        if "mapper" in cconfig:
            self.mapper = Mapper(cconfig["mapper"]["from"], cconfig["mapper"]["to"])
        
                                              

