"""Typer CLI entrypoint for QuickXSS."""

from __future__ import annotations

import typer

from quickxss.cli.scan import scan
from quickxss.cli.setup import setup

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.callback()
def root() -> None:
    """QuickXSS command line interface."""


app.command()(scan)
app.command()(setup)


def main() -> None:
    """CLI entrypoint."""

    app()


if __name__ == "__main__":
    main()
