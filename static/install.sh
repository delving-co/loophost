#!/bin/bash

echo "Installing loophost..."

TARGET_DIR=~/.flingdev

pip install fling-cli fling-hub uwsgi
HUBDIR=`python -c "import os; import fling_hub; print(os.path.dirname(os.path.realpath(fling_hub.__file__)))"`

mkdir -p $TARGET_DIR/certs
pushd $TARGET_DIR
CWD=`pwd`

fling auth
if [ ! -f flinguser.txt ]
then
    echo "Authentication failed... loophost setup aborted."
    exit 1
fi
# Save the github username into apps.json
USERNAME=$(<flinguser.txt)

certbot certonly --non-interactive --expand --agree-tos -m webmaster@fling.dev \
     --authenticator fling_authenticator -d "*.$USERNAME.fling.dev"  -d "$USERNAME.fling.dev"\
    --config-dir . --work-dir . --logs-dir . --fling_authenticator-propagation-seconds 30
cp "./live/$USERNAME.fling.dev/fullchain.pem" ./certs/$USERNAME.fling.dev.crt
cp "./live/$USERNAME.fling.dev/privkey.pem" ./certs/$USERNAME.fling.dev.key

cp $HUBDIR/hubconfig.ini ./

if [ ! -f loophost.json ]
then 
    echo "{\"apps\": {}, \"fqdn\": \"$USERNAME.fling.dev\"}" > loophost.json
fi

# TODO(DEAL WITH MULTIPLE USERS)
cp $HUBDIR/loophost.plist.template ./
cp $HUBDIR/hub.plist.template ./
sed -e "s@\${USERNAME}@$USERNAME@" -e "s@\${CWD}@$CWD@" -e "s@\${HUBDIR}@$HUBDIR@" loophost.plist.template | sudo tee /Library/LaunchDaemons/dev.fling.hub.local.plist
sed -e "s@\${USERNAME}@$USERNAME@" -e "s@\${CWD}@$CWD@" -e "s@\${HUBDIR}@$HUBDIR@" hub.plist.template | sudo tee /Library/LaunchDaemons/dev.fling.hub.plist
sudo launchctl load /Library/LaunchDaemons/dev.fling.hub.local.plist
sudo launchctl load /Library/LaunchDaemons/dev.fling.hub.plist


popd