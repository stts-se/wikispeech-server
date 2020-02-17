# build script for Wikispeech
# mimic travis build tests, always run before pushing!

set -e

if [ $# -ne 0 ]; then
    echo "For developers: If you are developing for Wikispeech, and need to make changes to this repository, make sure you run a test build using build_and_test.sh before you make a pull request. Don't run more than one instance of this script at once, and make sure no pronlex server is already running on the default port."
    exit 0
fi


RELEASE=master

basedir=`dirname $0`
basedir=`realpath $basedir`
cd $basedir
builddir="${basedir}/.build"
mkdir -p .build

for proc in `ps --sort pid -Af|egrep 'pronlex|wikispeech|marytts|tts_server|ahotts|mishkal' | egrep -v 'docker.*build' | egrep -v  "grep .E"|sed 's/  */\t/g'|cut -f2`; do
    kill $proc || echo "Couldn't kill $pid"
done


## AHOTTS
cd $builddir
git clone https://github.com/Elhuyar/AhoTTS-eu-Wikispeech.git && cd AhoTTS-eu-Wikispeech || cd AhoTTS-eu-Wikispeech && git pull
git checkout $RELEASE || echo "No such release for ahotts. Using master."
if [ ! -f bin/tts_server ]; then
    sh script_compile_all_linux.sh && mkdir -p txt wav
fi
sh start_ahotts_wikispeech.sh &
export ahotts_pid=$!
echo "ahotts started with pid $ahotts_pid"
sleep 20
python ahotts_testcall.py "test call for ahotts"


## PRONLEX
cd $builddir
export GOPATH=`go env GOPATH`
export PATH=$PATH:$GOPATH/bin
cd $GOPATH/src/github.com/stts-se/
git clone https://github.com/stts-se/pronlex.git && cd pronlex || cd pronlex && git pull
git checkout $RELEASE || echo "No such release for pronlex. Using master."
go get ./...

rm -rf ${builddir}/appdir
bash install/setup.sh ${builddir}/appdir
echo ${builddir}/appdir
bash install/start_server.sh -a ${builddir}/appdir &
export pronlex_pid=$!
echo "pronlex started with pid $pronlex_pid"
sleep 20


## MARYTTS
cd $builddir
git clone https://github.com/stts-se/marytts.git && cd marytts || cd marytts && git pull
git checkout $RELEASE || echo "No such release for marytts. Using master."
 
./gradlew check
./gradlew assembleDist
./gradlew test
./gradlew run &
export marytts_pid=$!
echo "marytts started with pid $marytts_pid"
sleep 20


## WIKISPEECH FULL
cd $basedir && python3 bin/wikispeech docker/config/travis.conf &
export wikispeech_pid=$!  
echo "wikispeech started with pid $wikispeech_pid"
sleep 20


# FINALLY
sh $basedir/.travis/exit_server_and_fail_if_not_running.sh wikispeech $wikispeech_pid
sh $basedir/.travis/exit_server_and_fail_if_not_running.sh marytts $marytts_pid
sh $basedir/.travis/exit_server_and_fail_if_not_running.sh pronlex $pronlex_pid
 
# kill ahotts
#sh $basedir/.travis/exit_server_and_fail_if_not_running.sh ahotts $ahotts_pid
for proc in `ps -f --sort pid|egrep 'tts_server|ahotts|python' | egrep -v  "grep .E"|sed 's/  */\t/g'|cut -f2`; do
    kill $proc || echo "Couldn't kill $pid"
done

docker build . --no-cache -t sttsse/wikispeech:buildtest --build-arg RELEASE=$RELEASE


