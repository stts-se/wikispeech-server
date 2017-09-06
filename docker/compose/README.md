## Docker compose 

WORK IN PROGRESS

Utilities and info for building and running the Wikispeech server using `docker-compose`.

### I. Install `docker-compose`

Requires Docker CE: https://docs.docker.com/engine/installation/

General info: https://docs.docker.com/compose/   
Installation: https://docs.docker.com/compose/install/   

Latest Linux version for docker-compose (as of 2017-09-06):
https://github.com/docker/compose/releases/download/1.16.1/docker-compose-Linux-x86_64

Sample installation command for version 1.16.1:   
  
    sudo -i curl -L https://github.com/docker/compose/releases/download/1.16.1/docker-compose-Linux-x86_64 -`uname -s`-`uname -m` -o /usr/local/bin/docker-compose

Getting started: https://docs.docker.com/compose/gettingstarted/

Test setup for docker compose with pronlex, marytts and the wikispeech server.

### II. Run wikispeech

1. Create environment variables

   `$ cp TEMPLATE.env $USER.env`     
   `$ ln -s $USER.env .env`
   
    Edit the variables in the `$USER.env` file to match your system settings.


2. Run wikispeech
   
   `$ docker-compose up --abort-on-container-exit`

   To specify a separate compose-file:   
   `$ docker-compose up -f docker-compose.yml --abort-on-container-exit`

   Inspect the application:   
   `$ docker-compose config`




---
TODO: How do we know the docker internal IP addresses?
