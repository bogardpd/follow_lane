"""Follows a road lane through GeoPackage data."""

from pathlib import Path
import argparse
import networkx as nx
from build_graph import build_graph


def follow_lane(source: Path, start_fid: int, start_lane: int) -> None:
    """Follows a lane starting with the provided fid and lane number."""
    print(source, start_fid, start_lane)
    g = build_graph(source)
    print(g)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Follow Lane",
        description="Follows a road lane using GeoPackage data"
    )
    parser.add_argument('--source',
        help="GeoPackage source path",
        type=Path,
        required=True,
    )
    parser.add_argument('--fid',
        help="Feature id to start from",
        type=int,
        required=False,
    )
    parser.add_argument('--lane',
        help="Lane number to start from",
        type=int,
        required=False
    )
    args = parser.parse_args()

    follow_lane(args.source, args.fid, args.lane)
