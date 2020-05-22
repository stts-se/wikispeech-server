FROM buildpack-deps

############# INITIAL SETUP/INSTALLATION #############
# non-root user
RUN useradd -m -u 8877 wikispeech

# setup apt
RUN apt-get update -y && apt-get upgrade -y && apt-get install apt-utils -y

# debugging tools
# RUN apt-get install -y libnet-ifconfig-wrapper-perl/stable curl wget emacs

# RELEASE variable (to be set by build args)
ARG RELEASE="undefined"

LABEL "se.stts.vendor"="STTS - Speech technology services - http://stts.se"
LABEL "se.stts.release"=$RELEASE



############# COMPONENT SPECIFIC DEPENDENCIES #############
RUN apt-get install -y opus-tools python3-pip netcat
RUN pip3 install simplejson requests flask flask_cors pytz tzlocal
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8



############# WIKISPEECH #############
ENV BASEDIR /wikispeech/wikispeech_server
WORKDIR $BASEDIR

# local copy of https://github.com/stts-se/wikispeech_mockup.git 
COPY . $BASEDIR

RUN mkdir -p $BASEDIR/bin

WORKDIR $BASEDIR

RUN mkdir -p $BASEDIR/wikispeech_server/tmp
RUN ln -s $BASEDIR/docker/ws-postponed-start $BASEDIR/bin/


############# POST INSTALL #############
WORKDIR "/wikispeech"

# BUILD INFO
ENV BUILD_INFO_FILE $BASEDIR/build_info.txt
RUN echo "Application name: wikispeech"  > $BUILD_INFO_FILE
RUN echo -n "Build timestamp: " >> $BUILD_INFO_FILE
RUN date --utc "+%Y-%m-%d %H:%M:%S %Z" >> $BUILD_INFO_FILE
RUN echo "Built by: docker" >> $BUILD_INFO_FILE
RUN echo "Release: $RELEASE" >> $BUILD_INFO_FILE
RUN cat $BUILD_INFO_FILE


############# RUNTIME SETTINGS #############
WORKDIR $BASEDIR
RUN chown -R wikispeech.wikispeech /wikispeech
USER wikispeech
EXPOSE 10000

CMD python3 bin/wikispeech docker/config/docker.conf

