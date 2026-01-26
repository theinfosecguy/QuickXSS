# QuickXSS

> Automate XSS discovery by chaining **waybackurls**, **gau**, **gf**, and **dalfox**.

[![CI](https://github.com/theinfosecguy/QuickXSS/actions/workflows/ci.yml/badge.svg)](https://github.com/theinfosecguy/QuickXSS/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/quickxss)](https://pypi.org/project/quickxss/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Quick Start

```bash
pip install quickxss
quickxss setup --install      # Auto-install gf, dalfox, waybackurls, gau
quickxss scan -d testphp.vulnweb.com
```

## Installation

```bash
pip install quickxss
```

Or with pipx:

```bash
pipx install quickxss
```

## Usage

```bash
quickxss scan -d testphp.vulnweb.com                    # Basic scan
quickxss scan -d testphp.vulnweb.com -b blind.xss.ht    # With blind XSS callback
quickxss scan -d testphp.vulnweb.com -o results.txt     # Custom output name
quickxss setup                                          # Check dependencies
quickxss setup --install                                # Auto-install missing deps
```

## Docker

```bash
docker build -t quickxss .
docker run --rm -it quickxss scan -d testphp.vulnweb.com
```

## Output

Results saved to `results/<domain>/`:

| File | Description |
|------|-------------|
| `<domain>.txt` | Raw URL collection |
| `<domain>_xss.txt` | Candidate URLs for testing |
| `results.txt` | Dalfox findings |

## Development

```bash
pytest                                    # Run tests
QUICKXSS_INTEGRATION=1 pytest -m integration  # Integration tests
make isort                                # Sort imports
make lint                                 # Run linter
```

## License

[MIT](LICENSE)
