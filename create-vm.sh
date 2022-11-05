#!/bin/bash

usage() {
  echo "usage $0 <resource group name> <vm name>"
  exit 2
}

if [[ $# != 2 ]]
then
  usage
fi

resource_group=$1
name=$2
az vm create \
  --name $name \
  --resource-group $resource_group \
  --location westeurope \
  --image "Canonical:0001-com-ubuntu-server-jammy:22_04-lts-gen2:22.04.202211011" \
  --data-disk-delete-option Delete \
  --public-ip-address-dns-name catsndogs
