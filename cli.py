"""Command line interface for modular arithmetic utilities."""

from __future__ import annotations

import json
from typing import Any

import typer

from modmath import (
    MultiplicativeOrderError,
    benchmark_modexp,
    modexp,
    multiplicative_order,
)

app = typer.Typer(
    add_completion=False,
    help=(
        "Efficient modular exponentiation and multiplicative order calculations.\n\n"
        "Examples:\n"
        "  python cli.py modexp --a 7 --e 560 --modulus 561\n"
        "  python cli.py order --a 4 --modulus 21\n"
        "  python cli.py bench --a 2 --e 1024 --modulus 101 --iterations 100"
    ),
    no_args_is_help=True,
)


def _echo_verbose(ctx: typer.Context, message: str) -> None:
    if ctx.obj and ctx.obj.get("verbose"):
        typer.echo(message, err=True)


@app.callback()
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose diagnostics."),
) -> None:
    """Initialize shared CLI state."""

    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose


@app.command("modexp")
def modexp_cmd(
    ctx: typer.Context,
    a: int = typer.Option(..., "--a", help="Base of the exponentiation."),
    e: int = typer.Option(..., "--e", help="Exponent (non-negative)."),
    modulus: int = typer.Option(..., "--modulus", help="Modulus (positive integer)."),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON instead of plain text."),
) -> None:
    """Compute a modular exponent."""

    try:
        result = modexp(a, e, modulus)
    except Exception as exc:  # pragma: no cover - defensive branch
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc

    _echo_verbose(ctx, f"Computed {a}^{e} mod {modulus} -> {result}")
    if json_output:
        typer.echo(json.dumps({"result": result}))
    else:
        typer.echo(str(result))


@app.command("order")
def order_cmd(
    ctx: typer.Context,
    a: int = typer.Option(..., "--a", help="Base value; must be coprime with the modulus."),
    modulus: int = typer.Option(..., "--modulus", help="Modulus (>= 2)."),
    max_iter: int | None = typer.Option(
        None,
        "--max-iter",
        help="Optional safety bound for the order search.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON instead of plain text."),
) -> None:
    """Determine the multiplicative order of a base modulo N."""

    try:
        order = multiplicative_order(a, modulus, max_iter=max_iter)
    except MultiplicativeOrderError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=2) from exc
    except Exception as exc:  # pragma: no cover - defensive branch
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc

    _echo_verbose(ctx, f"Order({a}, mod {modulus}) = {order}")
    if json_output:
        typer.echo(json.dumps({"order": order}))
    else:
        typer.echo(str(order))


@app.command()
def bench(
    ctx: typer.Context,
    a: int = typer.Option(..., "--a", help="Base for repeated exponentiation."),
    e: int = typer.Option(..., "--e", help="Exponent used during benchmarking."),
    modulus: int = typer.Option(..., "--modulus", help="Modulus for exponentiation."),
    iterations: int = typer.Option(100, "--iterations", help="Number of iterations to run."),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON instead of plain text."),
) -> None:
    """Benchmark the modular exponentiation routine."""

    try:
        result = benchmark_modexp(a, e, modulus, iterations=iterations)
    except Exception as exc:  # pragma: no cover - defensive branch
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc

    _echo_verbose(ctx, f"Benchmark completed in {result.elapsed_seconds:.6f}s")
    payload: dict[str, Any] = {
        "iterations": result.iterations,
        "elapsed_seconds": result.elapsed_seconds,
        "seconds_per_iteration": result.elapsed_seconds / result.iterations,
    }

    if json_output:
        typer.echo(json.dumps(payload))
    else:
        typer.echo(
            "Iterations: {iterations}\nElapsed (s): {elapsed:.6f}\nPer iteration (s): {per_iter:.6e}".format(
                iterations=payload["iterations"],
                elapsed=payload["elapsed_seconds"],
                per_iter=payload["seconds_per_iteration"],
            )
        )


def run() -> None:
    """Entrypoint for invoking the Typer application."""

    app()


if __name__ == "__main__":
    run()
