"""Run the independent satellite and ground demonstrations."""

import argparse
import subprocess
import sys
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', choices=('all', 'satellite', 'ground'), default='all')
    args = parser.parse_args()
    if args.source in ('all', 'satellite'):
        folder = root / 'satellite_insar'
        subprocess.run([sys.executable, str(folder / 'scripts/run_demo.py')], cwd=folder, check=True)
    if args.source in ('all', 'ground'):
        folder = root / 'ground_rldv'
        subprocess.run([sys.executable, str(folder / 'examples/read_data.py')], cwd=folder, check=True)


if __name__ == '__main__':
    main()
