#!/usr/bin/env bash
cd $( dirname $0 )
if [[ ! -d venv ]];then
    rm -f venv
    mkdir venv
    virtualenv venv
fi
. venv/bin/activate
[[ -f ./requirements.txt ]] && pip install -r ./requirements.txt
[[ -f ./requirements_gunicorn.txt ]] && pip install -r ./requirements_gunicorn.txt
cd ..
gunicorn --timeout 120 --workers 4 --pid ./twitterservice --log-level=DEBUG -b 0.0.0.0:5431 twitterservice:app
