## Docker compose 

WORK IN PROGRESS

Utilities and info for building and running the Wikispeech server using [Docker Compose](https://docs.docker.com/compose/).

### I. Install Docker Compose

_Requires Docker CE: https://docs.docker.com/engine/installation/_

Docker Compose Installation: https://docs.docker.com/compose/install/   

Sample installation command for Linux version 1.16.1 (latest version as of 2017-09-06):   
  
    sudo -i curl -L https://github.com/docker/compose/releases/download/1.16.1/docker-compose-Linux-x86_64 -`uname -s`-`uname -m` -o /usr/local/bin/docker-compose

### II. Clone the Wikispeech git repository

TODO: Should NOT be needed in the future -- move Docker stuff to a separate repository?

`$ mkdir -p ~/gitrepos`    
`$ cd ~/gitrepos`   
`$ git clone https://github.com/stts-se/wikispeech_mockup.git`

### III. Start using wikispeech

1. Create environment variables

   `$ cd ~/gitrepos/stts-se/wikispeech_mockup/docker/compose`      
   `$ cp TEMPLATE.env .env`     
   
   Edit the variables in the `.env` file to match your system settings.


2. Setup standard lexicon data

   `$ docker-compose --file pronlex-import-all.yml up`


3. Run wikispeech
   
   `$ docker-compose --file wikispeech.yml up --abort-on-container-exit`

   To specify a separate compose-file:   
   `$ docker-compose --file wikispeech.yml up --abort-on-container-exit`

   Inspect the application:   
   `$ docker-compose config`


   
