"""Create fictional observations; no real monitoring records are used."""

import csv
import math
import random
from datetime import date, timedelta
from pathlib import Path


def main():
    rng = random.Random(731)
    target = Path(__file__).resolve().parents[1] / "data/sample/runway_displacement.csv"
    target.parent.mkdir(parents=True, exist_ok=True)
    start = date(2021, 1, 1)
    with target.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["point_id", "chainage_m", "offset_m", "date", "los_displacement_mm"])
        for index, chainage in enumerate(range(0, 3001, 50)):
            for lane, offset in enumerate([-20, 0, 20]):
                point_id = f"P{index * 3 + lane + 1:03d}"
                rate = -1.2 - 3.0 * math.exp(-((chainage - 1800) / 650) ** 2)
                rate += -0.6 * math.sin(chainage / 550) + 0.012 * offset
                phase = chainage / 1000 + offset / 40
                for epoch in range(16):
                    observed = start + timedelta(days=epoch * 90)
                    years = (observed - start).days / 365.25
                    seasonal = 0.45 * (math.sin(2 * math.pi * years + phase) - math.sin(phase))
                    displacement = 0.0 if epoch == 0 else rate * years + seasonal + rng.gauss(0, 0.12)
                    writer.writerow([point_id, chainage, offset, observed.isoformat(), f"{displacement:.4f}"])
    print(f"Created 2,928 synthetic observations: {target}")


if __name__ == "__main__":
    main()
