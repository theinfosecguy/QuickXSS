#! /bin/bash

set -e

cyan="\e[0;36m"
end="\e[0m"

# Banner
echo -e "$cyan
 ██████╗  ██╗   ██╗██╗ ██████╗██╗  ██╗    ██╗  ██╗███████╗███████╗
 ██╔═══██╗██║   ██║██║██╔════╝██║ ██╔╝    ╚██╗██╔╝██╔════╝██╔════╝
 ██║   ██║██║   ██║██║██║     █████╔╝      ╚███╔╝ ███████╗███████╗
 ██║▄▄ ██║██║   ██║██║██║     ██╔═██╗      ██╔██╗ ╚════██║╚════██║
 ╚██████╔╝╚██████╔╝██║╚██████╗██║  ██╗    ██╔╝ ██╗███████║███████║
  ╚══▀▀═╝  ╚═════╝ ╚═╝ ╚═════╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚══════╝╚══════╝
$end\n"
printf "By theinfosecguy.."

printf "Installing GF..\n"
go install github.com/tomnomnom/gf@latest
printf "Installing waybackurls ..\n"
go install github.com/tomnomnom/waybackurls@latest
printf "Installing Dalfox..\n"
go install github.com/hahwul/dalfox/v2@latest
printf "Installing gau..\n"
go install github.com/lc/gau/v2/cmd/gau@latest

printf "Setting up GF Patterns\n"
# Create directory for gf-patterns
if [ ! -d ~/.gf ]; then
    mkdir ~/.gf
fi
# Copy example gf patterns to gf directory
cp -r $GOPATH/pkg/mod/github.com/tomnomnom/gf@v0.0.0-20200618134122-dcd4c361f9f5/examples ~/.gf
cd ~

#Install GF Patterns
git clone https://github.com/1ndianl33t/Gf-Patterns
mv ~/Gf-Patterns/*.json ~/.gf

printf "Installation Completed Successfully."
