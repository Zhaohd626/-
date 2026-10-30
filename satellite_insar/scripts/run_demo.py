"""Read point observations and produce basic displacement summaries and figures."""

import argparse
import csv
import math
from collections import defaultdict
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


REQUIRED = {"point_id", "chainage_m", "offset_m", "date", "los_displacement_mm"}


def load_observations(path):
    """Read the documented CSV schema and reject ambiguous point/date pairs."""
    groups = defaultdict(list)
    seen = set()
    positions = {}
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if not REQUIRED.issubset(reader.fieldnames or []):
            raise ValueError(f"Required columns: {', '.join(sorted(REQUIRED))}")
        for line, row in enumerate(reader, 2):
            point = row["point_id"].strip()
            observed = date.fromisoformat(row["date"])
            x, y, displacement = (float(row[key]) for key in ("chainage_m", "offset_m", "los_displacement_mm"))
            if not point or not all(math.isfinite(v) for v in (x, y, displacement)):
                raise ValueError(f"Invalid observation at line {line}")
            if (point, observed) in seen:
                raise ValueError(f"Duplicate point/date pair at line {line}")
            if point in positions and positions[point] != (x, y):
                raise ValueError(f"Position changes for point {point}")
            seen.add((point, observed))
            positions[point] = (x, y)
            groups[point].append((observed, x, y, displacement))
    if not groups:
        raise ValueError("The input contains no observations")
    for values in groups.values():
        values.sort(key=lambda item: item[0])
    return groups


def linear_rate(values):
    """Return an ordinary least-squares slope in mm/year."""
    if len(values) < 2:
        return None
    elapsed = [(item[0] - values[0][0]).days / 365.25 for item in values]
    mean_time = sum(elapsed) / len(elapsed)
    mean_value = sum(item[3] for item in values) / len(values)
    denominator = sum((t - mean_time) ** 2 for t in elapsed)
    return sum((t - mean_time) * (item[3] - mean_value) for t, item in zip(elapsed, values)) / denominator


def save_summaries(groups, output):
    with (output / "point_rate_summary.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["point_id", "chainage_m", "offset_m", "observations", "linear_rate_mm_per_year"])
        for point, values in sorted(groups.items()):
            rate = linear_rate(values)
            writer.writerow([point, values[0][1], values[0][2], len(values), "" if rate is None else f"{rate:.4f}"])


def draw_figures(groups, output):
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 160, "savefig.dpi": 220})
    colors = ["#4477AA", "#228833", "#CC6677"]
    latest = max(item[0] for values in groups.values() for item in values)
    profiles = defaultdict(list)
    for values in groups.values():
        for observed, x, y, displacement in values:
            if observed == latest:
                profiles[y].append((x, displacement))
    fig, ax = plt.subplots(figsize=(7.0, 4.2), layout="constrained")
    for index, (offset, values) in enumerate(sorted(profiles.items())):
        color = colors[index % len(colors)]
        values.sort()
        ax.plot([v[0] for v in values], [v[1] for v in values], color=color, linewidth=1.6, label=f"Offset {offset:g} m")
    ax.set(xlabel="Chainage (m)", ylabel="LOS displacement (mm)", title=f"Synthetic displacement profiles | {latest.isoformat()}")
    ax.grid(alpha=0.2)
    ax.legend(frameon=False, fontsize=9)
    fig.savefig(output / "displacement_profiles.png")
    plt.close(fig)

    centerline = sorted((values for values in groups.values() if values[0][2] == 0), key=lambda values: values[0][1])
    candidates = centerline or sorted(groups.values(), key=lambda values: values[0][1])
    selected = [candidates[round((len(candidates) - 1) * fraction)] for fraction in (1 / 6, 1 / 2, 5 / 6)]
    fig, ax = plt.subplots(figsize=(7.0, 4.2), layout="constrained")
    for color, values in zip(colors, selected):
        ax.plot([v[0] for v in values], [v[3] for v in values], "o-", color=color, markersize=3, linewidth=1.5, label=f"Chainage {values[0][1]:g} m")
    ax.set(xlabel="Observation date", ylabel="LOS displacement (mm)", title="Synthetic point displacement time series")
    ax.grid(alpha=0.2)
    ax.legend(frameon=False, fontsize=9)
    fig.savefig(output / "displacement_timeseries.png")
    plt.close(fig)


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=root / "data/sample/runway_displacement.csv")
    parser.add_argument("--output", type=Path, default=root / "outputs/demo")
    args = parser.parse_args()
    groups = load_observations(args.input)
    args.output.mkdir(parents=True, exist_ok=True)
    save_summaries(groups, args.output)
    draw_figures(groups, args.output)
    print(f"Processed {sum(map(len, groups.values())):,} observations at {len(groups)} points.")
    print(f"Results: {args.output.resolve()}")


if __name__ == "__main__":
    main()
