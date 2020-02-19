import re, requests, os, socket, struct

import wikispeech_server.log as log
import wikispeech_server.config as config

from wikispeech_server.adapters.lexicon_client import Lexicon, LexiconException
from wikispeech_server.adapters.mapper_client import Mapper, MapperException



class VoiceException(Exception):
    pass

class Voice(object):
    def __init__(self, voice_config):
        self.config = voice_config
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


        elif self.engine == "ahotts" and config.config.get("Services", "ahotts_server_ip") != None:
            from wikispeech_server.adapters.ahotts_adapter import socket_write_filelength_file,socket_read_filelength_file
            cwdir = os.getcwd()
            tmpdir = config.config.get("Audio settings","audio_tmpdir")
            ahotts_server_ip = config.config.get("Services", "ahotts_server_ip")
            ahotts_server_port = config.config.get("Services", "ahotts_server_port")
            ahotts_speed = config.config.get("Services", "ahotts_speed")

            try:
                response=requests.post("http://"+ahotts_server_ip+":"+ahotts_server_port+"/ahotts_getaudio",data={'text':"Hasierako proba".encode('latin-1'),'lang':self.lang,'voice':self.name,'speed':ahotts_speed})
            except:
                msg = "Ahotts server not found at %s:%s" % (ahotts_server_ip, ahotts_server_port)
                log.error(msg)
                raise VoiceException(msg)
                
            if response.status_code==200:
                files=response.json()
                wavfile=files['wav']
                wrdfile=files['wrd']
                response2=requests.get("http://"+ahotts_server_ip+":"+ahotts_server_port+"/ahotts_downloadfile?file="+wavfile)
                if response2.status_code==200:
                    response3=requests.get("http://"+ahotts_server_ip+":"+ahotts_server_port+"/ahotts_downloadfile?file="+wrdfile)
                    if response3.status_code!=200:
                        msg = "AhoTTS server error"
                        log.error(msg)
                        raise VoiceException(msg)
                else:
                    msg = "AhoTTS server error"
                    log.error(msg)
                    raise VoiceException(msg)
            else:
                msg = "AhoTTS server error"
                log.error(msg)
                raise VoiceException(msg)

        elif self.engine == "nnmnkwii":
            url = self.config["url"]
            try:
                response=requests.get(url)
                assert response.status_code == 200
            except:
                msg = "nnmnkwii server not found at url %s" % (url)
                log.error(msg)
                raise VoiceException(msg)
            log.info("Test successful for voice %s" % self.name)
            
        else:
            log.warning("No test implemented for voice %s" % self.name)


            
    def getMaryttsVoicenames(self, response):
        names = []
        lines = response.split("\n")
        for line in lines:
            #example: stts_sv_nst-hsmm sv male hmm
            name = line.split(" ")[0]
            names.append(name)
        return names

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
