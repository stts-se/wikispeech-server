# Download wikispeech_base from hub.docker.com | source repository: https://github.com/stts-se/wikispeech_base.git
FROM sttsse/wikispeech_base

RUN git clone https://github.com/stts-se/wikispeech_mockup.git 

RUN mkdir -p wikispeech_mockup/wikispeech_server/tmp
RUN ln -s /wikispeech_mockup/docker/ws-postponed-start /bin/
RUN ln -s /wikispeech_mockup/docker/config /config

EXPOSE 10000

# TODO: Specify config file?

CMD (cd wikispeech_mockup && python3 bin/wikispeech config/docker.conf)

