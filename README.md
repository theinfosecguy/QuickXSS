# QuickXSS


Bash Script to Automate XSS using Waybackurls, GF, GF Patterns and Dalfox. 

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
https://github.com/theinfosecguy/QuickXSS.git
cd QuickXSS
chmod +x QuickXSS.sh
```

## Usage 

Provide your Target as the Argument

```
./QuickXSS target.com
```

### Special Thanks

Special Thanks to all these for their amazing tools ❤ : 
1. [TomNomNom](https://twitter.com/tomnomnom/) for Waybackurls and GF
2. [Shiv Chouhan](https://twitter.com/1ndianl33t) for GF Patterns
3. [HAHWUL](https://twitter.com/hahwul) for Dalfox
4. [Zemo](https://www.youtube.com/watch?v=fVBvqy-7Ug0) for his amazing video.

#### React out to me if you have any ideas to make this better via [Twitter](https://twitter.com/g0t_rOoT_)
