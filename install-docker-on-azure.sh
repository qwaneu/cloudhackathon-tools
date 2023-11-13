#!/bin/bash

remote_machine=$1
password=$2

usage() {
    echo $1
    echo "usage: $0 <remote_machine> <password>"
    echo "       where remote machine will also be used as pair user name"
    exit 1
}

[[ "$remote_machine" == "" ]] && usage "no remote_machine given"
[[ "$password" == "" ]] && usage "no password given"


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
  sudo useradd ${remote_machine} -m -p ${password}
  sudo addgroup ${remote_machine} docker
ENDOFINSTALL

