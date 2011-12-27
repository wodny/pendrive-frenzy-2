#!/bin/sh

echo "==============="
echo "POST MBR SCRIPT"
echo "param: $1"
echo "==============="
/sbin/install-mbr "$1"
