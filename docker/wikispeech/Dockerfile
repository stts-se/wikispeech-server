FROM debian

RUN apt-get update -y && apt-get upgrade -y && apt-get install apt-utils -y

RUN apt-get install -y curl opus-tools python3-pip git emacs

RUN pip3 install simplejson requests flask flask_cors

RUN git clone https://github.com/stts-se/wikispeech_mockup.git 

RUN mkdir -p wikispeech_mockup/wikispeech_server/tmp

EXPOSE 10000

CMD (cd wikispeech_mockup && python3 bin/wikispeech /config/hanna-maskineri.conf)

