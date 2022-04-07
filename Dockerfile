FROM alpine:latest

RUN apk add --no-cache git make musl-dev go
RUN apk add --no-cache --upgrade bash

# Configure Go
ENV GOROOT /usr/lib/go
ENV GOPATH /go
ENV PATH /go/bin:$PATH

RUN mkdir -p ${GOPATH}/src ${GOPATH}/bin

RUN mkdir -p /app
WORKDIR /app

COPY . .
RUN chmod +x ./install.sh
RUN ./install.sh

ENTRYPOINT [ "./QuickXSS.sh" ]