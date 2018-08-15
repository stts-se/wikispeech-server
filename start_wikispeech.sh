#!/bash

set -e

CMD=`basename $0`

gitrepos=`ls -d $HOME/git* 2> >(grep -v 'No such file' >&2) | egrep "(git|git_repos|gitrepos)$" | head -1`
pronlex=`ls -d ~/go/src/github.com/stts-se/pronlex $gitrepos/pronlex 2> >(grep -v 'No such file' >&2) | egrep pronlex$`
lexserverappdir="$HOME/wikispeech/standalone"    

printUsage() {
    echo "Usage:" 2>&1
    echo "  $ $CMD <gitroot> <pronlex> <lexserver appdir>" 2>&1
    echo "    <gitroot> - root folder for git repositories mishkal, marytts, ahotts and wikispeech_mockup (default $gitrepos)" 2>&1
    echo "    <pronlex> - location of the pronlex git repository (default $pronlex)" 2>&1
    echo "    <lexserver appdir> - location of the lexserver installation (default $lexserverappdir)" 2>&1
}

while getopts "h" opt; do
    case $opt in
    h) printUsage && exit 1;;
    \?) ERR=1 && echo "" 2>&1
    esac
done

shift $(( OPTIND - 1 ))

if [ $# -eq 0 ]; then
    if [ $gitrepos ] && [ -d $gitrepos ]; then
	echo -n ""
    else
	echo "No gitrepos folder found in default location: $gitrepos"
	printUsage
	exit 1
    fi
    
    if [ $pronlex ] && [ -d $pronlex ]; then
	echo -n ""
    else
	echo "No pronlex folder found in default location: $pronlex"
	printUsage
	exit 1
    fi

    if [ $lexserverappdir ] && [ -d $lexserverappdir ]; then
	echo -n ""
    else
	echo "No lexserver appdir found in default location: $lexserverappdir"
	printUsage
	exit 1
    fi
elif [ $# -eq 3 ]; then
    gitrepos=$1
    pronlex=$2
    lexserverappdir=$3
else
    echo "[$CMD] invalid arguments: $*" 2>&1
    printUsage
    exit 1
fi

rundir=`pwd`
logdir=$rundir/log
mkdir -p $logdir

echo "gitrepos folder: $gitrepos"
echo "pronlex folder: $pronlex"
echo "lexserver appdir: $lexserverappdir"

echo "starting pronlex"
cd $pronlex/ && nohup bash install/start_server.sh -a $lexserverappdir &>> $logdir/pronlex.log &

echo "starting mishkal"
cd $gitrepos/mishkal/ && nohup python interfaces/web/mishkal-webserver.py &>> $logdir/mishkal.log &

echo "starting marytts"
cd $gitrepos/marytts && nohup ./gradlew run &>> $logdir/marytts.log &

echo "starting ahotts"
cp $gitrepos/wikispeech_mockup/start_ahotts_wikispeech.sh $gitrepos/AhoTTS-eu-Wikispeech/
cd $gitrepos/AhoTTS-eu-Wikispeech && nohup sh start_ahotts_wikispeech.sh &>> $logdir/ahotts.log &

# echo "TESTING -- not starting wikispeech" && exit 0

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
cd $gitrepos/wikispeech_mockup && nohup python3 bin/wikispeech &>> $logdir/wikispeech.log &

echo ""
echo "check log files for process details: $logdir"
