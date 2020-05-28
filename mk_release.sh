#!/bash

set -e

CMD=`basename $0`

printUsage() {
    echo "USAGE: mk_release.sh <gitroot> <release-tag>"
}

if [ $# -ne 2 ]; then
    printUsage
    exit 1
fi

GITROOT=$1
#TAG="0.3.0beta4"
TAG=`echo $2 | sed 's/^\([0-9]\)/v\1/'`
shorttag=$TAG
longtag=$shorttag

echo "GITROOT: $GITROOT"
echo "RELEASE TAG: $TAG"


wikispeech=`ls -d $GITROOT/wikispeech*server 2> >(grep -v 'No such file' >&2) | head -1`
if [ $wikispeech ] && [ -d $wikispeech ]; then
    echo -n ""
else
    echo "[$CMD] No wikispeech git folder found in default location: $gitrepos/wikispeech-server or $gitrepos/wikispeech_server"
    printUsage
    exit 1
fi
echo "WIKISPEECH: $wikispeech"

if [ ! -d $GITROOT/pronlex ]; then
    echo "[$CMD] Couldn't find pronlex folder in $GITROOT" 1>&2
    exit 1  
fi

preReleaseActions() {
    echo ""
    echo "(1) PRE RELEASE ACTIONS"
    
    echo "     >> Merge completed branches to master, if any"
    echo ""

    echo "(2) UPDATE HARDWIRED RELEASE TAGS"
    
    declare -a files=("$wikispeech/.travis.yml" "$GITROOT/pronlex/.travis.yml" "$GITROOT/symbolset/.travis.yml" "$wikispeech/build_and_test.sh" "$GITROOT/pronlex/build_and_test.sh")
    
    cmd="sed -i 's/^\( *-\? *\)RELEASE=[^ ]*/\1RELEASE=$TAG/' ${files[@]}"
    echo "    $cmd"
    for file in "${files[@]}"; do
	file=`realpath $file`
    	dir=`dirname $file`
	name=`basename $file`
	echo "    cd $dir && git commit $name -m '$name release tag $TAG'"
    done
}

createReleaseTag() {
    echo ""
    echo "(3) COMMANDS FOR RELEASE TAGS - COPY AND RUN!"
    
    declare -a repos=("$GOHOME/pronlex" "$wikispeech" "$GITROOT/marytts" "$GITROOT/symbolset" "$GITROOT/ws-lexdata")
    
    tagcmd="git tag -a $shorttag -m \"$longtag\""
    pushcmd="git push origin $shorttag"

    for repo in "${repos[@]}"; do
	cmd="cd $repo && $tagcmd && $pushcmd"
	if [ $repo != ${repos[-1]} ]; then
	    cmd="$cmd && "
	fi
	echo "    $cmd"
    done
    echo ""
}

preReleaseActions
createReleaseTag

echo "(5) CREATE RELEASE NOTES"
echo " >> Add release notes to stts-se.github.io/wikispeech/release_notes.html"
echo ""

echo "(6) LINK RELEASE NOTES: Link release notes for all five repos on github.com"
echo " >> http://stts-se.github.io/wikispeech/release_notes.html#$TAG"
echo ""

