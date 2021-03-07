#! /bin/bash

set -e

bold="\e[1m"
version="1.2.0"
red="\e[1;31m"
green="\e[32m"
blue="\e[34m"
end="\e[0m"

echo -e "$red
 ██████╗  ██╗   ██╗██╗ ██████╗██╗  ██╗    ██╗  ██╗███████╗███████╗
 ██╔═══██╗██║   ██║██║██╔════╝██║ ██╔╝    ╚██╗██╔╝██╔════╝██╔════╝
 ██║   ██║██║   ██║██║██║     █████╔╝      ╚███╔╝ ███████╗███████╗
 ██║▄▄ ██║██║   ██║██║██║     ██╔═██╗      ██╔██╗ ╚════██║╚════██║
 ╚██████╔╝╚██████╔╝██║╚██████╗██║  ██╗    ██╔╝ ██╗███████║███████║
  ╚══▀▀═╝  ╚═════╝ ╚═╝ ╚═════╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚══════╝╚══════╝
$end "

printf "$bold$blue ** Developed by theinfosecguy ** \n\n$end"

contruct_mode(){
    echo -e "${green}Creating Directory for $1 ....$end";

    if [ -d "$1" ]; then
    printf "$red$1 Directory already exits. Please try again.\n\n$end";
    exit 1;
    fi

    mkdir $1
    cd $1

    echo -e "\nFinding URLs for $domain using Waybackurls ...."

    echo "$domain" | waybackurls | tee "$domain".txt >/dev/null 2>&1;
    printf "URLS fetched using waybackurls & Stored in $blue$domain.txt$end"
    printf "\n\nFinding URLs for $domain using gau ....\n"
    echo "$1" | gau | tee -a $1 >/dev/null 2>&1;
    printf "URLS fetched using gau & appended in $blue$domain.txt$end \n\n"

    echo -e "\nFinding valid URLs for XSS using GF Patterns \n"

    cat "$domain".txt | gf xss | sed 's/=.*/=/' | sed 's/URL: //' | tee "$domain"_temp_xss.txt >/dev/null 2>&1;

    sort "$domain"_temp_xss.txt | uniq | tee "$domain"_xss.txt >/dev/null 2>&1;
    printf "XSS Vulnerable URL's added to $blue"$domain"_xss.txt$end"
}

while [ -n "$1" ]; do
	case $1 in
		-d|--domain)
			domain=$2
			shift ;;
        -b|--blind)
			blind=$2
			shift 
            ;;
        -o| --output)
            out=$2
            shift
            ;;
		-h|--help)
			usage
            ;;
		-v|--version)
			echo "Version of QuickXSS: $version"
			exit 0 ;;
		*)
			echo "[-] Unknown Option: $1"
			usage ;;
	esac
	shift
done

contruct_mode "$domain"

if [ -z "$out"]
then
    $out="results.txt"
fi

if [ -z "$blind" ]
then
    echo "XSS Automation Started using Dalfox.."
    dalfox file $domain_xss.txt -o $out
else
    echo "XSS Automation Started using Dalfox with your Blind Payload.."
    dalfox file "$domain"_xss.txt -b $blind -o $out
fi

echo -e "XSS automation completed, Results stored in$blue $domain Directory $end"