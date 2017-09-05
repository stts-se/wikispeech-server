Work in progress!! Currently, for some reason, the container cannot be called from outside, which makes it unusable....

## Docker build

`$ cd <GIT>/wikispeech_mockup/docker/wikispeech`
`$ docker build . -t wikispeech`

## Docker run

`$ sh docker_run.sh <CONFIG DIR>'    
`<CONFIG DIR> must contain valid config file: docker.conf`

Requires `pronlex` lexicon server and `marytts` server up and running.

