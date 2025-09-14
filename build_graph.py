"""Builds a directed graph of lanes from GeoPackage data."""

from pathlib import Path
import argparse
import sqlite3
import networkx as nx

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
    parser = argparse.ArgumentParser(prog="Build Graph",
        description="Builds a directed graph of lanes from GeoPackage data"
    )
    parser.add_argument('--source',
        help="GeoPackage source path",
        type=Path,
        required=True,
    )
    parser.add_argument('--output',
        help="GraphML output path",
        type=Path,
        required=True,
    )
    args = parser.parse_args()

    graph = build_graph(args.source)
    nx.write_graphml(graph, args.output)
