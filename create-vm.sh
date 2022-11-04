#!/bin/bash


az vm create \
  --name catsndocs \
  --resource-group catsndogs \
  --location westeurope \
  --image "Canonical:0001-com-ubuntu-server-jammy:22_04-lts-gen2:22.04.202211011" \
  --data-disk-delete-option Delete \
  --public-ip-address-dns-name catsndogs

