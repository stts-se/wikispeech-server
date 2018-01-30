CMD=`basename $0`

hostname=`hostname`
defaultConfigFile="wikispeech_server/$USER-$hostname.conf"
configFile=$defaultConfigFile
uninit="<uninit>"
cacheDir="$uninit"
audioTmpDirVarName="audio_tmpdir"
quiet=0

printUsage() {
    echo "Usage:" 2>&1
    echo "  $ $CMD - clear audio cache specified in default config file $defaultConfigFile" 2>&1
    echo "  $ $CMD <config file> - clear audio cache in the specified config file (pattern *.conf)" 2>&1
    echo "  $ $CMD <folder> - clear specified folder" 2>&1
    echo "" 2>&1
    echo "Switches:" 2>&1
    echo " -h print help/usage and exit" 2>&1
    echo " -q quiet/non-interactive mode -- WILL DELETE WITHOUT ASKING!!" 2>&1
    echo "" 2>&1
}

while getopts "hq" opt; do
    case $opt in
	q) quiet="1" ;; #
	h) printUsage && exit 0 ;; # 
	\?) printUsage && exit 1
    esac
done

shift $(( OPTIND - 1 ))

readCacheDir() {
    cf=$1
    if [ -f $cf ]; then
	hasCacheDir=`cat $cf | egrep -c "$audioTmpDirVarName"`
	if [ $hasCacheDir -eq 1 ]; then
	    cacheDir=`cat $cf | egrep "$audioTmpDirVarName" | sed "s/${audioTmpDirVarName}: //"`
	else
	    echo "[$CMD] ERROR | no variable $audioTmpDirVarName in config file: $cf" 2>&1
	    echo "" 2>&1
	    printUsage
	    exit 1
	fi	
	else
	    echo "[$CMD] ERROR | no such file: $cf" 2>&1
	    echo "" 2>&1
	    printUsage
	    exit 1
    fi
}

numSuffixForNoun() {
    n=$1
    if [ $n -eq 1 ]; then
	suffix=""
    else
	suffix="s"
   fi
}

numSuffixForVerb() {
    n=$1
    if [ $n -eq 1 ]; then
	suffix="s"
    else
	suffix=""
   fi
}

## READ CACHEDIR FROM ARGS OR CONFIG FILE
if [ $# -eq 0 ]; then
    echo "[$CMD] using default config file: $configFile" 2>&1
    readCacheDir $configFile
    echo "[$CMD] using cache dir specified in config: $cacheDir" 2>&1	
elif [ $# -eq 1 ]; then
    isConfig=`echo $1 | egrep -c "\.conf$"`
    if [ $isConfig -eq 1 ]; then
	configFile=$1
	echo "[$CMD] using user specified config file: $configFile" 2>&1
	readCacheDir $configFile
	echo "[$CMD] using cache dir specified in config: $cacheDir" 2>&1	
    else
	cacheDir=$1
	echo "[$CMD] using user specified cache dir: $cacheDir" 2>&1	
    fi
else
    echo "[$CMD] ERROR | runs with zero or one argument, found: $*" 2>&1
    echo "" 2>&1
    printUsage
    exit 1
fi

## DELETE FILES FROM CACHEDIR
if [ -d $cacheDir ]; then
    echo -n "[$CMD] reading files in folder $cacheDir ..." 2>&1
    nFiles=`ls $cacheDir | wc -l`
    echo " done" 2>&1
    if [ $nFiles -eq 0 ]; then
	echo "[$CMD] $cacheDir is already empty" 2>&1
	exit 0
    else
	numSuffixForNoun $nFiles
	isYes="0"
	if [ $quiet -eq 1 ]; then
	    echo "[$CMD] deleting $nFiles file$suffix from folder $cacheDir -- DELETING WITHOUT ASKING!!" 2>&1
	    isYes="1";
	else
	    echo -n "[$CMD] delete $nFiles file$suffix from folder $cacheDir? [y/N] " 2>&1
	    read reply
	    isYes=`echo $reply|egrep -ic "^[y]$"`
	fi
	if [ $isYes == 1 ]; then
	    echo "[$CMD] clearing folder $cacheDir ..." 2>&1
	    rm -rf $cacheDir
	    mkdir $cacheDir
	    nFiles=`ls $cacheDir | wc -l`
	    if [ $nFiles -ne 0 ]; then
		numSuffixForNoun $nFiles
		files="file$suffix"
		numSuffixForVerb $nFiles
		remain="remain$suffix"				
		echo "[$CMD] WARNING | $nFiles $files still $remain in folder $cacheDir" 2>&1
	    fi
	else
	    echo "[$CMD] aborted, no files were deleted"
	fi
    fi
else
    echo "[$CMD] ERROR | $cacheDir is not a folder" 2>&1
    echo "" 2>&1
    printUsage
    exit 1
fi
