FROM openjdk

RUN apt-get update -y && apt-get upgrade -y && apt-get install apt-utils -y

# FOR DEBUGGING
RUN apt-get install -y libnet-ifconfig-wrapper-perl/stable wget

RUN git clone https://github.com/marytts/marytts-installer.git

RUN cd marytts-installer && ./marytts install:cmu-slt && ./marytts install:cmu-slt-hsmm && ./marytts install:dfki-spike-hsmm

RUN cd marytts-installer/installed && wget https://github.com/HaraldBerthelsen/marytts/releases/download/v5.9-alpha/marytts-lang-sv-6.0-SNAPSHOT.jar && wget https://github.com/HaraldBerthelsen/marytts/releases/download/v5.9-alpha/voice-stts_sv_nst-hsmm-5.2.jar && wget https://github.com/HaraldBerthelsen/marytts/releases/download/v5.9-alpha/marytts-lang-no-6.0-SNAPSHOT.jar && wget https://github.com/HaraldBerthelsen/marytts/releases/download/v5.9-alpha/voice-stts_no_nst-hsmm-5.2.jar

## ARABIC (doesn't work properly without the vocalizer)
RUN cd marytts-installer/installed && wget https://github.com/HaraldBerthelsen/marytts-lang-ar/releases/download/v0.1-alpha/marytts-lang-ar-6.0-SNAPSHOT.jar && wget https://github.com/HaraldBerthelsen/voice-ar-nah-hsmm/releases/download/v5.2/voice-ar-nah-hsmm-5.2.jar

EXPOSE 59125

CMD (cd marytts-installer && ./marytts)

