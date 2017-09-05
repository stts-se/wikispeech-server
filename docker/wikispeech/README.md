Work in progress! Currently, for some reason, the container cannot be called from outside, which makes it unusable....

## Docker build

`$ docker build <GIT>/wikispeech_mockup/docker/wikispeech/ -t wikispeech`

## Docker run

`$ sh docker_run.sh <CONFIG DIR>`      
`<CONFIG DIR>` must contain valid config file: `docker.conf`

Requires `pronlex` and `marytts` servers up and running as specified in `docker.conf`.

