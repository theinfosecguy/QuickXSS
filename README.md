# QuickXSS

Automate your XSS workflow by chaining **waybackurls**, **gau**, **gf**, and **dalfox**.

## Requirements

QuickXSS orchestrates external tools. Install these first:

- Python 3.12+

- [gf](https://github.com/tomnomnom/gf)
- [Gf-Patterns](https://github.com/1ndianl33t/Gf-Patterns)
- [dalfox](https://github.com/hahwul/dalfox)
- [waybackurls](https://github.com/tomnomnom/waybackurls)
- [gau](https://github.com/lc/gau)

Example (Go-based installs):

```bash
go install github.com/tomnomnom/gf@latest
go install github.com/tomnomnom/waybackurls@latest
go install github.com/hahwul/dalfox/v2@latest
go install github.com/lc/gau@latest

mkdir -p ~/.gf
git clone https://github.com/tomnomnom/gf /tmp/gf
cp -r /tmp/gf/examples/* ~/.gf/

git clone https://github.com/1ndianl33t/Gf-Patterns /tmp/Gf-Patterns
cp -r /tmp/Gf-Patterns/*.json ~/.gf/
```

## Install QuickXSS

Recommended with `pipx`:

```bash
pipx install .
```

Or with `pip`:

```bash
pip install .
```

## Usage

```bash
quickxss scan -d example.com
quickxss scan -d example.com -b blind.xss.ht
quickxss scan -d example.com -o results.txt
```

## Setup

Check dependencies:

```bash
quickxss setup
```

Install missing dependencies (macOS/Linux with brew/apt):

```bash
quickxss setup --install
```

On Windows, `setup` is check-only and prints manual install commands.

## Docker

Build and run using Docker:

```bash
docker build -t quickxss .
docker run --rm -it quickxss scan -d example.com
```

## Output

Results are stored under `results/<domain>/` by default:

- `<domain>.txt` (raw URL collection)
- `<domain>_temp_xss.txt` (gf output before de-dup)
- `<domain>_xss.txt` (candidate URLs)
- `results.txt` (dalfox output; always created)

## Development

Run tests:

```bash
pytest
```

Integration tests (requires external tools + network):

```bash
QUICKXSS_INTEGRATION=1 pytest -m integration
```

Sort imports:

```bash
isort quickxss tests
```

## License

MIT
