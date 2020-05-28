#!/bash

set -e

CMD=`basename $0`

rundir=`pwd`

defaultlogdir=$rundir/log
defaultgitrepos=`ls -d $HOME/git* 2> >(grep -v 'No such file' >&2) | egrep "(git|git_repos|gitrepos)$" | head -1`
if [ -z $defaultgitrepos ]; then
    defaultgitrepos=$HOME/gitrepos
fi
defaultlexserverappdir="$HOME/wikispeech"    
defaultsleep=30

gitrepos=$defaultgitrepos
logdir=$defaultlogdir
lexserverappdir=$defaultlexserverappdir
sleep=$defaultsleep

printUsage() {
    echo "Usage:" 2>&1
    echo "  $ $CMD <gitroot> <pronlex> <lexserver appdir>" >&2
    echo "    -g gitroot - root folder for git repositories mishkal, marytts, ahotts, symbolset and wikispeech_mockup (default $defaultgitrepos)" >&2
    echo "    -d lexserver appdir - location of the lexserver installation (default $defaultlexserverappdir)" >&2
    echo "    -l logdir - log files folder (default $defaultlogdir)" >&2
    echo "    -s sleep - sleep seconds after starting sub-services before starting the main server (default $defaultsleep)" >&2
}

while getopts "hg:l:d:s:" opt; do
    case $opt in
	h) printUsage && exit 1;;
	g)
	    gitrepos=$OPTARG
	    ;;
	d)
	    lexserverappdir=$OPTARG
	    ;;
	l)
	    logdir=$OPTARG
	    ;;
	s)
	    sleep=$OPTARG
	    ;;
	\?) ERR=1 && echo "" >&2
    esac
done

shift $(expr $OPTIND - 1 )

if [ $# -ne 0 ]; then
    echo "[$CMD] Invalid option(s): $*" >&2
    exit 1
fi

if [ $gitrepos ] && [ -d $gitrepos ]; then
    echo -n ""
else
    echo "[$CMD] No gitrepos folder found in default location: $gitrepos"
    printUsage
    exit 1
fi

if [ $lexserverappdir ] && [ -d $lexserverappdir ]; then
    echo -n ""
else
    echo "[$CMD] No lexserver appdir found in default location: $lexserverappdir"
    printUsage
    exit 1
fi

mkdir -p $logdir

echo "[$CMD] gitrepos folder: $gitrepos" >&2
echo "[$CMD] lexserver appdir: $lexserverappdir" >&2
echo "[$CMD] logdir: $logdir" >&2

echo "[$CMD] starting pronlex" >&2
cd $gitrepos/pronlex/ && nohup bash scripts/start_server.sh -e sqlite -a $lexserverappdir &>> $logdir/pronlex.log &

echo "[$CMD] starting mapper" >&2
cd $gitrepos/symbolset/server && go run . -ss_files $lexserverappdir/symbol_sets &>> $logdir/mapper.log &

echo "[$CMD] starting mishkal" >&2
cd $gitrepos/mishkal/ && nohup python interfaces/web/mishkal-webserver.py &>> $logdir/mishkal.log &

echo "[$CMD] starting marytts" >&2
cd $gitrepos/marytts && nohup ./gradlew run &>> $logdir/marytts.log &

# echo "[$CMD] TESTING -- not starting ahotts, wikispeech" >&2 && exit 0

echo "[$CMD] starting ahotts" >&2
cd $gitrepos/AhoTTS-eu-Wikispeech && nohup sh start_ahotts_wikispeech.sh &>> $logdir/ahotts.log &

#echo "[$CMD] TESTING -- not starting wikispeech" && exit 0

echo "[$CMD] clearing wikispeech audio cache" >&2
cd $gitrepos/wikispeech_mockup && bash clear_audio_cache.sh -q || exit 1

echo "[$CMD] waiting $sleep secs before starting main wikispeech server" >&2
for i in `seq 1 $sleep`;
do
    echo -en "\r - time elapsed: ${i}s" >&2 ;
    sleep 1
done  
echo "" >&2

echo "[$CMD] starting main wikispeech server" >&2
cd $gitrepos/wikispeech_mockup && nohup python3 bin/wikispeech &>> $logdir/wikispeech.log &

echo ""
echo "[$CMD] check logs in folder $logdir for process details" >&2
