NETWORKARGS="--network=wikispeech" # --name=pronlexSend --env SEND_HOST=pronlexListen --env SEND_PORT=8787"
docker run --name=wikispeech $NETWORKARGS -p 10000:10000 -v /home/hanna/git_repos/wikispeech_mockup/wikispeech_server/:/config/ -it wikispeech_server $*

## TODO: SNYGGARE MAPPNING AV CONFIGFILER!


