"""Compute the logarithmic spiral pitch of a complex signal trace.

The pitch ``c = d ln r / d theta`` is estimated via linear regression on the
unwrapped phase ``theta`` and the logarithm of the magnitude ``r`` of the
complex samples.  This CLI is intentionally small so it can be wired into
experiments, notebooks, or quick terminal checks when exploring spiral
signatures across RF, vision, or control domains.

Example usage::

    $ python -m tools.metrics.spiral_pitch samples.csv --real real --imag imag

    $ python -m tools.metrics.spiral_pitch samples.csv --magnitude mag \
          --phase phase --phase-degrees

The input may contain a header row.  Columns can be referenced either by name
or by zero-based index.
"""
"""CLI for estimating the pitch of logarithmic spiral traces."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Sequence

import numpy as np

from tools.rf.spiral_loss import SpiralEstimate, spiral_pitch


def _read_csv(path: Path) -> tuple[list[str], list[list[float]]]:
    with path.open("r", newline="") as handle:
        reader = csv.reader(handle)
        headers: list[str] = []
        rows: list[list[float]] = []
        for idx, row in enumerate(reader):
            if idx == 0 and _row_is_header(row):
                headers = row
                continue
            if not row:
                continue
            try:
                rows.append([float(cell) for cell in row])
            except ValueError as exc:  # pragma: no cover - CLI level feedback
                raise ValueError(f"Non-numeric value on line {idx + 1}") from exc
    if not rows:
        raise ValueError("input file contains no numeric rows")
    return headers, rows


def _row_is_header(row: Sequence[str]) -> bool:
    for cell in row:
        try:
            float(cell)
            return False
        except ValueError:
            continue
    return True


def _coerce_column(value: str | None) -> str | int | None:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return value


def _resolve_column(headers: list[str], columns: list[list[float]], selector: str | int | None, label: str) -> np.ndarray:
    if selector is None:
        raise ValueError(f"{label} column must be provided")
    if isinstance(selector, int):
        index = selector
    else:
        if not headers:
            raise ValueError("column names supplied but the file has no header row")
        try:
            index = headers.index(selector)
        except ValueError as exc:
            raise ValueError(f"column '{selector}' not found in header {headers}") from exc
    try:
        data = np.asarray(columns[index], dtype=float)
    except IndexError as exc:
        raise ValueError(f"column index {index} out of range for input with {len(columns)} columns") from exc
    return data


def load_gamma(
    path: Path,
    real_column: str | int | None,
    imag_column: str | int | None,
    magnitude_column: str | int | None,
    phase_column: str | int | None,
    phase_degrees: bool,
) -> np.ndarray:
    """Load a complex array from ``path`` using the provided column selectors."""

    headers, rows = _read_csv(path)
    columns = list(zip(*rows))

    if real_column is not None and imag_column is not None:
        real = _resolve_column(headers, columns, real_column, "real")
        imag = _resolve_column(headers, columns, imag_column, "imaginary")
        gamma = real + 1j * imag
    elif magnitude_column is not None and phase_column is not None:
        mag = _resolve_column(headers, columns, magnitude_column, "magnitude")
        phase = _resolve_column(headers, columns, phase_column, "phase")
        if phase_degrees:
            phase = np.deg2rad(phase)
        gamma = mag * np.exp(1j * phase)
    else:
        raise ValueError("provide either real+imag or magnitude+phase columns")

    return gamma


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("samples", type=Path, help="CSV file containing complex samples")
    parser.add_argument("--real", dest="real", help="Real part column (name or zero-based index)")
    parser.add_argument("--imag", dest="imag", help="Imaginary part column (name or zero-based index)")
    parser.add_argument("--magnitude", dest="magnitude", help="Magnitude column (name or zero-based index)")
    parser.add_argument("--phase", dest="phase", help="Phase column (name or zero-based index)")
    parser.add_argument("--phase-degrees", action="store_true", help="Interpret phase column as degrees (default: radians)")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Suppress per-field breakdown when printing text output",
    )
    return parser


def format_text(path: Path, estimate: SpiralEstimate, summary_only: bool) -> str:
    lines: list[str] = [
        f"Samples: {path}",
        f"Pitch (d ln r / d theta): {estimate.pitch:+.6f}",
        f"Spiralness (0=circle, 1=ideal): {estimate.spiralness:.3f}",
    ]
    if not summary_only:
        lines.extend(
            [
                f"Slope (rho vs theta): {estimate.rho_slope:+.6f}",
                f"Intercept (rho vs theta): {estimate.rho_intercept:+.6f}",
            ]
        )
    return "\n".join(lines)
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

    real = _coerce_column(args.real)
    imag = _coerce_column(args.imag)
    magnitude = _coerce_column(args.magnitude)
    phase = _coerce_column(args.phase)

    try:
        gamma = load_gamma(
            path=args.samples,
            real_column=real,
            imag_column=imag,
            magnitude_column=magnitude,
            phase_column=phase,
            phase_degrees=args.phase_degrees,
        )
        estimate = spiral_pitch(gamma)
    except Exception as exc:  # pragma: no cover - CLI level error reporting
        parser.error(str(exc))
        return 2

    if args.json:
        payload = {"path": str(args.samples), **asdict(estimate)}
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(format_text(args.samples, estimate, summary_only=args.summary_only))
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


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
