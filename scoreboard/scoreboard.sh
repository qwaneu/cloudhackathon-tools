#!/bin/bash

export PYTHONPATH=tests:src
. venv/bin/activate

python src/scoreboard.py $@

