processNames="pronlex|wikispeech|marytts|mishkal"
cmd=`basename $0`

#ps --sort pid -eo "%p	%a" -A | egrep "$processNames" | sed 's/-cp .*//' | egrep -v "grep .E" | egrep -v "$cmd" | sed 's/  */\t/g' | sed 's/\t/¤/g'

psargs="--sort pid -Af"
pids=""
for proc in `ps $psargs | egrep "$processNames|PID" | sed 's/-cp .*//' | egrep -v "grep .E" | egrep -v "$cmd" | sed 's/  */\t/g' | sed 's/\t/¤/g'`; do
    proc=`echo $proc | tr '¤' '\t'`
    pid=`echo $proc | cut -f2 -d' '|egrep -v PID`
    echo $proc
    pids="$pids $pid"
done

nPids="`echo $pids | tr ' ' '\012' | egrep -v "^$" | wc -l`"
if [ $nPids -ne 0 ]; then
    ps -Af --sort pid | egrep "PID|$processNames" | sed 's/-cp .*//' | egrep -v "grep .E" | egrep -v "$cmd" 2>&1
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

