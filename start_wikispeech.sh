CMD=`basename $0`

printUsage() {
    echo "Usage:" 2>&1
    echo "  $ $CMD <gitroot> <pronlex>" 2>&1
    echo "    <gitroot> - root folder for git repositories mishkal, marytts, ahotts and wikispeech_mockup (default \$HOME/gitrepos or \$HOME/git_repos or \$HOME/git)" 2>&1
    echo "    <pronlex> - location of the pronlex git repository (default \$HOME/go/src/github.com/stts-se/pronlex or <gitroot>/pronlex)" 2>&1
}

while getopts "h" opt; do
    case $opt in
    h) printUsage && exit 1;;
    \?) ERR=1 && echo "" 2>&1
    esac
done

shift $(( OPTIND - 1 ))

if [ $# -eq 0 ]; then
    gitrepos=`ls -d $HOME/git* 2> >(grep -v 'No such file' >&2) | egrep "(git|git_repos|gitrepos)$" | head -1`
    if [ $gitrepos ] && [ -d $gitrepos ]; then
	echo -n ""
    else
	echo "No gitrepos folder found in default location!"
	printUsage
	exit 1
    fi
    
    pronlex=`ls -d ~/go/src/github.com/stts-se/pronlex $gitrepos/pronlex 2> >(grep -v 'No such file' >&2) | egrep pronlex$`
    if [ $pronlex ] && [ -d $pronlex ]; then
	echo -n ""
    else
	echo "No pronlex folder found in default location!"
	printUsage
	exit 1
    fi
elif [ $# -eq 2 ]; then
    gitrepos=$1
    pronlex=$2
else
    echo "[$CMD] invalid arguments: $*" 2>&1
    printUsage
    exit 1
fi

echo "gitrepos folder: $gitrepos"
echo "pronlex folder: $pronlex"

echo "starting pronlex"
cd $pronlex/ && nohup bash install/start_server.sh -a ~/wikispeech/standalone &> pronlex.log &

echo "starting mishkal"
cd $gitrepos/mishkal/ && nohup python interfaces/web/mishkal-webserver.py &> mishkal.log &

echo "starting marytts"
cd $gitrepos/marytts && nohup ./gradlew run &> marytts.log &

echo "starting ahotts"
cd $gitrepos/AhoTTS-eu-Wikispeech && nohup bin/tts_server -IP=127.0.0.1 -Port=1200 &> ahotts.log &

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
echo " - in each git folder : pronlex.log / mishkal.log / marytts.log / ahotts.log / wikispeech.log"
