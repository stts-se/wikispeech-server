#Lexicon service

export GOPATH=/home/harald/go
cd $GOPATH/src/github.com/stts-se/pronlex/lexserver
sh ./lexserver.sh &

#Arabic vocalisation service
export GIT=/home/harald/git
cd $GIT/mishkal
python interfaces/web/mishkal-webserver.py &


#marytts
#export GIT=/home/harald/git
#Allow mishkal to start
sleep 2
cd $GIT/marytts
sh target/marytts-5.2-SNAPSHOT/bin/marytts-server



