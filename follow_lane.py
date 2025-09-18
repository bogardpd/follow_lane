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

    gdf = gpd.read_file(source, layer='road_segments')
    gdf_forward = gdf[gdf.index.isin(fids_forward)]
    gdf_forward.plot()
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
