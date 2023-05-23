#!/bin/bash

echo "Installing loophost..."

if ! python3 -c 'import sys; assert sys.version_info >= (3,9)' > /dev/null; then
    echo "You need a newer version of python installed first."
    echo "We recommend following the instructions at https://docs.python-guide.org/starting/install3/osx/."
    open "https://docs.python-guide.org/starting/install3/osx/"
    exit 1
fi


python3 -m pip install loophost --upgrade
python3 -m loophost.postinstall
