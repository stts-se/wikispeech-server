#!/bash

set -e

CMD=`basename $0`

rundir=`pwd`

defaultlogdir=$rundir/log
defaultgitrepos=`ls -d $HOME/git* 2> >(grep -v 'No such file' >&2) | egrep "(git|git_repos|gitrepos)$" | head -1`
if [ -z $defaultgitrepos ]; then
    defaultgitrepos=$HOME/gitrepos
fi
defaultlexserverappdir="$HOME/wikispeech/sqlite"
defaultsleep=20
#defaultmatchaconfig=config_stts.env
#defaultpiperconfig=config_sample.env
#defaulttextprocconfig=config_sample.env
#defaultwikispeechconfig=config-sample.conf
defaultmatchaconfig=""
defaultpiperconfig=""
defaulttextprocconfig=""
defaultwikispeechconfig=""

doTail=0
gitrepos=$defaultgitrepos
logdir=$defaultlogdir
lexserverappdir=$defaultlexserverappdir
matchaconfig=$defaultmatchaconfig
piperconfig=$defaultpiperconfig
textprocconfig=$defaulttextprocconfig
wikispeechconfig=$defaultwikispeechconfig
sleep=$defaultsleep

printUsage() {
    echo "Usage:" 2>&1
    echo "  $ $CMD <options>" >&2
    echo "    -g gitroot - root folder for git repositories symbolset, pronlex, wikispeech-tts-wrappers, wikispeech-server (default $defaultgitrepos)" >&2
    echo "    -d lexserver appdir - location of the lexserver installation (default $defaultlexserverappdir)" >&2
    echo "    -l logdir - log files folder (default $defaultlogdir)" >&2
    echo "    -s sleep - sleep seconds after starting sub-services before starting the main server (default $defaultsleep)" >&2
    echo "    -t textprocconfig - textproc config file (required)" >&2    
    echo "    -p piperconfig - piper config file (required)" >&2    
    echo "    -m matchaconfig - matcha config file (optional)" >&2
    echo "    -w wikispeechconfig - wikispeech config file (required)" >&2
    echo "    -T tail (follow) wikispeech log after startup" >&2
}

getoptsError=0

while getopts "hTg:l:d:s:m:p:t:w:" opt; do
    case $opt in
	h) printUsage && exit 1;;
	T) doTail=1;;
	g)
	    gitrepos=$OPTARG
	    ;;
	d)
	    lexserverappdir=`realpath $OPTARG`
	    ;;
	l)
	    logdir=$OPTARG
	    ;;
	s)
	    sleep=$OPTARG
	    ;;
	m)
	    matchaconfig=$OPTARG
	    ;;
	p)
	    piperconfig=$OPTARG
	    ;;
	t)
	    textprocconfig=$OPTARG
	    ;;
	w)
	    wikispeechconfig=$OPTARG
	    ;;
	\?) ERR=1 >&2 && getoptsError=1
    esac
done

shift $(expr $OPTIND - 1 )

if [ $# -ne 0 ]; then
    echo "[$CMD] Invalid option(s): $*" >&2
    getoptsError=1
fi

if [ -z $gitrepos ]; then
    echo "[$CMD] Missing required setting -g gitrepos"
    getoptsError=1  
elif [ $gitrepos ] && [ -d $gitrepos ]; then
    echo -n ""
else
    echo "[$CMD] No gitrepos folder found in default location: $gitrepos"
    getoptsError=1
fi

if [ -z $gitrepos ]; then
    echo "[$CMD] Missing required setting -l lexserverappdir"
    getoptsError=1  
elif [ $lexserverappdir ] && [ -d $lexserverappdir ]; then
    echo -n ""
else
    echo "[$CMD] No lexserver appdir found in default location: $lexserverappdir"
    getoptsError=1
fi

# if [ -z $matchaconfig ]; then
#     echo "[$CMD] Missing required flag -m matchaconfig"
#     getoptsError=1
# fi

if [ -z $piperconfig ]; then
    echo "[$CMD] Missing required flag -p piperconfig"
    getoptsError=1
fi

if [ -z $textprocconfig ]; then
    echo "[$CMD] Missing required flag -t textprocconfig"
    getoptsError=1
fi

if [ -z $wikispeechconfig ]; then
    echo "[$CMD] Missing required flag -w wikispeechconfig"
    getoptsError=1
fi

if [ $getoptsError -eq 1 ]; then
    printUsage
    exit 1
fi

if [[ $matchaconfig == *"/"* ]]; then
    matchaconfig=`realpath $matchaconfig`
fi

if [[ $piperconfig == *"/"* ]]; then
    piperconfig=`realpath $piperconfig`
fi

if [[ $textprocconfig == *"/"* ]]; then
    textprocconfig=`realpath $textprocconfig`
fi

if [[ $wikispeechconfig == *"/"* ]]; then
    wikispeechconfig=`realpath $wikispeechconfig`
fi

wikispeech=`ls -d $gitrepos/wikispeech*server 2> >(grep -v 'No such file' >&2) | head -1`
if [ $wikispeech ] && [ -d $wikispeech ]; then
    echo -n ""
else
    echo "[$CMD] No wikispeech git folder found in default location: $gitrepos/wikispeech-server or $gitrepos/wikispeech_server"
    printUsage
    exit 1
fi

mkdir -p $logdir

echo "[$CMD] gitrepos folder: $gitrepos" >&2
echo "[$CMD] wikispeech git folder: $wikispeech" >&2
echo "[$CMD] lexserver appdir: $lexserverappdir" >&2
echo "[$CMD] logdir: $logdir" >&2

echo "[$CMD] starting pronlex" >&2
cd $gitrepos/pronlex/ && nohup bash scripts/start_server.sh -e sqlite -a $lexserverappdir &> $logdir/pronlex.log &

echo "[$CMD] starting symbolset mapper" >&2
if [ ! -d "$lexserverappdir/symbol_sets" ]; then
    echo "[$CMD] No symbolset dir found in lexserverappdir $lexserverappdir"
    printUsage
    exit 1
fi
cd $gitrepos/symbolset/server && ./server -ss_files $lexserverappdir/symbol_sets &> $logdir/mapper.log &


if [ -z $matchaconfig ]; then
    echo "[$CMD] not starting matcha-tts (no matchaconfig set)" >&2
else
    echo "[$CMD] starting matcha-tts using config file $matchaconfig" >&2
    cd $gitrepos/wikispeech-tts-wrappers/matcha_server
    source $PWD/.venv/bin/activate
    if [ ! -f $matchaconfig ]; then
	echo "[$CMD] matchaconfig $matchaconfig not found in $PWD"
	printUsage
	exit 1
    fi
    uvicorn matcha_server:app --env-file $matchaconfig --port 8009 &> $logdir/matcha.log &
fi

echo "[$CMD] starting piper-tts using config file $piperconfig" >&2
cd $gitrepos/wikispeech-tts-wrappers/piper_server
source $PWD/.venv/bin/activate
if [ ! -f $piperconfig ]; then
    echo "[$CMD] piperconfig $piperconfig not found in $PWD"
    printUsage
    exit 1
fi
uvicorn piper_server:app --env-file $piperconfig --port 8010 &> $logdir/piper.log &

echo "[$CMD] starting textproc using config file $textprocconfig" >&2
cd $gitrepos/wikispeech-tts-wrappers/textproc
source $PWD/.venv/bin/activate
if [ ! -f $textprocconfig ]; then
    echo "[$CMD] textprocconfig $textprocconfig not found in $PWD"
    printUsage
    exit 1
fi
uvicorn textproc_server:app --env-file $textprocconfig --port 8011 &> $logdir/textproc.log &

# echo "[$CMD] TESTING -- not starting wikispeech" && exit 0

echo "[$CMD] clearing wikispeech audio cache" >&2
cd $wikispeech && bash clear_audio_cache.sh -q $wikispeechconfig || exit 1

echo "[$CMD] waiting $sleep secs before starting main wikispeech server" >&2
for i in `seq 1 $sleep`;
do
    echo -en "\r - time elapsed: ${i}s" >&2 ;
    sleep 1
done  
echo "" >&2

echo "[$CMD] starting main wikispeech server using config file $wikispeechconfig" >&2
cd $wikispeech
source $PWD/.venv/bin/activate
if [ ! -f $wikispeechconfig ]; then
    echo "[$CMD] wikispeechconfig $wikispeechconfig not found in $PWD"
    printUsage
    exit 1
fi
nohup python3 bin/wikispeech $wikispeechconfig &> $logdir/wikispeech.log &

echo ""
echo "[$CMD] check logs in folder $logdir for process details" >&2

if [ $doTail -eq 1 ]; then
    tail -f $logdir/wikispeech.log
fi
