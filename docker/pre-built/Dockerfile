FROM debian

RUN apt-get update -y && apt-get upgrade -y && apt-get install apt-utils -y 
RUN apt-get install -y opus-tools python3-pip git netcat

# FOR DEBUGGING
RUN apt-get install -y libnet-ifconfig-wrapper-perl/stable curl emacs
    
RUN pip3 install simplejson requests flask flask_cors
    
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

