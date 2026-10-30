"""Read the original exports and verify the public demonstration subset."""
from pathlib import Path
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parents[1]


def read_record(path):
    times, velocities = [], []
    with Path(path).open(encoding='gb18030') as stream:
        if next(stream).strip() != '时间(S) - 曲线0\tmm/s - 曲线0':
            raise ValueError(f'Unexpected header: {path}')
        for line_no, line in enumerate(stream, 2):
            t, v = map(float, line.split())
            if not (math.isfinite(t) and math.isfinite(v)):
                raise ValueError(f'Nonfinite number at line {line_no}')
            times.append(t)
            velocities.append(v)
    return times, velocities


def main():
    manifest = json.loads((ROOT/'data/manifest.json').read_text(encoding='utf-8'))
    records = manifest['records']
    if len(records) != 2 or {r['condition'] for r in records} != {'unballasted','ballasted'}:
        raise ValueError('Expected one record for each ballast state')
    count = 0
    for r in records:
        path = ROOT/r['path']
        if hashlib.sha256(path.read_bytes()).hexdigest() != r['sha256']:
            raise ValueError(f'Checksum mismatch: {path.name}')
        t, v = read_record(path)
        if len(v) != r['sample_count'] or not v:
            raise ValueError('Unexpected sample count')
        if any(b < a for a,b in zip(t,t[1:])):
            raise ValueError('Exported time decreases')
        rms = math.sqrt(sum(x*x for x in v)/len(v))
        if not math.isclose(rms,r['rms_velocity_mm_s'],rel_tol=1e-10):
            raise ValueError('RMS does not match manifest')
        print(f"{r['condition']:12s} | {len(v):,} samples | RMS {rms:.6f} mm/s")
        count += len(v)
    print(f'PASS: {len(records)} complete records, {count:,} samples; checksums and data verified.')


if __name__ == '__main__':
    main()
