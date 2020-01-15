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

            """ Call to socket, does not work properly in docker compose environment
            # Write text to file
            inputfilename="%s/%s/ahotts_test.txt" % (cwdir,tmpdir)
            inputfile=open(inputfilename,"wb")
            inputfile.write("Hasierako proba".encode('latin-1')+'\n'.encode('latin-1'))
            inputfile.close()
            # Open socket
            socketa=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            ipa=socket.gethostbyname(ahotts_server_ip)
            print (ipa)
            socketa.connect((ipa,int(ahotts_server_port)))
            # Write options
            options_struct=struct.Struct('4s 4s 4s 1024s 1024s 1024s ?')
            options_struct_packed=options_struct.pack(self.lang.encode('utf-8'),"".encode('utf-8'),ahotts_speed.encode('utf-8'),"".encode('utf-8'),"wav/ahotts_test.pho".encode('utf-8'),"wav/ahotts_test.wrd".encode('utf-8'),True)
            totalsent=0
            while totalsent<len(options_struct_packed):
                sent=socketa.send(options_struct_packed[totalsent:])
                if sent==0:
                    raise RuntimeError("socket connection broken")
                totalsent=totalsent+sent
            # Write text file length + text file
            socket_write_filelength_file(socketa,inputfilename)
            # Read wav file
            wavfilename="%s/%s/ahotts_test.wav" % (cwdir,tmpdir)
            wavfile=open(wavfilename,"wb")
            wavfile.write(socket_read_filelength_file(socketa))
            wavfile.close()
            # Read pho file
            socket_read_filelength_file(socketa)
            # Read wrd file
            wrdfilename="%s/%s/ahotts_test.wrd" % (cwdir,tmpdir)
            wrdfile=open(wrdfilename,"wb")
            wrdfile.write(socket_read_filelength_file(socketa))
            wrdfile.close()
            # Close socket
            socketa.close()
            try:
                wavfile=open(wavfilename,'r')
                wavfile.close()
                os.remove(inputfilename)
                os.remove(wavfilename)
                os.remove(wrdfilename)
            except:
                msg = "AhoTTS server not found at IP %s and Port %s" % (ahotts_server_ip,ahotts_server_port)
                log.error(msg)
                raise VoiceException(msg)
            """

            response=requests.post("http://"+ahotts_server_ip+":"+ahotts_server_port+"/ahotts_getaudio",data={'text':"Hasierako proba".encode('latin-1'),'lang':self.lang,'voice':self.name,'speed':ahotts_speed})
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

    def getMaryttsVoicenames(self, response):
        names = []
        lines = response.split("\n")
        for line in lines:
            #example: stts_sv_nst-hsmm sv male hmm
            name = line.split(" ")[0]
            names.append(name)
        return names

    def __repr__(self):
        #return {"name":self.name, "lang":self.lang}
        return "{name:%s, lang:%s}" % (self.name, self.lang)

    def __str__(self):
        return {"name":self.name, "lang":self.lang}
        #return "{name:%s, lang:%s}" % (self.name, self.lang)




    
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
