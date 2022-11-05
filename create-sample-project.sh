#!/bin/bash

if [[ "$1"  == "--help" ]]
then
  echo "usage $0 [remote machine ip, dns or ssh config name (defaults to catsndogs)]"
  exit 1
fi

remote_machine=${1:-catsndogs}

ssh ${remote_machine} /bin/bash << ENDOFSCRIPT
sudo mkdir /home/catsndogs
sudo chmod 777 /home/catsndogs
cd /home/catsndogs
git clone https://github.com/dockersamples/example-voting-app
ENDOFSCRIPT
