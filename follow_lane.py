"""Creates a LineString of a given lane from a starting way."""

from pathlib import Path
import argparse
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from lxml import etree
from shapely.geometry import LineString


def follow_lane(pbf_path: Path, way_id: int) -> None:
    """Follows a lane starting with the provided way."""
    way = get_way_by_id(pbf_path, way_id)

    print(way)

def get_way_by_id(pbf_path: Path, way_id: int) -> dict:
    """Fetches a way from OSM data."""
    if way_id is None:
        return ValueError("Way id may not be None.")

    with tempfile.TemporaryDirectory() as tmpdir:
        way_file = Path(tmpdir) / "way.osm"
        nodes_file = Path(tmpdir) / "nodes.osm"
        merged_file = Path(tmpdir) / "combined.osm"
        output_file = Path(tmpdir) / "located_way.osm"

        # Find way by ID.
        print(f"Finding way {way_id}...")
        subprocess.run([
            "osmium", "getid", str(pbf_path), f"w{way_id}",
            "-o", way_file, "--overwrite",
        ], check=True)

        # Parse node refs from the way.
        with open(way_file, "rb") as f:
            tree = etree.parse(f)
            root = tree.getroot()
            node_refs = [nd.attrib['ref'] for nd in root.findall(".//way/nd")]
        if not node_refs:
            raise RuntimeError("No node references found in way.")

        # Get node elements.
        node_args = [f"n{nid}" for nid in node_refs]
        print(f"Finding nodes for way {way_id}...")
        subprocess.run([
            "osmium", "getid", str(pbf_path), *node_args,
            "-o", nodes_file, "--overwrite",
        ], check=True)

        # Merge node and way files.
        print(f"Merging way {way_id} and its nodes...")
        subprocess.run([
            "osmium", "merge", str(nodes_file), str(way_file),
            "-o", str(merged_file)
        ], check=True)

        # Add locations to way.
        print(f"Adding locations to way {way_id}...")
        subprocess.run([
            "osmium", "add-locations-to-ways", str(merged_file),
            "-o", str(output_file),
        ], check=True)

        # Parse the output file.
        tree = ET.parse(output_file)
        root = tree.getroot()
        tags = {}
        geometry = None

        for way in root.findall('way'):
            if way.attrib['id'] != str(way_id):
                continue
            tags = {
                tag.attrib['k']: tag.attrib['v']
                for tag in way.findall('tag')
            }
            nodes = {}
            for nd in way.findall("nd"):
                node_id = nd.attrib['ref']
                lat = float(nd.attrib['lat'])
                lon = float(nd.attrib['lon'])
                nodes[node_id] = (lon, lat)
            geometry = LineString(nodes.values())
            break

        return {'tags': tags, 'geometry': geometry}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Follow Lane",
        description="Follows a road lane using OSM data"
    )
    parser.add_argument('--pbf',
        help="Preprocessed OSM PBF file path",
        type=Path,
        required=True,
    )
    parser.add_argument('--way',
        help="OSM way id to start from",
        type=int,
        required=True,
    )
    args = parser.parse_args()

    follow_lane(args.pbf, args.way)
