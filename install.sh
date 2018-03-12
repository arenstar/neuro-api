#!/usr/bin/env bash

echo "Install required packages"

case `uname` in
    Darwin )
        echo "OSX"
        ;;
    Linux )
        sudo apt-get update
        sudo apt-get install build-essential python-pip libffi-dev python-dev python3-dev libpq-dev
        ;;
    *)
    exit 1
    ;;
esac

type virtualenv >/dev/null 2>&1 || { echo >&2 "No suitable python virtual env tool found, aborting"; exit 1; }

rm -rf .venv
pyvenv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
