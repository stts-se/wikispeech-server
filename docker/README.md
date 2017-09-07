_For information on how to build the complete wikispeech server, please see the [wikispeech_compose](https://github.com/stts-se/wikispeech_compose/) repository._

## Docker installation

### I. Install Docker CE

1. Install Docker CE for your OS: https://docs.docker.com/engine/installation/   
   * Ubuntu installation: https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/

2. Make sure you set all permissions and groups as specified in the installation instructions above. Log out and log in again.

### II. Obtain a Docker image

Obtain a Docker image using one of the following methods

* Build from GitHub:

   `$ docker build https://github.com/stts-se/wikispeech_mockup.git -t wikispeech`   

* Build from local Dockerfile:

   `$ docker build <GIT>/wikispeech_mockup/ -t wikispeech`

Insert the `--no-cache` switch after the `build` tag if you encounter caching issues (e.g., with updated git repos, etc).


### III. Run the Docker app


`$ sh docker_run.sh <CONFIG DIR>`      
`<CONFIG DIR>` must contain valid config file: `docker.conf`

Suggested config dir: `<GIT>/wikispeech_mockup/docker/ws-config`

Requires `pronlex` and `marytts` servers up and running as specified in `docker.conf`.

