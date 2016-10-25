#!/bin/bash

#Paths
export GOPATH=/home/harald/go
export GIT=/home/harald/git

#Lexicon service
cd $GOPATH/src/github.com/stts-se/pronlex/lexserver
go run *.go &

#Arabic vocalisation service
cd $GIT/mishkal
python interfaces/web/mishkal-webserver.py &


#marytts
#Allow mishkal to start
sleep 2
cd $GIT/marytts
sh target/marytts-5.2-SNAPSHOT/bin/marytts-server &

