"""Follows a road lane through GeoPackage data."""

from pathlib import Path
from typing import List, Tuple
import argparse
import sqlite3

import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt


Node = Tuple[int, int]

def follow_lane(source: Path, start: List[int], output: List[Path]) -> None:
    """Follows a lane."""
    output_types = {o.suffix: o for o in output}

    g = build_graph(source)
    if '.graphml' in output_types:
        nx.write_graphml(g, output_types['.graphml'])
        print(f"Wrote graph to {output_types['.graphml']}.")


    start_node = tuple(start)
    lanes_forward: List[Node] = sorted(nx.descendants(g, start_node))
    fids_forward: List[int] = [l[0] for l in lanes_forward]
    lanes_backward: List[Node] = sorted(nx.ancestors(g, start_node))
    fids_backward: List[int] = [l[0] for l in lanes_backward]

    fig, ax = plt.subplots(1, 1)

    gdf = gpd.read_file(source, layer='road_segments')
    print(gdf.crs)
    gdf_start = gdf[gdf.index.isin([start_node[0]])]
    gdf_forward = gdf[gdf.index.isin(fids_forward)]
    gdf_backward = gdf[gdf.index.isin(fids_backward)]
    gdf_start.plot(ax=ax, label="Start", color='black')
    if len(gdf_forward) > 0:
        gdf_forward.plot(ax=ax, label="Forward", color='blue')
    if len(gdf_backward) > 0:
        gdf_backward.plot(ax=ax, label="Backward", color='orange')
    fig.tight_layout()
    plt.show()

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
        help="GeoPackage source path",
        type=Path,
        required=True,
    )
    parser.add_argument('--start',
        help="Node to start following from",
        nargs=2,
        metavar=('fid', 'lane'),
        type=int
    )
    parser.add_argument('--output',
        help="Output path(s) (supports .graphml)",
        nargs='+',
        type=Path,
        default=[]
    )
    args = parser.parse_args()
    follow_lane(args.source, args.start, args.output)
