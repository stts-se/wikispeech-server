#!/bash

processNames="pronlex|wikispeech|marytts|tts_server|python ahotts-httpserver.py|mishkal"
cmd=`basename $0`

exclude="$cmd|git-receive-pack|docker.*build|installDist|grep .E PID"

psargs="--sort pid -Af"
pids=""
for proc in `ps $psargs | egrep "PID|$processNames" | sed 's/-cp .*//' | egrep -v "$exclude" | sed 's/  */\t/g' | sed 's/\t/¤/g'`; do
    proc=`echo $proc | tr '¤' '\t'`
    pid=`echo $proc | cut -f2 -d' '|egrep -v PID`
    pids="$pids $pid"
done

nPids="`echo $pids | tr ' ' '\012' | egrep -v "^$" | wc -l`"
if [ $nPids -ne 0 ]; then
    ps $psargs | egrep "PID|$processNames" | sed 's/-cp .*//' | egrep -v "$exclude" 2>&1
    echo ""
    echo "Kill all $nPids proccesses? $pids"
    echo -n " [y/N] "
    read reply
    isYes=`echo $reply|egrep -ic "^[y]$"`
    
    if [ $isYes == 1 ]; then
	echo -n "killing processes ..." 2>&1
	kill $pids
	echo " done" 2>&1
    fi
else
    echo "no wikispeech processes running" 2>&1
fi

