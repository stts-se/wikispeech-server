import os, requests


url = "http://localhost:10000/wikispeech/?lang=sv&input=Det%20h%C3%A4r%20%C3%A4r%20ett%20test"


r = requests.get(url)
res = r.json()

audio_url = res["audio"]

#print(audio_url)


def saveAndConvertAudio(audio_url):

    r = requests.get(audio_url)
    print(r.headers['content-type'])

    audio_data = r.content

    tmpdir = "tmp"
    tmpfilename = "apa"
    tmpwav = "%s/%s.wav" % (tmpdir, tmpfilename)
    tmpopus = "%s/%s.opus" % (tmpdir, tmpfilename)

    fh = open(tmpwav, "wb")
    fh.write(audio_data)
    fh.close()

    convertcmd = "opusenc %s %s" % (tmpwav, tmpopus)
    os.system(convertcmd)

    return tmpopus


opus = saveAndConvertAudio(audio_url)
print(opus)
