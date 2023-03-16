#!/usr/bin/bash

for group in $(az group list | jq --raw-output '.[].name')
do 
    az group delete -y --resource-group $group
done

