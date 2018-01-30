gitrepos=`ls -d $HOME/git* $HOME/private/git* 2> >(grep -v 'No such file' >&2) | egrep "(git|git_repos|gitrepos)$" | head -1`
if [ $gitrepos ]; then
    echo "gitrepos folder: $gitrepos"
else
    echo "No gitrepos folder found!"
    exit 1
fi

pronlex=`ls -d $gitrepos/pronlex ~/go/src/github.com/stts-se/pronlex 2> >(grep -v 'No such file' >&2) | egrep pronlex$`

if [ $pronlex ]; then
    echo -n ""
else
    echo "No pronlex folder found!"
    exit 1
fi
echo "pronlex folder: $pronlex"

echo "starting pronlex"
cd $pronlex/ && nohup bash install/start_server.sh ~/wikispeech/standalone &> pronlex.log &

echo "starting mishkal"
cd $gitrepos/mishkal/ && nohup python interfaces/web/mishkal-webserver.py &> mishkal.log &

echo "starting marytts"
cd $gitrepos/marytts && nohup ./gradlew run &> marytts.log &

echo "clearing wikispeech audio cache"
cd $gitrepos/wikispeech_mockup && bash clear_audio_cache.sh -q || exit 1

sleep=60
echo "waiting $sleep secs before starting main wikispeech server"
for i in `seq 1 $sleep`;
do
    echo -en "\r - time elapsed: ${i}s"; 
    sleep 1
done  
echo ""

echo "starting main wikispeech server"
cd $gitrepos/wikispeech_mockup && nohup python3 bin/wikispeech &> wikispeech.log &

echo ""
echo "check log files for process details"
echo " - in each git folder : pronlex.log / mishkal.log / marytts.log / wikispeech.log"
