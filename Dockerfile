# Download sttsse/wikispeech_base from hub.docker.com | source repository: https://github.com/stts-se/wikispeech_base.git
FROM sttsse/wikispeech_base

WORKDIR "/"

RUN git clone https://github.com/stts-se/wikispeech_mockup.git

RUN mkdir -p /wikispeech_mockup/wikispeech_server/tmp
RUN ln -s /wikispeech_mockup/docker/ws-postponed-start /bin/
RUN ln -s /wikispeech_mockup/docker/config /config


## RUNTIME SETTINGS

EXPOSE 10000
WORKDIR "/wikispeech_mockup"
CMD python3 bin/wikispeech config/docker.conf

