# Download sttsse/wikispeech_base from hub.docker.com | source repository: https://github.com/stts-se/wikispeech_base.git
FROM sttsse/wikispeech_base

WORKDIR "/"

RUN git clone https://github.com/stts-se/wikispeech_mockup.git

RUN mkdir -p /wikispeech_mockup/wikispeech_server/tmp
RUN ln -s /wikispeech_mockup/docker/ws-postponed-start /bin/


# BUILD INFO
RUN echo -n "Build timestamp: " > /var/.wikispeech_build_info.txt
RUN date --utc "+%Y-%m-%d %H:%M:%S %Z" >> /var/.wikispeech_build_info.txt
RUN echo "Built by: docker" >> /var/.wikispeech_build_info.txt
RUN echo "Application name: wikispeech"  >> /var/.wikispeech_build_info.txt


## RUNTIME SETTINGS

EXPOSE 10000
WORKDIR "/wikispeech_mockup"

CMD python3 bin/wikispeech docker/config/docker.conf

