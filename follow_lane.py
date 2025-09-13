"""Follows a road lane through GeoPackage data."""

from pathlib import Path
import argparse


def follow_lane(source: Path, start_fid: int, start_lane) -> None:
    """Follows a lane starting with the provided fid and lane number."""
    print(source, start_fid, start_lane)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Follow Lane",
        description="Follows a road lane using GeoPackage data"
    )
    parser.add_argument('--source',
        help="Geopackage file",
        type=Path,
        required=True,
    )
    parser.add_argument('--fid',
        help="Feature id to start from",
        type=int,
        required=True,
    )
    parser.add_argument('--lane',
        help="Lane number to start from",
        type=int,
        required=True
    )
    args = parser.parse_args()

    follow_lane(args.source, args.fid, args.lane)
