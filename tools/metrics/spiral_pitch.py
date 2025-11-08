"""CLI for estimating the pitch of logarithmic spiral traces."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np

from utils.spiral_pitch import analyze_spiral_trace


def _parse_indices(value: str) -> int:
    try:
        index = int(value, 10)
    except ValueError as exc:  # pragma: no cover - defensive CLI parsing
        raise argparse.ArgumentTypeError(f"Invalid column index: {value!r}") from exc
    if index < 0:
        raise argparse.ArgumentTypeError("Column indices must be non-negative")
    return index


def _load_trace(
    source: str,
    *,
    delimiter: str | None,
    skip_rows: int,
    real_col: int,
    imag_col: int,
) -> np.ndarray:
    stream: Iterable[str] | str
    if source == "-":
        stream = sys.stdin
    else:
        stream = str(Path(source).expanduser())

    if skip_rows < 0:
        raise ValueError("skip_rows must be zero or positive")

    data = np.genfromtxt(stream, delimiter=delimiter, skip_header=skip_rows)
    if data.size == 0:
        raise ValueError("Input contains no numeric samples")

    if data.ndim == 1:
        if data.size % 2 != 0:
            raise ValueError(
                "Expected an even number of values when providing a single column"
            )
        data = data.reshape(-1, 2)

    if not 0 <= real_col < data.shape[1]:
        raise ValueError(
            f"Real component column {real_col} out of range for {data.shape[1]} columns"
        )
    if not 0 <= imag_col < data.shape[1]:
        raise ValueError(
            f"Imaginary component column {imag_col} out of range for {data.shape[1]} columns"
        )

    real = np.asarray(data[:, real_col], dtype=np.float64)
    imag = np.asarray(data[:, imag_col], dtype=np.float64)

    if np.isnan(real).any() or np.isnan(imag).any():
        raise ValueError("Trace contains NaN values; clean the input first")

    return real + 1j * imag


def _format_number(value: float, precision: int) -> str:
    return f"{value:.{precision}f}"


def _write_reconstruction(
    path: str,
    reconstruction: np.ndarray,
    *,
    delimiter: str | None,
    precision: int,
) -> None:
    output_path = Path(path).expanduser()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    real = np.real(reconstruction)
    imag = np.imag(reconstruction)
    magnitude = np.abs(reconstruction)
    theta = np.unwrap(np.angle(reconstruction))
    data = np.column_stack([real, imag, magnitude, theta])

    out_delim = "," if delimiter is None else delimiter
    header = "real,imag,magnitude,theta"
    fmt = [f"%.{precision}f"] * data.shape[1]
    np.savetxt(
        output_path,
        data,
        delimiter=out_delim,
        header=header,
        comments="",
        fmt=fmt,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Estimate the pitch and quality of logarithmic spiral traces. "
            "Provide a text file with complex samples (real and imaginary parts)."
        )
    )
    parser.add_argument(
        "path",
        help="Path to the data file (use '-' to read from stdin)",
    )
    parser.add_argument(
        "--delimiter",
        default=None,
        help="Column delimiter understood by numpy.genfromtxt (default: whitespace)",
    )
    parser.add_argument(
        "--skip-rows",
        type=int,
        default=0,
        help="Number of header rows to skip",
    )
    parser.add_argument(
        "--real-col",
        type=_parse_indices,
        default=0,
        help="Zero-based column index containing the real component (default: 0)",
    )
    parser.add_argument(
        "--imag-col",
        type=_parse_indices,
        default=1,
        help="Zero-based column index containing the imaginary component (default: 1)",
    )
    parser.add_argument(
        "--precision",
        type=int,
        default=6,
        help="Decimal precision for reported metrics (default: 6)",
    )
    parser.add_argument(
        "--reconstruction",
        help=(
            "Optional path to save the fitted spiral samples as CSV "
            "(columns: real, imag, magnitude, theta)"
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        trace = _load_trace(
            args.path,
            delimiter=args.delimiter,
            skip_rows=args.skip_rows,
            real_col=args.real_col,
            imag_col=args.imag_col,
        )
        pitch, spiralness, reconstruction = analyze_spiral_trace(trace)
    except (OSError, ValueError) as exc:  # pragma: no cover - CLI error path
        parser.error(str(exc))

    precision = max(args.precision, 0)
    pitch_per_turn = pitch * (2.0 * np.pi)

    print(f"samples: {trace.size}")
    print(f"pitch_per_radian: {_format_number(pitch, precision)}")
    print(f"pitch_per_turn: {_format_number(pitch_per_turn, precision)}")
    print(f"spiralness: {_format_number(spiralness, precision)}")

    if args.reconstruction:
        _write_reconstruction(
            args.reconstruction,
            reconstruction,
            delimiter=args.delimiter,
            precision=precision,
        )
        print(f"reconstruction_saved: {Path(args.reconstruction).expanduser()}")

    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
