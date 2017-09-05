FROM debian

RUN apt-get update -y && apt-get upgrade -y && apt-get install apt-utils -y

RUN apt-get install -y opus-tools python3-pip git netcat

# DEBUG
RUN apt-get install -y libnet-ifconfig-wrapper-perl/stable curl

RUN pip3 install simplejson requests flask flask_cors

RUN git clone https://github.com/stts-se/wikispeech_mockup.git 

RUN mkdir -p wikispeech_mockup/wikispeech_server/tmp

RUN cp wikispeech_mockup/docker/wikispeech/ws-postponed-start /bin/
RUN chmod +x bin/ws-postponed-start

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

EXPOSE 10000

# TODO: Specify config file

CMD (cd wikispeech_mockup && python3 bin/wikispeech /config/docker.conf)

