import requests
import simplejson as json
import wikispeech_server.config as config
import wikispeech_server.log as log


class MapperException(Exception):
    pass

class Mapper(object):
    
    def __init__(self, from_symbol_set, to_symbol_set):
        self.from_symbol_set = from_symbol_set
        self.to_symbol_set = to_symbol_set
        
        self.base_url = "%s/mapper" % config.config.get("Services", "lexicon")

        self.test()


    def test(self):
        url = "%s/%s/%s/%s" % (self.base_url, "maptable", self.from_symbol_set, self.to_symbol_set)
        log.debug(url)
        try:
            r = requests.get(url)
            response = r.text
            response_json = json.loads(response)
        except json.JSONDecodeError:
            msg = "Unable to create mapper from %s to %s. Response was: %s" % (self.from_symbol_set, self.to_symbol_set, response)
            log.error(msg)
            raise MapperException(msg)
        except Exception as e:
            msg = "Unable to create mapper at url %s. Reason: %s" % (url, e)
            log.error(msg)
            raise MapperException(msg)


    def map(self, string):
        
        url = "%s/%s/%s/%s/%s" % (self.base_url, "map", self.from_symbol_set, self.to_symbol_set, string)
        r = requests.get(url)
        log.debug(r.url)
        response = r.text
        try:
            response_json = json.loads(response)
            new_string = response_json["Result"]
            return new_string
        except:
            log.error("unable to map string '%s'from %s to %s. response was %s" % (string,self.from_symbol_set, self.to_symbol_set, response))
            raise MapperException
        
       


        
