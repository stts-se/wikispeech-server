## Docker compose 

WORK IN PROGRESS

General info: https://docs.docker.com/compose/   
Installation: https://docs.docker.com/compose/install/   

Latest Linux version for docker-compose (as of 2017-09-06):
https://github.com/docker/compose/releases/download/1.16.1/docker-compose-Linux-x86_64

Sample installation command for version 1.16.1:   
  
    sudo -i curl -L https://github.com/docker/compose/releases/download/1.16.1/docker-compose-Linux-x86_64 -`uname -s`-`uname -m` -o /usr/local/bin/docker-compose

Getting started: https://docs.docker.com/compose/gettingstarted/

Test setup for docker compose with pronlex, marytts and the wikispeech server.

### Config

Sample config file: `<GIT>/wikispeech_mockup/docker/ws-config/docker-compose.conf`

---
TODO: How do we know the docker internal IP addresses?
