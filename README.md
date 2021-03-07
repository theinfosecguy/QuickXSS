# QuickXSS

![](https://img.shields.io/badge/license-MIT-red)
![](https://img.shields.io/badge/PR's-Welcome-red)
![](https://img.shields.io/badge/version-2.0.0-red)
![](https://img.shields.io/github/contributors/theinfosecguy/QuickXSS?color=red)
![](https://img.shields.io/github/forks/theinfosecguy/QuickXSS?color=red)
![](https://img.shields.io/github/stars/theinfosecguy/QuickXSS?color=red)

Bash Script to Automate XSS using Waybackurls, GF, GF Patterns and Dalfox. 

![Quick XSSr](https://user-images.githubusercontent.com/33570148/109413987-6fc3d780-79d6-11eb-9af2-bb58432fc151.png)

Here are their Repositories:

1. [GF](https://github.com/tomnomnom/gf)
2. [GF Patterns](https://github.com/1ndianl33t/Gf-Patterns)
3. [Dalfox](https://github.com/hahwul/dalfox)
4. [Waybackurls](https://github.com/tomnomnom/waybackurls)


## Pre-Requisites

 Install Go in your Machine and then use following commands.

```
go get -u github.com/tomnomnom/gf
go get github.com/tomnomnom/waybackurls
go get -u github.com/hahwul/dalfox
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
./QuickXSS.sh target.com your_payload.xss.ht
```

### Special Thanks

Special Thanks to all these for their amazing tools ❤ : 
1. [TomNomNom](https://twitter.com/tomnomnom/) for Waybackurls and GF
2. [Shiv Chouhan](https://twitter.com/1ndianl33t) for GF Patterns
3. [HAHWUL](https://twitter.com/hahwul) for Dalfox
4. [Zemo](https://www.youtube.com/watch?v=fVBvqy-7Ug0) for his amazing video.

### Support !

If QuickXSS helped you land a Bounty ! Support me & Buy me a Ko-Fi

[Buy Me a Ko-Fi](https://ko-fi.com/theinfosecguy)


#### React out to me if you have any ideas to make this better via [Twitter](https://twitter.com/g0t_rOoT_)
