#! /bin/bash

set -e

echo -e "\e[1;31m
 ██████╗  ██╗   ██╗██╗ ██████╗██╗  ██╗    ██╗  ██╗███████╗███████╗
 ██╔═══██╗██║   ██║██║██╔════╝██║ ██╔╝    ╚██╗██╔╝██╔════╝██╔════╝
 ██║   ██║██║   ██║██║██║     █████╔╝      ╚███╔╝ ███████╗███████╗
 ██║▄▄ ██║██║   ██║██║██║     ██╔═██╗      ██╔██╗ ╚════██║╚════██║
 ╚██████╔╝╚██████╔╝██║╚██████╗██║  ██╗    ██╔╝ ██╗███████║███████║
  ╚══▀▀═╝  ╚═════╝ ╚═╝ ╚═════╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚══════╝╚══════╝
                                                                   
 \e[0m "


echo -e "\n\n"

echo -e "\e[1;34mCreating Directory for $1 .... \e[0m"

mkdir $1
cd $1

echo -e "\e[1;34m\nFinding URLs for $1 .... \n \e[0m"

echo "$1" | waybackurls | tee $1.txt

echo -e "\e[1;31m\nFinding valid URLs for XSS \n \e[0m"

cat $1.txt | gf xss | sed 's/=.*/=/' | sed 's/URL: //' | tee $1_temp_xss.txt

sort $1_temp_xss.txt | uniq | tee $1_xss.txt

dalfox file $1_xss.txt pipe -b $2
