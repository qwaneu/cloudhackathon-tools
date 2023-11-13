#!/bin/bash

username=$1
password=$2

usage() {
    echo $1
    echo "usage: $0 <username> <password>"
    exit 1
}

[[ "$username" == "" ]] && usage "no username given"
[[ "$password" == "" ]] && usage "no password given"

az ad user create --display-name ${username} --password "${password}" --user-principal-name "${username}@westghost.onmicrosoft.com"
az ad group create --display-name ${username}s --mail-nickname ${username}s
az ad group member add -g ${username}s --member-id $(az ad user show --id ${username}@westghost.onmicrosoft.com  --query objectId | tr \" " ")
