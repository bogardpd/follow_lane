"""Creates a LineString of a given lane from a starting way."""

import argparse
import requests

OVERPASS_API_URL = "https://overpass-api.de/api/interpreter"
OVERPASS_TIMEOUT = 15

def follow_lane(way_id: int) -> None:
    """Follows a lane starting with the provided way."""
    way = fetch_osm_way(way_id)

    print(way)

def fetch_osm_way(way_id: int) -> dict:
    """Fetches a way from OSM via the Overpass API."""
    if way_id is None:
        return ValueError("Way id may not be None.")

    query = f"""
    [out:json];
    way({way_id});
    out body;
    node(w);
    out body;
    """

    response = requests.post(
        OVERPASS_API_URL,
        data={'data': query},
        timeout=OVERPASS_TIMEOUT
    )
    response.raise_for_status()
    data = response.json()
    elements = data['elements']

    return elements


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Follow Lane",
        description="Follows a road lane using OSM data"
    )
    parser.add_argument('--way', type=int, required=True)
    args = parser.parse_args()

    follow_lane(args.way)
