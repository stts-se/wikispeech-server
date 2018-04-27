sleep=60
echo "waiting $sleep secs before starting main wikispeech server"
for i in `seq 1 $sleep`;
do
    echo -en "\r - time elapsed: ${i}s";
    sleep 1
done
echo ""

if sh clear_audio_cache.sh -q wikispeech_server/hanna-morf2010.conf; then
    python3 bin/wikispeech
else
    echo "Couldn't clear audio cache!" 1>&2
    exit 1
fi
