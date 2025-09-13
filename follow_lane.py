"""Follows a road lane through GeoPackage data."""

from pathlib import Path
import argparse
import sqlite3
import networkx as nx


def follow_lane(source: Path, start_fid: int, start_lane) -> None:
    """Follows a lane starting with the provided fid and lane number."""
    print(source, start_fid, start_lane)
    g = build_graph(source)
    nx.write_graphml(g, source.with_suffix('.graphml'))

def build_graph(source: Path) -> nx.Graph:
    """Creates a directed graph from connectors data."""
    g = nx.DiGraph()
    con = sqlite3.connect(source)
    query = """
        SELECT from_segment_fid, from_lane_number,
        to_segment_fid, to_lane_number, crosses_paint
        FROM connectors
    """
    cur = con.execute(query)
    results = cur.fetchall()

    for r in results:
        n1 = (r[0],r[1]) # From (segment, lane) pair
        n2 = (r[2],r[3]) # To (segment, lane) pair
        g.add_node(n1, segment=str(r[0]), lane=str(r[1]))
        g.add_node(n2, segment=str(r[2]), lane=str(r[3]))
        g.add_edge(n1, n2, crosses_paint=r[4]==1)

    con.close()
    return g

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
