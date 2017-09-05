CNAME="marytts"
if docker container inspect $CNAME &> /dev/null ; then
    echo -n "STOPPING CONTAINER "
    docker stop $CNAME
    echo -n "DELETING CONTAINER "
    docker rm $CNAME
fi

docker run --name=$CNAME -p 59125:59125 -ti marytts
