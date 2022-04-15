# QuickXSS

![](https://img.shields.io/badge/license-MIT-red)
![](https://img.shields.io/badge/PR's-Welcome-red)
![](https://img.shields.io/badge/version-2.0.0-red)
![](https://img.shields.io/github/contributors/theinfosecguy/QuickXSS?color=red)
![](https://img.shields.io/github/forks/theinfosecguy/QuickXSS?color=red)
![](https://img.shields.io/github/stars/theinfosecguy/QuickXSS?color=red)

<h1 align="center">
  <br>
  <a href=""><img src="https://user-images.githubusercontent.com/33570148/110236951-26880080-7f5f-11eb-9b92-4b6122478e33.png" alt="" width="400px;"></a>
</h1>

Bash Script to Automate XSS using Waybackurls, GF, GF Patterns and Dalfox. 

Here are their Repositories:

1. [GF](https://github.com/tomnomnom/gf)
2. [GF Patterns](https://github.com/1ndianl33t/Gf-Patterns)
3. [Dalfox](https://github.com/hahwul/dalfox)
4. [Waybackurls](https://github.com/tomnomnom/waybackurls)
5. [Gau](https://github.com/lc/gau)

## Pre-Requisites

Install Go in your Machine and then install required Tools.

For installing Go in your system:
```
sudo apt install -y golang
export GOROOT=/usr/lib/go
export GOPATH=$HOME/go
export PATH=$GOPATH/bin:$GOROOT/bin:$PATH
source .bashrc
```
## Install Tools in one go !

```
chmod +x install.sh
./install.sh
```

## Docker support

```bash
# for build docker image
$ docker build --tag quickxss .
# run docker image
$ docker run -it --rm --name qs quickxss
```


### For Installing Pre-Requisites (In case you want to do it one by one):
```
go get -u github.com/tomnomnom/gf
go get github.com/tomnomnom/waybackurls
GO111MODULE=on go get -v github.com/hahwul/dalfox/v2
GO111MODULE=on go get -u -v github.com/lc/gau
mkdir .gf
cp -r $GOPATH/src/github.com/tomnomnom/gf/examples ~/.gf
git clone https://github.com/1ndianl33t/Gf-Patterns
mv ~/Gf-Patterns/*.json ~/.gf
```

## Installation

```
git clone https://github.com/theinfosecguy/QuickXSS.git
cd QuickXSS
chmod +x QuickXSS.sh
```

## Usage 

Provide your Target & XSSHunter Payload as the Argument.
For generating XSS Hunter Payload: [Check This](https://xsshunter.com/)

```
QuickXSS Usage 

./QuickXSS.sh -d <target.com>
./QuickXSS.sh -d <target.com> -b <blindxss.xss.ht>
./QuickXSS.sh -d <target.com> -o xss_results.txt 
./QuickXSS.sh -d <target.com> -b <blindxss.xss.ht> -o xss_results.txt

```

### Special Thanks

Special Thanks to all these for their amazing tools ❤ : 
1. [TomNomNom](https://twitter.com/tomnomnom/) for Waybackurls and GF
2. [Shiv Chouhan](https://twitter.com/1ndianl33t) for GF Patterns
3. [HAHWUL](https://twitter.com/hahwul) for Dalfox
4. [Corben Leo]() for gau
4. [Zemo](https://www.youtube.com/watch?v=fVBvqy-7Ug0) for his amazing video.

### Support !

If QuickXSS helped you land a Bounty ! Support me & Buy me a Ko-Fi

[Buy Me a Ko-Fi](https://ko-fi.com/theinfosecguy)


#### React out to me if you have any ideas to make this better via [Twitter](https://twitter.com/g0t_rOoT_)
