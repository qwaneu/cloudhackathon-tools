#!/bin/bash
set -e

if [[ $# != 1 ]]
then
  echo "usage $0 <pair-name>"
  exit 2
fi

pair_name=$1

az group create --location westeurope --resource-group ${pair_name}-group
./create-vm.sh ${pair_name}-group ${pair_name}
./install-docker-on-azure.sh ${pair_name} 
./install-gh-cli-on-azure.sh ${pair_name} 
./create-sample-project.sh ${pair_name}
