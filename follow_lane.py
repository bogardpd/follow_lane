"""Follows a road lane through GeoPackage data."""

from pathlib import Path
import argparse
import sqlite3


def follow_lane(source: Path, start_fid: int, start_lane) -> None:
    """Follows a lane starting with the provided fid and lane number."""
    con = sqlite3.connect(source)
    query = """
        SELECT
            from_segment_fid, from_lane_number,
            to_segment_fid, to_lane_number,
            crosses_paint
        FROM connectors
        WHERE from_segment_fid = :fid AND from_lane_number = :lane
    """
    cur = con.execute(query, {'fid': start_fid, 'lane': start_lane})
    results = cur.fetchall()
    if len(results) == 0:
        raise LookupError("Could not find fid/lane number combination")
    print(results)

    con.close()

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
