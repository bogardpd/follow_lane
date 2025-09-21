"""Follows a road lane through GeoPackage data."""

from pathlib import Path
from typing import List, Tuple
import argparse
import sqlite3

import pandas as pd
import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt


Node = Tuple[int, int]

def follow_lane(source: Path, start: List[int], output: List[Path]) -> None:
    """Follows a lane."""
    output_types = {o.suffix: o for o in output}

    # Load dataframes from source.
    con = sqlite3.connect(source)
    connectors = pd.read_sql_query("SELECT * FROM connectors", con)
    segments = gpd.read_file(source,
        layer='road_segments',
        engine='pyogrio', # Needed to use fid_as_index
        fid_as_index=True,
    )
    con.close()

    # Create directed graph.
    g = build_graph(connectors)
    if '.graphml' in output_types:
        nx.write_graphml(g, output_types['.graphml'])
        print(f"Wrote graph to {output_types['.graphml']}.")

    # Plot segments.
    if start is not None:
        plot_segments(g, segments, start)

def build_graph(connectors: pd.DataFrame) -> nx.DiGraph:
    """Creates a directed graph from connectors data."""
    g = nx.DiGraph()

    for _, r in connectors.iterrows():
        n1 = (r['from_segment_fid'], r['from_lane_number'])
        n2 = (r['to_segment_fid'], r['to_lane_number'])
        g.add_node(n1,
            segment=str(r['from_segment_fid']),
            lane=str(r['from_lane_number']),
        )
        g.add_node(n2,
            segment=str(r['to_segment_fid']),
            lane=str(r['to_lane_number']),
        )
        g.add_edge(n1, n2, crosses_paint=bool(r['crosses_paint']==1))

    return g

def plot_segments(g, segments, start):
    """Plots a graph of road segments from a starting node."""
    start_node = tuple(start)
    lanes_forward: List[Node] = sorted(nx.descendants(g, start_node))
    fids_forward: List[int] = [l[0] for l in lanes_forward]
    lanes_backward: List[Node] = sorted(nx.ancestors(g, start_node))
    fids_backward: List[int] = [l[0] for l in lanes_backward]

    fig, ax = plt.subplots(1, 1)

    gdf_start = segments[segments.index.isin([start_node[0]])]
    gdf_forward = segments[segments.index.isin(fids_forward)]
    gdf_backward = segments[segments.index.isin(fids_backward)]
    gdf_start.plot(ax=ax, label="Start", color='black')
    if len(gdf_forward) > 0:
        gdf_forward.plot(ax=ax, label="Forward", color='blue')
    if len(gdf_backward) > 0:
        gdf_backward.plot(ax=ax, label="Backward", color='orange')
    fig.tight_layout()
    plt.show()


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
