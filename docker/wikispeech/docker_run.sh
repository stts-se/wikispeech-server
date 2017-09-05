CMD=`basename $0`
CONFIGNAME="docker.conf"

if [ $# -lt 1 ]; then
    echo "USAGE: sh $CMD <CONFIG DIR>
       <CONFIG DIR> must contain valid config file: $CONFIGNAME
" >&2
    exit 1
fi

DIR=$1
DIRABS=`realpath $DIR`

if [ ! -f $DIRABS/$CONFIGNAME ]; then
    echo "[$CMD] Config file $DIRABS/$CONFIGNAME is required!" >&2
    exit 1
fi

echo "[$CMD] Using config file: $DIRABS/$CONFIGNAME"

CNAME="wikispeech"
if docker container inspect $CNAME &> /dev/null ; then
    echo -n "[$CMD] STOPPING CONTAINER "
    docker stop $CNAME
    echo -n "[$CMD] DELETING CONTAINER "
    docker rm $CNAME
fi

shift
docker run --name=$CNAME -p 10000:10000 -v $DIRABS:/config/ -it wikispeech $*

## TODO: SNYGGARE MAPPNING AV CONFIGFILER


