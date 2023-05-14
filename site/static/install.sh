#!/usr/bin/bash

TARGET_DIR=/etc/flingdev
SITE_PACKAGES_FOLDER=`python -c "import sysconfig; print(sysconfig.get_path('purelib'))"`

echo "Installing loophost..."
sudo mkdir -p $TARGET_DIR/certs && chown -R joshuamckenty $TARGET_DIR
pushd $TARGET_DIR
pip install fling-cli fling-hub uwsgi

fling auth
# Save the github username into apps.json
USERNAME=joshuamckenty

certbot certonly --authenticator fling-authenticator -d "*.$USERNAME.fling.dev" \
    --config-dir . --work-dir . --logs-dir . --fling_authenticator-propagation-seconds 30
cp "./live/$USERNAME.fling.dev/fullchain.pem" ./certs/$USERNAME.fling.dev.crt
cp "./live/$USERNAME.fling.dev/privkey.pem" ./certs/$USERNAME.fling.dev.key

cp $SITE_PACKAGES_FOLDER/fling_hub/hubconfig.ini ./
# cp $SITE_PACKAGES_FOLDER/fling_hub/flingroute.py ./
# cp $SITE_PACKAGES_FOLDER/fling_hub/logo-hc.txt ./
# TODO(don't clobber if it exists)!

echo "{\"apps\": {}, \"fqdn\": \"$USERNAME.fling.dev\"}" > loophost.json

sudo cp $SITE_PACKAGES_FOLDER/fling_hub/hub.plist /Library/LaunchDaemons/
popd