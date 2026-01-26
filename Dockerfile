FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV GOPATH=/root/go
ENV PATH="/root/go/bin:/usr/local/bin:/usr/local/sbin:/usr/sbin:/usr/bin:/sbin:/bin"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        golang-go \
    && rm -rf /var/lib/apt/lists/*

# Install Go-based tools
RUN go install github.com/tomnomnom/gf@latest \
    && go install github.com/tomnomnom/waybackurls@latest \
    && go install github.com/hahwul/dalfox/v2@latest \
    && go install github.com/lc/gau@latest

# Install GF patterns
RUN mkdir -p /root/.gf \
    && git clone --depth 1 https://github.com/tomnomnom/gf /tmp/gf \
    && cp -r /tmp/gf/examples/* /root/.gf/ \
    && git clone --depth 1 https://github.com/1ndianl33t/Gf-Patterns /tmp/Gf-Patterns \
    && cp -r /tmp/Gf-Patterns/*.json /root/.gf/ \
    && rm -rf /tmp/gf /tmp/Gf-Patterns

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir .

ENTRYPOINT ["quickxss"]
CMD ["scan", "--help"]
