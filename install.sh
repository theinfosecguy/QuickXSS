#! /bin/bash

set -e

cyan="\e[0;36m"
end="\e[0m"

echo -e "$cyan
 ██████╗  ██╗   ██╗██╗ ██████╗██╗  ██╗    ██╗  ██╗███████╗███████╗
 ██╔═══██╗██║   ██║██║██╔════╝██║ ██╔╝    ╚██╗██╔╝██╔════╝██╔════╝
 ██║   ██║██║   ██║██║██║     █████╔╝      ╚███╔╝ ███████╗███████╗
 ██║▄▄ ██║██║   ██║██║██║     ██╔═██╗      ██╔██╗ ╚════██║╚════██║
 ╚██████╔╝╚██████╔╝██║╚██████╗██║  ██╗    ██╔╝ ██╗███████║███████║
  ╚══▀▀═╝  ╚═════╝ ╚═╝ ╚═════╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚══════╝╚══════╝
$end\n"

printf "Installing GF..\n"
go get -u github.com/tomnomnom/gf
printf "Installing waybackurls ..\n"
go get github.com/tomnomnom/waybackurls
printf "Installing Dalfox..\n"
go install github.com/hahwul/dalfox/v2@latest
printf "Installing gau..\n"
GO111MODULE=on go get -u -v github.com/lc/gau
printf "Setting up GF Patterns\n"
mkdir ~/.gf
cp -r $GOPATH/src/github.com/tomnomnom/gf/examples ~/.gf
cd ~
git clone https://github.com/1ndianl33t/Gf-Patterns
mv ~/Gf-Patterns/*.json ~/.gf
printf "Installation Completed Successfully."
