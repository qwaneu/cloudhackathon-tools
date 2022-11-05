#!/bin/bash

if [[ "$1"  == "--help" ]]
then
  echo "usage $0 [remote machine ip, dns or ssh config name (defaults to catsndogs)]"
  exit 1
fi

remote_machine=${1:-catsndogs}

ssh ${remote_machine} /bin/bash << ENDOFINSTALL
  sudo apt-get update
  sudo apt-get install -y ca-certificates     curl     gnupg     lsb-release
  sudo mkdir -p /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  echo   "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  sudo apt-get update
  sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
  sudo addgroup $(whoami)  docker
ENDOFINSTALL

