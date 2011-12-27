#!/bin/sh

echo "================"
echo "POST PART SCRIPT"
echo "param: $1"
echo "================"
extlinux --install "$1"
