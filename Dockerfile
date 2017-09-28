FROM debian

RUN apt-get update -y && apt-get upgrade -y && apt-get install apt-utils -y

RUN apt-get install -y opus-tools python3-pip git netcat

# FOR DEBUGGING
RUN apt-get install -y libnet-ifconfig-wrapper-perl/stable curl emacs

RUN pip3 install simplejson requests flask flask_cors

RUN git clone https://github.com/stts-se/wikispeech_mockup.git 

RUN mkdir -p wikispeech_mockup/wikispeech_server/tmp
RUN ln -s /wikispeech_mockup/docker/ws-postponed-start /bin/
RUN ln -s /wikispeech_mockup/docker/config /config

RUN echo "172.99.0.1	localhost" >> /etc/hosts

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

EXPOSE 10000

# TODO: Specify config file?

CMD (cd wikispeech_mockup && python3 bin/wikispeech config/docker.conf)

