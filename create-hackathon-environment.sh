#!/bin/bash
set -e

pair_name=$1
password=$2

usage() {
    echo $1
    echo "usage: $0 <pair_name>"
    exit 1
}

[[ "$pair_name" == "" ]] && usage "no pair_name given"
[[ "$password" == "" ]] && usage "no password given"


az group create --location westeurope --resource-group ${pair_name}-group
./create-vm.sh ${pair_name}-group ${pair_name} ${password}
./install-docker-on-azure.sh ${pair_name} 
./install-gh-cli-on-azure.sh ${pair_name} 
./create-sample-project.sh ${pair_name}
