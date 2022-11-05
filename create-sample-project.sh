#!/bin/bash

if [[ $# != 1 ]]
then
  echo "usage $0 <remote machine>
    where <remote machine> can be ip, dns or ssh config name"
  exit 1
fi

remote_machine=$1

ssh ${remote_machine} /bin/bash << ENDOFSCRIPT
sudo mkdir /home/catsndogs
sudo chmod 777 /home/catsndogs
cd /home/catsndogs
git clone https://github.com/dockersamples/example-voting-app
ENDOFSCRIPT
