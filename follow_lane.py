"""Creates a LineString of a given lane from a starting way."""

from pathlib import Path
import argparse
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from shapely.geometry import LineString

OVERPASS_API_URL = "https://overpass-api.de/api/interpreter"
OVERPASS_TIMEOUT = 15

class Way:
    """Finds a way from an id"""
    def __init__(self, way_id, pbf_path):
        """Initialize WayExtractor"""
        super().__init__()
        self.way_id = str(way_id)
        self.pbf_path = pbf_path
        self.tags = {}
        self.geometry = None

        if not shutil.which("osmium"):
            raise RuntimeError(
                "The 'osmium' CLI tool is not installed or not in PATH."
            )

    def extract(self):
        """Parse data for the Way"""
        with tempfile.NamedTemporaryFile(suffix=".osm", delete=False) as t:
            tmp_osm_path = t.name

        # Run osmium getid to extract the way.
        try:
            result = subprocess.run([
                "osmium", "getid", str(self.pbf_path), f"w{self.way_id}",
                "-f", "osm",
                "-o", tmp_osm_path, "--overwrite"
            ], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print("Osmium exited with error code", e.returncode)
            print("stdout:", e.stdout)
            print("stderr:", e.stderr)


        # Parse the .osm file.
        tree = ET.parse(tmp_osm_path)
        root = tree.getroot()

        # Collect node positions.
        node_coords = {}
        for node in root.findall('node'):
            node_id = node.attrib['id']
            lat = float(node.attrib['lat'])
            lon = float(node.attrib['lon'])
            node_coords[node_id] = (lon, lat)

        # Find the way.
        for way in root.findall('way'):
            if way.attrib['id'] != self.way_id:
                continue

            # Extract tags.
            self.tags = {
                tag.attrib['k']: tag.attrib['v']
                for tag in way.findall('tag')
            }

            # Build geometry.
            coords = []
            for nd in way.findall("nd"):
                ref = nd.attrib['ref']
                if ref in node_coords:
                    coords.append(node_coords[ref])
                else:
                    raise ValueError(
                        f"Node {ref} not found in extracted data."
                    )
            self.geometry = LineString(coords)
            break

        if self.geometry is None:
            raise ValueError(f"Way {self.way_id} not found in file.")


def follow_lane(pbf_path: Path, way_id: int) -> None:
    """Follows a lane starting with the provided way."""
    way = get_way_by_id(pbf_path, way_id)

    print(way.tags)
    print(way.geometry)

def get_way_by_id(pbf_path: Path, way_id: int) -> Way:
    """Fetches a way from OSM via the Overpass API."""
    if way_id is None:
        return ValueError("Way id may not be None.")

    way = Way(way_id, pbf_path)
    way.extract()

    return way


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
