#!/bin/bash
echo $1 > SSID
echo $2 > CHANNEL
mpfshell -s mpfshellscript

