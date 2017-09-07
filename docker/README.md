## Docker build

`$ docker build <GIT>/wikispeech_mockup/docker/wikispeech/ -t wikispeech`

## Docker run

`$ sh docker_run.sh <CONFIG DIR>`      
`<CONFIG DIR>` must contain valid config file: `docker.conf`

Suggested config dir: `<GIT>/wikispeech_mockup/docker/ws-config`

Requires `pronlex` and `marytts` servers up and running as specified in `docker.conf`.

