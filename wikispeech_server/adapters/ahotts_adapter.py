import os, re, sys, hashlib, struct, socket, requests

if __name__ == "__main__":
    sys.path.append(".")

import wikispeech_server.log as log
import wikispeech_server.config as config

cwdir = os.getcwd()
tmpdir = config.config.get("Audio settings","audio_tmpdir")
ahotts_server_ip = config.config.get("Services", "ahotts_server_ip")
ahotts_server_port = config.config.get("Services", "ahotts_server_port")
ahotts_speed = config.config.get("Services", "ahotts_speed")

from wikispeech_server.adapters.units_eu import units_eu
from wikispeech_server.adapters.abbreviations_eu import abbreviations_eu
from wikispeech_server.adapters.foreign_eu import foreign_eu
from wikispeech_server.adapters.initials_eu import initials_eu

specials_eu=units_eu+initials_eu+abbreviations_eu+foreign_eu
specials_eu.sort()

def socket_write_filelength_file(tts_socket,filename):
    file_length=os.stat(filename).st_size
    length_struct=struct.Struct('11s')
    length_struct_packed=length_struct.pack(str(file_length).encode('utf-8'))
    totalsent=0
    while totalsent<len(length_struct_packed):
        sent=tts_socket.send(length_struct_packed[totalsent:])
        if sent==0:
            raise RuntimeError("socket connection broken")
        totalsent=totalsent+sent
    inputfile=open(filename,"rb")
    left=inputfile.read(1024)
    while (left):
        sent=tts_socket.send(left)
        if sent==0:
            raise RuntimeError("socket connection broken")
        left=inputfile.read(1024)
    inputfile.close()

def socket_read_filelength_file(tts_socket):
    chunks=[]
    bytes_recd=0
    while bytes_recd<11:
        chunk=tts_socket.recv(11-bytes_recd)
        if chunk==b'':
            raise RuntimeError("socket connection broken")
        chunks.append(chunk)
        bytes_recd=bytes_recd+len(chunk)
    length_struct_packed=b''.join(chunks)
    length_struct=struct.Struct('11s')
    file_length=length_struct.unpack(length_struct_packed)[0]
    file_length=file_length[:file_length.find(b'\x00')]
    file_length=int(file_length)
    chunks=[]
    bytes_recd=0
    while bytes_recd<file_length:
        chunk=tts_socket.recv(min(file_length-bytes_recd,2048))
        if chunk==b'':
            raise RuntimeError("socket connection broken")
        chunks.append(chunk)
        bytes_recd=bytes_recd+len(chunk)
    return b''.join(chunks)


def synthesise(lang, voice, utterance, presynth=False, hostname=None):
    log.info("Utterance: %s" % utterance)
    input = utterance['original_text']
    log.info("Text: %s" % input)
    words = get_orth(utterance)
    log.info("Words: %s" % words)

    hashstring=input+'&Lang='+lang+'&Voice='+voice['name']
    
    try:
        hash_object=hashlib.md5(hashstring.encode('latin-1'))
    except:
        try:
            hash_object=hashlib.md5(hashstring.encode('utf-8'))
        except:
            hash_object=hashlib.md5(hashstring.encode())
    hashnumber=hash_object.hexdigest()

    """ Call to tts_client, only works if ahotts is installed in same server as wikispeech_mockup. Better to make socket calls over the network.
    inputfile=open("%s/bin/tts_%s.txt" % (ahotts_dir, hashnumber),"wb")
    inputfile.write(input.encode('latin-1')+'\n'.encode('latin-1'))
    inputfile.close()
    ahotts_command = "cd %s/bin ; ./tts_client -SetDur=y -Speed=%s -IP=%s -Port=%s -InputFile=tts_%s.txt -OutputFile=tts_%s.wav -WordFile=tts_%s.wrd -PhoFile=tts_%s.pho ; mv tts_%s.wav %s/%s/tts_%s.wav ; rm tts_%s.txt" % (ahotts_dir, ahotts_speed, ahotts_server_ip, ahotts_server_port, hashnumber, hashnumber, hashnumber, hashnumber, hashnumber, cwdir, tmpdir, hashnumber, hashnumber)
    log.info("Ahotts command: %s" % ahotts_command)
    os.system(ahotts_command)
    audio_url = "%s%s/%s" % (hostname, "audio",'tts_%s.wav' % hashnumber)
    words_times_file=open(ahotts_dir+'/tts_'+hashnumber+'.wrd','r')
    words_times=words_times_file.readlines()
    words_times_file.close()
    os.remove(ahotts_dir+'/tts_'+hashnumber+'.wrd')
    os.remove(ahotts_dir+'/tts_'+hashnumber+'.pho')
    log.info(str(words))
    audio_url = "%s%s/%s" % (hostname, "audio",'tts_%s.wav' % hashnumber)
    words_times_file=open(wrdfilename,'r')
    words_times=words_times_file.readlines()
    words_times_file.close()
    os.remove(inputfilename)
    os.remove(wrdfilename)
    """

    """ Call to socket, does not work properly in docker compose environment
    # Write text to file
    inputfilename="%s/%s/tts_%s.txt" % (cwdir,tmpdir,hashnumber)
    inputfile=open(inputfilename,"wb")
    inputfile.write(input.encode('latin-1')+'\n'.encode('latin-1'))
    inputfile.close()
    # Open socket
    socketa=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    ipa=socket.gethostbyname(ahotts_server_ip)
    socketa.connect((ipa,int(ahotts_server_port)))
    # Write options
    options_struct=struct.Struct('4s 4s 4s 1024s 1024s 1024s ?')
    options_struct_packed=options_struct.pack(lang.encode('utf-8'),"".encode('utf-8'),ahotts_speed.encode('utf-8'),"".encode('utf-8'),("wav/tts_%s.pho" % hashnumber).encode('utf-8'),("wav/tts_%s.wrd" % hashnumber).encode('utf-8'),True)
    totalsent=0
    while totalsent<len(options_struct_packed):
        sent=socketa.send(options_struct_packed[totalsent:])
        if sent==0:
            raise RuntimeError("socket connection broken")
        totalsent=totalsent+sent
    # Write text file length + text file
    socket_write_filelength_file(socketa,inputfilename)
    # Read wav file
    wavfilename="%s/%s/tts_%s.wav" % (cwdir,tmpdir,hashnumber)
    wavfile=open(wavfilename,"wb")
    wavfile.write(socket_read_filelength_file(socketa))
    wavfile.close()
    # Read pho file
    socket_read_filelength_file(socketa)
    # Read wrd file
    wrdfilename="%s/%s/tts_%s.wrd" % (cwdir,tmpdir,hashnumber)
    wrdfile=open(wrdfilename,"wb")
    wrdfile.write(socket_read_filelength_file(socketa))
    wrdfile.close()
    # Close socket
    socketa.close()
    audio_url = "%s%s/%s" % (hostname, "audio",'tts_%s.wav' % hashnumber)
    words_times_file=open(wrdfilename,'r')
    words_times=words_times_file.readlines()
    words_times_file.close()
    os.remove(inputfilename)
    os.remove(wrdfilename)
    """

    response=requests.post("http://"+ahotts_server_ip+":"+ahotts_server_port+"/ahotts_getaudio",data={'text':input.encode('latin-1')+'\n'.encode('latin-1'),'lang':lang,'voice':voice,'speed':ahotts_speed})
    url="http://"+ahotts_server_ip+":"+ahotts_server_port+"/ahotts_getaudio"
    data={'text':input.encode('latin-1')+'\n'.encode('latin-1'),'lang':lang,'voice':voice,'speed':ahotts_speed}
    
    if response.status_code==200:
        files=response.json()
        wavfile=files['wav']
        wrdfile=files['wrd']
        response2=requests.get("http://"+ahotts_server_ip+":"+ahotts_server_port+"/ahotts_downloadfile?file="+wavfile)
        if response2.status_code==200:
            wavfilename="%s/%s/tts_%s.wav" % (cwdir,tmpdir,hashnumber)
            wavfile=open(wavfilename,"wb")
            for chunk in response2.iter_content(1024):
                wavfile.write(chunk)
            wavfile.close()
            response3=requests.get("http://"+ahotts_server_ip+":"+ahotts_server_port+"/ahotts_downloadfile?file="+wrdfile)
            if response3.status_code==200:
                wrdfilename="%s/%s/tts_%s.wrd" % (cwdir,tmpdir,hashnumber)
                wrdfile=open(wrdfilename,"wb")
                for chunk in response3.iter_content(1024):
                    wrdfile.write(chunk)
                wrdfile.close()
            else:
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
    audio_url = "%s%s/%s" % (hostname, "audio",'tts_%s.wav' % hashnumber)
    words_times_file=open(wrdfilename,'r')
    words_times=words_times_file.readlines()
    words_times_file.close()
    os.remove(wrdfilename)

    words_times=list(map(lambda x:x[:-1].split(' ')[1],words_times))
    tokens = []
    starttime=0.0
    lastendtime=0.0
    for word_ind in range(len(words)):
        word=words[word_ind]
        if word_ind>len(words_times)-1:
            endtime=lastendtime
        else:
            endtime=float(words_times[word_ind])/1000
        tokens.append({"orth":word, "starttime":starttime, "endtime":endtime})
        starttime=endtime
        lastendtime=endtime
    return (audio_url, tokens)



def get_orth(utterance):
    orth_list = []
    paragraphs = utterance["paragraphs"]
    for paragraph in paragraphs:
        sentences = paragraph["sentences"]
        for sentence in sentences:
            phrases = sentence["phrases"]
            for phrase in phrases:
                tokens = phrase["tokens"]
                for token in tokens:
                    words = token["words"]
                    for word in words:
                        split_list=word["orth"].split('-')
                        split_list_initial='-'.join(split_list[:-1])
                        if (split_list_initial in specials_eu and not any(word["orth"].startswith(special_eu) for special_eu in filter(lambda x:x.startswith(split_list_initial+'-'),specials_eu))) or re.search('[^0-9\-]',word["orth"])==None:
                            orth_list.append(word["orth"])
                        else:
                            for wordpart in split_list:
                                orth_list.append(wordpart)
    return orth_list




if __name__ == "__main__":
    input = {
        "lang": "eu",
        "original_text": "test",
        "paragraphs": [
            {
                "sentences": [
                    {
                        "phrases": [
                            {
                                "tokens": [
                                    {
                                        "words": [
                                            {
                                                "orth": "test",
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
    

    lang = "eu"
    log.log_level = "debug"

    #HB voice['name'] is used in synthesise?
    voice = {"name": "ahotts-eu-female"}
    #voice = "ahotts-eu-female"
    
    (audio_url, tokens) = synthesise(lang, voice, input)
    log.debug("AUDIO URL: %s" % audio_url)
    log.debug("TOKENS: %s" % tokens)
