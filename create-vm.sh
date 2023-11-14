#!/bin/bash

if [[ $# != 3 ]]
then
  echo "usage $0 <resource group name> <vm name> <password>
    choose vm name carefully as it is used for public domain in the form of:
    '<vm name>.westeurope.cloudapp.azure.com'"
  exit 2
fi

resource_group=$1
name=$2
password=$3

echo "creating vm:
name:           '$name' 
password:       '$password' 
resource group: '$resource_group'
domain name:    '${name}.westeurope.cloudapp.azure.com'
"

while [[ -z $REPLY ]]
do
  read -p "Is this ok? " -n 1 -r
  echo    # (optional) move to a new line
done
if ! [[ $REPLY =~ ^[Yy]$ ]]
then
  exit 0
fi

az vm create \
  --name ${name} \
  --resource-group ${resource_group} \
  --location westeurope \
  --image "Canonical:0001-com-ubuntu-server-jammy:22_04-lts-gen2:22.04.202211011" \
  --data-disk-delete-option Delete \
  --public-ip-address-dns-name ${name}
az vm user update -n ${name} -g $resource_group -u ${name} -p ${password}
az vm open-port --resource-group ${resource_group} --name ${name} --port 5000-5001

