#!/usr/bin/env bash
cd $( dirname $0 )
if [[ ! -d ./venv ]];then
    rm -f ./venv
    mkdir ./venv
    virtualenv ./venv
fi
. venv/bin/activate
[[ -f ./requirements.txt ]] && pip install -r ./requirements.txt
python manage.py runserver &
