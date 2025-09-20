"""Follows a road lane through GeoPackage data."""

from pathlib import Path
from typing import List, Tuple
import argparse
import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt
from build_graph import build_graph


Node = Tuple[int, int]

def follow_lane(source: Path, start_fid: int, start_lane: int) -> None:
    """Follows a lane starting with the provided fid and lane number."""
    g = build_graph(source)
    start = (start_fid, start_lane)
    lanes_forward: List[Node] = sorted(nx.descendants(g, start))
    fids_forward: List[int] = [l[0] for l in lanes_forward]
    lanes_backward: List[Node] = sorted(nx.ancestors(g, start))
    fids_backward: List[int] = [l[0] for l in lanes_backward]

    fig, ax = plt.subplots(1, 1)

    gdf = gpd.read_file(source, layer='road_segments')
    print(gdf.crs)
    gdf_start = gdf[gdf.index.isin([start_fid])]
    gdf_forward = gdf[gdf.index.isin(fids_forward)]
    gdf_backward = gdf[gdf.index.isin(fids_backward)]
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
