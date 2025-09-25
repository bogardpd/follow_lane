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

def follow_lane(
    source: Path,
    start: List[int],
    output: List[Path],
    allow_paint: bool = False,
) -> None:
    """Follows a lane."""
    output_types = {o.suffix: o for o in output}

    # Load dataframes from source.
    con = sqlite3.connect(source)
    connectors = pd.read_sql_query(
        "SELECT * FROM connectors",
        con,
        index_col='fid',
    )
    segments = gpd.read_file(source,
        layer='road_segments',
        engine='pyogrio', # Needed to use fid_as_index
        fid_as_index=True,
    )
    con.close()

    # Validate connectors.
    validate_connectors(connectors)

    # Create directed graph.
    g = build_graph(connectors, allow_paint)

    # Find loops.
    print("Finding segments with loops...")
    for node in g.nodes:
        looped_segs = [d for d in nx.descendants(g, node) if d[0] == node[0]]
        if len(looped_segs) > 0:
            print(
                f"{format_node(node)} → "
                f"{", ".join([format_node(ls) for ls in looped_segs])}"
            )
            nx.set_node_attributes(g, {node: True}, 'is_seg_loop_source')
            nx.set_node_attributes(
                g, {ls: True for ls in looped_segs}, 'is_seg_loop_sink',
            )
            looped_segs_same_lane = [l for l in looped_segs if l[1] == node[1]]
            if len(looped_segs_same_lane) > 0:
                print("\tSame lane!")

    # Export GraphML.
    if '.graphml' in output_types:
        nx.write_graphml(g, output_types['.graphml'])
        print(f"Wrote graph to {output_types['.graphml']}.")

    # Plot segments.
    if start is not None:
        plot_segments(g, segments, start)

def build_graph(
    connectors: pd.DataFrame,
    allow_paint: bool = False,
) -> nx.DiGraph:
    """Creates a directed graph from connectors data."""
    print("Building graph...")
    g = nx.DiGraph()

    for _, r in connectors.iterrows():
        crosses_paint = bool(r['crosses_paint'] == 1)
        if (not allow_paint) and crosses_paint:
            continue
        n1 = (int(r['from_segment_fid']), int(r['from_lane_number']))
        n2 = (int(r['to_segment_fid']), int(r['to_lane_number']))
        g.add_node(n1,
            segment=str(r['from_segment_fid']),
            lane=str(r['from_lane_number']),
            is_seg_loop_source = False,
            is_seg_loop_sink = False,
        )
        g.add_node(n2,
            segment=str(r['to_segment_fid']),
            lane=str(r['to_lane_number']),
            is_seg_loop_source = False,
            is_seg_loop_sink = False,
        )
        g.add_edge(n1, n2, crosses_paint=crosses_paint)

    print(f"Created {g}.")
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
    if len(gdf_backward) > 0:
        gdf_backward.plot(ax=ax, label="Backward", color='orange')
    if len(gdf_forward) > 0:
        gdf_forward.plot(ax=ax, label="Forward", color='blue')
    gdf_start.plot(ax=ax, label="Start", color='black', linewidth=4)
    fig.tight_layout()
    plt.show()

def validate_connectors(connectors: pd.DataFrame):
    """Checks connectors for errors."""

    df_con_val = connectors.copy()

    # Check if any connectors rows have null values.
    na_rows = df_con_val[df_con_val.isna().any(axis=1)]
    if len(na_rows) > 0:
        raise ValueError(
            f"Connector(s) with NA values: {na_rows.index.tolist()}"
        )

    # Check if any connectors have the same from and to segment.
    self_rows = df_con_val[
        df_con_val['from_segment_fid'] == df_con_val['to_segment_fid']
    ]
    if len(self_rows) > 0:
        raise ValueError(
            f"Connector(s) with same from and to: {self_rows.index.tolist()}"
        )

    # Check that every from segment:lane has at least one matching to
    # segment:lane and vice versa. If a from segment has zero matching
    # to segments, or a to segment has zero from segments, it is
    # considered to be a terminal node and will not trigger a validation
    # error.
    segs_with_from = df_con_val['from_segment_fid'].unique()
    segs_with_to = df_con_val['to_segment_fid'].unique()
    from_check = df_con_val[df_con_val['from_segment_fid'].isin(segs_with_to)]
    from_check = from_check[['from_segment_fid', 'from_lane_number']]
    to_check = df_con_val[df_con_val['to_segment_fid'].isin(segs_with_from)]
    to_check = to_check[['to_segment_fid', 'to_lane_number']]
    from_comp = df_con_val.set_index(['from_segment_fid', 'from_lane_number'])
    from_comp['exists'] = True
    to_comp = df_con_val.set_index(['to_segment_fid', 'to_lane_number'])
    to_comp['exists'] = True
    from_join = from_check.join(to_comp['exists'],
        on=['from_segment_fid', 'from_lane_number'], how='left',
    )
    to_join = to_check.join(from_comp['exists'],
        on=['to_segment_fid', 'to_lane_number'], how='left',
    )
    from_fail = from_join[from_join['exists'].isna()]
    to_fail = to_join[to_join['exists'].isna()]
    if len(from_fail) > 0:
        raise ValueError(
            "Missing matching 'to' lanes at 'from' connector fid(s) " +
            str(from_fail.index.tolist())
        )
    if len(to_fail) > 0:
        raise ValueError(
            "Missing matching 'from' lanes at 'to' connector fid(s) " +
            str(to_fail.index.tolist())
        )

def format_node(node: Node):
    """Formats a Node as a string."""
    return f"{node[0]}:{node[1]}"


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
        type=int,
    )
    parser.add_argument('--output',
        help="Output path(s) (supports .graphml)",
        nargs='+',
        type=Path,
        default=[],
    )
    parser.add_argument('--paint',
        help="Allow paint line crossings for lanes starting or ending",
        action='store_true',
        default=False,
    )
    args = parser.parse_args()
    follow_lane(args.source, args.start, args.output, args.paint)
