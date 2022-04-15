FROM golang:1.18.1-alpine3.15

RUN apk update && apk add git

WORKDIR /quickxss

## install go packages
RUN go install github.com/tomnomnom/gf@latest
RUN go install github.com/tomnomnom/waybackurls@latest
RUN go install github.com/hahwul/dalfox/v2@latest
RUN go install github.com/lc/gau@latest
RUN mkdir ~/.gf
RUN git clone https://github.com/tomnomnom/gf
RUN git clone https://github.com/1ndianl33t/Gf-Patterns
RUN cp -r gf/examples ~/.gf/ && cp -r Gf-Patterns/*.json ~/.gf/
RUN rm -rf gf && rm -rf Gf-Patterns

COPY QuickXSS.sh .
RUN chmod +x QuickXSS.sh
RUN ls -la

ENTRYPOINT ["sh", "QuickXSS.sh"]